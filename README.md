# Ring Ceremony Invitation Video

Generates a cinematic **1080×1920** (portrait) invitation video for the Ring Ceremony of **Tanya Goel** and **Prabhat Goel**.

## Event Details

| | |
|---|---|
| **Date** | Saturday, 24 October |
| **Time** | 11:00 AM |
| **Venue** | The Tonight Rooms and Party Hall, Railway Road, Hapur |

## Output

The generated video is saved to:

```
output/ring_ceremony_invitation.mp4
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

Generation takes about 2–3 minutes. The script renders six animated scenes with maroon/gold/cream styling, elegant typography, subtle ambient audio, and a final reveal of the original invitation artwork.

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
