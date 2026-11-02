# Ethereal Audio Studio — Responsive UI upgrade

This package refreshes the ClearSound Studio interface with an ethereal visual style: airy gradients, soft lavender and blue accents, glass-like panels, rounded controls, and responsive CSS for desktop and mobile browsers.

## Features retained
- Extract audio from videos
- Optional background-noise reduction
- Original and cleaned audio previews
- MP3, WAV, M4A/AAC, AAC, and FLAC exports
- MP3/AAC bitrate settings
- FFmpeg-based conversion

## Install into the existing project
1. Back up your current project folder.
2. Extract this ZIP.
3. Copy `app.py` and `requirements.txt` into your existing `video_audio_cleaner` folder and replace the existing files.
4. Keep the existing `.venv` folder.

Open Command Prompt and run:

```bat
cd "C:\Users\parmar Aryan\OneDrive\Desktop\video_audio_cleaner_starter\video_audio_cleaner"
..\.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If your folder path differs, use your actual path in the `cd` command.

## Responsive testing
- Desktop: open the local Streamlit URL in Chrome or Edge.
- Mobile: use Chrome DevTools device toolbar to preview a phone layout, or open the app from a phone on the same Wi-Fi using the computer's local network IP and `streamlit run app.py --server.address 0.0.0.0`. Only do this on a trusted network.
- The CSS adjusts spacing, hero type, controls, and padding for screens under 768px and 420px.

## Important
Noise reduction quality depends on the recording. Higher strength can create watery or robotic artifacts. This is a Streamlit web interface, not a standalone EXE.
