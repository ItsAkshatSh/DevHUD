import win32gui
import win32process
import psutil
from pycaw.pycaw import AudioUtilities

def get_visible_windows():
    windows = []
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    pname = proc.name()
                except Exception:
                    pname = 'UNKNOWN'
                windows.append((hwnd, pname, title))
    win32gui.EnumWindows(enum_handler, None)
    return windows

def get_active_audio_processes():
    sessions = AudioUtilities.GetAllSessions()
    active_process_names = set()
    for session in sessions:
        if session.Process and session.SimpleAudioVolume.GetMute() == 0 and session.SimpleAudioVolume.GetMasterVolume() > 0:
            try:
                # Check for active audio peak value
                meter = session._ctl.QueryInterface(session._IAudioMeterInformation)
                if meter.GetPeakValue() > 0.01: # Threshold for active audio
                    active_process_names.add(session.Process.name())
            except Exception:
                continue
    return active_process_names

def get_playing_media_info():
    windows = get_visible_windows()
    active_audio_processes = get_active_audio_processes()

    for hwnd, pname, title in windows:
        is_current_audio_active = pname in active_audio_processes

        if pname.lower() == 'spotify.exe' and title.strip():
            # Spotify app format: "Artist - Song Title [ - Version/Remix/Album ]"
            # Example: "MXZI - MONTAGEM TOMADA - Slowed"
            if ' - ' in title:
                parts = title.split(' - ', 1) # Split only on the first ' - '
                if len(parts) == 2:
                    artist_name = parts[0].strip()
                    song_title = parts[1].strip()
                    return song_title, artist_name, is_current_audio_active
            return title, '', is_current_audio_active # If no ' - ' or unexpected format, return full title as song
        
        # For browsers, require active audio from pycaw for it to be considered 'playing media'
        elif is_current_audio_active: # Only consider if the browser is actually making sound
            if 'YouTube' in title or 'Chrome' in title or 'Edge' in title or 'Firefox' in title:
                # For browsers, return the full title as song, no separate artist
                return title, '', True # is_audio_active is True here by definition

    return None, None, False # No active media found

def get_spotify_song_info():
    return get_playing_media_info()

def send_spotify_control(action):
    import pyautogui
    pyautogui.press({
        'play_pause': 'playpause',
        'next': 'nexttrack',
        'prev': 'prevtrack',
    }.get(action, 'playpause')) 