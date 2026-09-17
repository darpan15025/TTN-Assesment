# Ring Ceremony Invitation Video

Generates a cinematic **1080×1920** (portrait) invitation video for the Ring Ceremony of **Tanya Goel** and **Prabhat Goel**.

The video keeps all invitation details in a **single view**, with **Ring Ceremony**, **of**, and **Tanya Goel & Prabhat Goel** displayed together prominently on one screen, surrounded by a rich animated maroon and gold backdrop.

## Event Details

| | |
|---|---|
| **Date** | Saturday, 24 October |
| **Time** | 11:00 AM |
| **Venue** | The Tonight Rooms and Party Hall, Railway Road, Hapur |

## Output

The generated video is saved to:

```
output/ring_ceremony_invitation.mp4          # High quality (~39 MB)
output/ring_ceremony_invitation_mobile.mp4   # Mobile-optimized (~1.3 MB)
```

To create a smaller mobile-friendly version from the high-quality export:

```bash
ffmpeg -i output/ring_ceremony_invitation.mp4 \
  -vf "scale=720:1280:flags=lanczos" \
  -c:v libx264 -preset slow -crf 28 -maxrate 2500k -bufsize 5000k \
  -c:a aac -b:a 96k -movflags +faststart \
  output/ring_ceremony_invitation_mobile.mp4
```

## Requirements

- Python 3.10+
- FFmpeg (system)

## Setup

```bash
pip install -r requirements.txt
```

## Generate Video

```bash
python generate_invitation_video.py
```

Generation takes about 1–2 minutes. The script animates the invitation card in one frame with Ken Burns motion, golden shimmer, sparkles, and ambient audio.

## Project Structure

```
assets/
  fonts/                  # Cinzel, Cormorant Garamond, Great Vibes
  invitation_source.jpg   # Original invitation artwork
  bg_music.wav            # Generated ambient background tone
generate_invitation_video.py
output/
  ring_ceremony_invitation.mp4
```
