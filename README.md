# 🎵 Spotify Remote via Gestures 👋

This project allows you to control Spotify playback using hand gestures via a webcam, while running as a daemon service on background. It uses computer vision and the Spotify Web API to create a hands-free, intuitive experience.

---

## Overview

This application utilizes your webcam to detect hand gestures, which map to Spotify commands like play/pause, next/previous track, and volume control. Ideal for hands-free control or accessibility.

---

### Prerequisites

- Spotify account with Premium!!!
- Spotify Developer API credentials (Client ID and Secret)
- Python 3.10 or higher
- Functional webcam

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/nuochka/spotify-remote.git
   cd spotify-remote
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create and configure the `.env` file:**

   Create a file named `.env` in the root directory with the following contents. See the example below or change `.env_template` file for a quick start:

   ```env
   # Spotify API Client ID. Must be supplied!
   SPOTIPY_CLIENT_ID="your_spotify_client_id"

   # Spotify API Client Secret. Must be supplied!
   SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"

   # This project does not use redirection features.
   SPOTIPY_REDIRECT_URI="http://127.0.0.1:8888/callback"

   # Timeout (in seconds) between camera retry attempts if unavailable.
   SPOTIFY_REMOTE_CAMERA_TIMEOUT="5"

   # Enable or disable debug mode (tracking markers and logs).
   SPOTIFY_REMOTE_DEBUG_MODE="True"
   ```

   Replace `your_spotify_client_id` and `your_spotify_client_secret` with your actual credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

---

## 🏁 Running the Application

Spotify gesture controller was meant to be used as a daemon utility running on background. It can also be started as a simple python script:

```bash
python main.py
```

The app will access your webcam and begin detecting hand gestures to control Spotify. All logs will be written to `spotify-remote.log` generated after the start of the daemon. Application also logs to standard output when started in shell.

---

## ⚙️ Environment Variables

| Variable                          | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| `SPOTIPY_CLIENT_ID`              | Your Spotify app's client ID (required).                                   |
| `SPOTIPY_CLIENT_SECRET`          | Your Spotify app's client secret (required).                               |
| `SPOTIPY_REDIRECT_URI`           | Redirect URI, not actively used but required by Spotipy (keep default).    |
| `SPOTIFY_REMOTE_CAMERA_TIMEOUT`  | Timeout in seconds before retrying webcam access.                          |
| `SPOTIFY_REMOTE_DEBUG_MODE`      | Set to `"True"` to show tracking markers and logs, `"False"` to disable.   |

---

## ✋ Supported Gestures

The following gestures are supported (gesture detection may vary based on lighting and camera quality):

| Gesture Name     | Action            | Description (approximate)                                                              |
|------------------|-------------------|-----------------------------------------------------------------------------------------|
| Open Palm        | Play / Pause      | Hold your open hand up, palm facing the camera.                                        |
| Thumb Left       | Previous Track    | Point your thumb clearly to the left with a closed fist.                               |
| Thumb Right      | Next Track        | Point your thumb clearly to the right with a closed fist.                              |
| Pinch Gesture    | Volume Control    | Pinch your thumb and pinky together—volume is adjusted based on the distance between the tips of these two fingers. The farther apart the fingers, the higher the volume.


> 🧪 You can enable `SPOTIFY_REMOTE_DEBUG_MODE` to help visualize gesture tracking and calibrate movements.

---

## 🐞 Debug Mode

When `SPOTIFY_REMOTE_DEBUG_MODE` is set to `"True"`, an additional window will appear displaying real-time gesture tracking markers and verbose logging. This is useful for testing but may slightly degrade performance.

---

For more information on setting up Spotify Developer credentials, visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

