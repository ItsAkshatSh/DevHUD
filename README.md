# NerdHUD - Cross-Platform Developer's Heads-Up Display

A lightweight, cross-platform desktop application that displays system information and productivity tools on your desktop wallpaper, similar to Rainmeter.

## Features

- Desktop Integration: Displays on wallpaper without interfering with normal window usage
- System Stats: Real-time CPU, RAM, GPU monitoring
- Clipboard History: Track and manage recent clipboard entries
- Focus Timer: Pomodoro-style productivity timer
- Custom Keybinds: System-wide keyboard shortcuts
- Modern UI: Cyber-themed interface with neon accents
- Cross-Platform: Works on Windows, macOS, and Linux

## Installation

1. Ensure you have Python 3.8+ installed
2. Clone this repository
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

## Configuration

The application can be configured through the settings interface. Configuration files are stored in:
- Windows: `%APPDATA%/NerdHUD/`
- macOS: `~/Library/Application Support/NerdHUD/`
- Linux: `~/.config/NerdHUD/`

## Development

This project uses PyQt5 for the UI framework and follows a modular architecture for easy extension.

## License

MIT License 