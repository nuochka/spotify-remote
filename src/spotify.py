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

""" Subset of lambda function with spotify class as an argument """
SpotifyPerformer = Callable[[Spotify], None]

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
        Performs a spotify web API action with additional error handling.
    """
    def perform(self, f: SpotifyPerformer):
        self.current = self.sp.current_playback()

        try:
            f_src = inspect.getsource(f).strip()
            if self.current:
                AppLogger.info("Current track: {}, playing: {}", self.current['item']['name'], self.current['is_playing'])
            else:
                AppLogger.error("Unable to retrieve currently selected track.")
        except Exception:
            f_src = f.__str__

        try:
            AppLogger.info(f'Performing Spotify API action: {f_src}')
            f(self.sp)
        except SpotifyException as e:
            AppLogger.error(f'Spotify API error has occured: {e}.')

            match e.http_status:
                case 403:
                    if "PREMIUM_REQUIRED" in e.msg:
                        AppLogger.error("Premium only feature used on non-premium account. Ignoring...")
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

# Basic predefined lambdas
SPOTIFY_NEXT_TRACK: SpotifyPerformer    = lambda sp: sp.next_track()
SPOTIFY_PREV_TRACK: SpotifyPerformer    = lambda sp: sp.previous_track()
SPOTIFY_PAUSE_TRACK: SpotifyPerformer   = lambda sp: sp.pause_playback()
SPOTIFY_RESUME_TRACK: SpotifyPerformer  = lambda sp: sp.start_playback()
