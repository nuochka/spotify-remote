""" 
    File: spotify.py
    Desc: Bindings to spotify API for handling currently played songs. All spotify tokens, secrets must be
    provided via environment variables.
"""

import os
import time
import inspect

# ruff: noqa: E731

from log import AppLogger
from spotipy import SpotifyOAuth, Spotify
from spotipy.exceptions import SpotifyException
from typing import Callable
from threading import Thread

class SpotifyHandler:
    CLIENT_ID       = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET   = os.getenv("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI    = os.getenv("SPOTIPY_REDIRECT_URI")
    SCOPE           = "user-modify-playback-state user-read-playback-state streaming"
    CACHE_PATH      = ".spotify_token_cache"

    """ 
        Creates a new instance of 'SpotifyHandler' while also initializing the token refreshing daemon 
        in the background, which will only be active once per hour.
    """
    def __init__(self) -> None:
        self.new()

        # Starting the token refresher daemon.
        Thread(
            target=self.token_refreshd,
            daemon=True, 
        ).start()

        user = self.sp.current_user()
        if user:
            AppLogger.info(f"Initialized spotify handler for {user['display_name']}")

    def new(self) -> None:
        self.oauth = SpotifyOAuth(
            client_id = self.CLIENT_ID,
            client_secret = self.CLIENT_SECRET,
            redirect_uri = self.REDIRECT_URI,
            scope=self.SCOPE,
            cache_path=self.CACHE_PATH,
        )
        self.sp = Spotify(auth_manager=self.oauth)
        self.current = self.sp.current_playback()
        self.playback_fallback_dev = None

    """ 
        Token refresh daemon thread. Will be run at background when new instance of 'SpotifyHandler' is
        created.
    """
    def token_refreshd(self) -> None:
        AppLogger.info("Starting token refresh daemon.")

        while True:
            time.sleep(3600) # Spotify API token is valid for one hour.
            AppLogger.debug("Token refreshing daemon is online.")
            token_info = self.oauth.cache_handler.get_cached_token()

            if token_info is None:
                AppLogger.warning(f'Failed to obtain token data from {self.CACHE_PATH}. Obtaining new token...')
                self.new()

            if self.oauth.is_token_expired(token_info):
                AppLogger.info("Refreshing spotify token.")
                self.oauth.refresh_access_token(token_info)

    """ 
        Used when spotify cannot find any active device to manually probe the required one.

        This problem usually occurs with web players. Even if spotify application is opened but playback never started
        from the first startup, daemon with just API actions may not be able to start the playback for the first time.
        Device is therefore can be probed or, in worst case scenario, one shall start the first song playback manually.
    """
    def probe_device(self) -> bool:
        devs = self.sp.devices()

        if devs and devs["devices"]:
            dev = devs["devices"][0].get("id")

            if dev:
                self.playback_fallback_dev = dev
            else:
                return False
        else:
            return False

        return True

    """
        Performs a spotify web API action with additional error handling.
    """
    def perform(self, f) -> None:
        try:
            f_src = inspect.getsource(f).strip()
            if self.current:
                AppLogger.info("Current track: {}, playing: {}", self.current['item']['name'], self.current['is_playing'])
            else:
                AppLogger.error("Unable to retrieve currently selected track.")
        except Exception:
            f_src = f.__str__

        self.current = self.sp.current_playback()
        try:
            AppLogger.info(f'Performing Spotify API action: {f_src}')
            f(self)
        except SpotifyException as e:
            AppLogger.error(f'Spotify API error has occured: {e}.')

            match e.http_status:
                case 403:
                    if "PREMIUM_REQUIRED" in e.msg: # No features from this daemon can be accessed without premium.
                        AppLogger.error("Premium only feature used on non-premium account. Ignoring...")
                    elif "RESTRICTION VIOLATED":    # Sending PLAY request when already playing or vice versa.
                        AppLogger.warning("Wrong command sent to spotify player API.")
                case 404:                           # No active device bug.
                    AppLogger.error("Spotify could not find proper active device. Enquiring...")
                    if not self.probe_device():
                        AppLogger.error("Unable to probe any active playback device. Spotify application is either not active or it is a web API bug.")
                case 429:   # Rate limit.
                    retry_after = e.headers["retry-after"]
                    AppLogger.error("Spotify API rate limit exceeded, retrying after {}s.")
            
                    # Retry in 'retry_after' seconds in a different thread.
                    Thread(
                        target=lambda _: time.sleep(retry_after) or self.perform(f) 
                    ).start()
                case _:     # Unhandled
                    AppLogger.error("Unhandled error. Ignoring...")
        except Exception as e:
            AppLogger.error(f'Unknown API error has occured: {e}. Unable to perform the task.')

""" Subset of lambda function with spotify class as an argument """
SpotifyPerformer = Callable[[SpotifyHandler], None]

# Basic predefined lambdas
SPOTIFY_NEXT_TRACK: SpotifyPerformer    = lambda h: h.sp.next_track(h.playback_fallback_dev)
SPOTIFY_PREV_TRACK: SpotifyPerformer    = lambda h: h.sp.previous_track(h.playback_fallback_dev)
SPOTIFY_PAUSE_TRACK: SpotifyPerformer   = lambda h: h.sp.pause_playback(h.playback_fallback_dev)
SPOTIFY_RESUME_TRACK: SpotifyPerformer  = lambda h: h.sp.start_playback(h.playback_fallback_dev)
