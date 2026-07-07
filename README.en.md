# EagleConvter

**English** | [中文](./README.md)

A media format conversion desktop tool powered by FFmpeg + PySide6.

![Screenshot](./dash.png)

## Features

- **Drag & Drop** — Drag or browse to add media files, auto-displays codec/resolution/duration
- **18 Presets** — One-click selection for MP4/AVI/MKV/WEBM/MOV/GIF/3GP/MPEG/OGV and audio formats
- **Fine Control** — Resolution / FPS / Video codec / Audio codec / CRF quality / Audio bitrate
- **Batch Queue** — Serial queue processes files one by one
- **Live Progress** — Progress bar + FPS + Speed + ETA + Elapsed time
- **Context Menu** — Right-click any task to "Save As" or "Open output folder"
- **Dark Theme** — Catppuccin Mocha dark style
- **Audio Extraction** — Extract audio to MP3/FLAC/WAV/AAC/Opus from video

## Presets

| Preset | Format | Video Codec | Audio Codec |
|--------|--------|-------------|-------------|
| MP4 H.264 | .mp4 | libx264 | aac |
| MP4 H.265 | .mp4 | libx265 | aac |
| AVI | .avi | mpeg4 | mp3 |
| MKV H.265 | .mkv | libx265 | aac |
| WEBM VP9 | .webm | libvpx-vp9 | libopus |
| WEBM VP8 | .webm | libvpx | libvorbis |
| MOV | .mov | libx264 | aac |
| GIF | .gif | gif | — |
| iPhone | .mp4 | libx264 | aac |
| Telegram | .mp4 | libx264 | aac |
| 3GP H.263 | .3gp | h263 | aac |
| MPEG-2 | .mpg | mpeg2video | mp2 |
| OGV Theora | .ogv | libtheora | libvorbis |
| MP3 Audio | .mp3 | copy | libmp3lame |
| FLAC Audio | .flac | copy | flac |
| WAV PCM | .wav | copy | pcm_s16le |
| AAC Audio | .m4a | copy | aac |
| OPUS Audio | .ogg | copy | libopus |

## Requirements

- Windows 10/11
- [FFmpeg](https://ffmpeg.org/) installed and added to PATH

## Development

```bash
# Clone
git clone https://github.com/yourname/EagleConvter.git
cd EagleConvter

# Install dependencies
pip install -r requirements.txt

# Run
python main.py

# Package
pyinstaller --onedir --windowed --name EagleConvter --icon resources/app.ico --add-data "resources/styles.qss;resources" --add-data "resources/app.png;resources" main.py
```

## Project Structure

```
convter/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── core/
│   ├── formats.py          # Presets / codecs / resolutions
│   ├── ffmpeg.py           # FFmpeg subprocess + progress parser
│   └── task.py             # Task queue + background thread
├── ui/
│   ├── main_window.py      # Main window
│   ├── file_panel.py       # File list + drag & drop
│   ├── format_panel.py     # Parameter selection
│   └── progress_panel.py   # Progress display
└── resources/
    ├── styles.qss          # Dark theme stylesheet
    ├── app.png             # App icon
    └── app.ico             # Windows icon
```
