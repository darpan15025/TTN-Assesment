#!/usr/bin/env python3
"""Generate a Ring Ceremony invitation video with animation in a single frame."""

from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy import AudioFileClip, VideoClip

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
INVITATION_IMAGE = ASSETS / "invitation_source.jpg"
OUTPUT_DIR = ROOT / "output"
OUTPUT_VIDEO = OUTPUT_DIR / "ring_ceremony_invitation.mp4"
OUTPUT_MOBILE = OUTPUT_DIR / "ring_ceremony_invitation_mobile.mp4"
BG_MUSIC = ASSETS / "bg_music.wav"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 20.0

GOLD = (212, 175, 55)
GOLD_PALE = (245, 228, 170)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def fit_cover(image: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = image.size
    scale = max(width / src_w, height / src_h)
    new_size = (int(src_w * scale), int(src_h * scale))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    left = (new_size[0] - width) // 2
    top = (new_size[1] - height) // 2
    return resized.crop((left, top, left + width, top + height))


def build_sparkles(count: int, seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    sparkles = []
    for _ in range(count):
        sparkles.append(
            {
                "x": rng.uniform(0.08, 0.92),
                "y": rng.uniform(0.05, 0.95),
                "size": rng.uniform(1.5, 4.5),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.8, 2.2),
                "drift": rng.uniform(0.004, 0.015),
            }
        )
    return sparkles


SPARKLES = build_sparkles(48)
BASE_FRAME = fit_cover(Image.open(INVITATION_IMAGE).convert("RGB"), WIDTH, HEIGHT)


def render_single_frame(t: float) -> np.ndarray:
    progress = clamp01(t / DURATION)

    zoom = 1.0 + 0.045 * ease_in_out_sine(progress)
    pan_x = math.sin(progress * math.pi * 2) * 8
    pan_y = math.cos(progress * math.pi * 1.5) * 6

    w, h = BASE_FRAME.size
    crop_w = int(WIDTH / zoom)
    crop_h = int(HEIGHT / zoom)
    left = int((w - crop_w) / 2 + pan_x)
    top = int((h - crop_h) / 2 + pan_y)
    left = max(0, min(w - crop_w, left))
    top = max(0, min(h - crop_h, top))

    frame = BASE_FRAME.crop((left, top, left + crop_w, top + crop_h)).resize(
        (WIDTH, HEIGHT), Image.Resampling.LANCZOS
    )

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    shimmer_x = int((progress * 1.4) % 1.0 * (WIDTH + 400)) - 200
    shimmer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shimmer_draw = ImageDraw.Draw(shimmer)
    for offset in range(-80, 120, 18):
        alpha = int(18 + 12 * math.sin(progress * math.pi * 4))
        shimmer_draw.polygon(
            [
                (shimmer_x + offset, 0),
                (shimmer_x + offset + 50, 0),
                (shimmer_x + offset + 180, HEIGHT),
                (shimmer_x + offset + 90, HEIGHT),
            ],
            fill=(*GOLD_PALE, alpha),
        )
    shimmer = shimmer.filter(ImageFilter.GaussianBlur(radius=18))
    overlay = Image.alpha_composite(overlay, shimmer)

    glow_alpha = int(22 + 18 * math.sin(progress * math.pi * 3))
    draw.ellipse((WIDTH // 2 - 280, 120, WIDTH // 2 + 280, 520), fill=(*GOLD, glow_alpha))

    ring_pulse = 0.5 + 0.5 * math.sin(progress * math.pi * 2.5)
    ring_alpha = int(40 + 80 * ring_pulse)
    cx, cy = WIDTH // 2 + 40, int(HEIGHT * 0.78)
    draw.ellipse((cx - 52, cy - 52, cx - 2, cy - 2), outline=(*GOLD, ring_alpha), width=3)
    draw.ellipse((cx - 12, cy - 62, cx + 38, cy - 12), outline=(*GOLD_PALE, ring_alpha), width=3)

    for sparkle in SPARKLES:
        twinkle = 0.35 + 0.65 * abs(math.sin(t * sparkle["speed"] + sparkle["phase"]))
        alpha = int(180 * twinkle * ease_out_cubic(min(1.0, progress * 2)))
        if alpha < 8:
            continue
        x = int(sparkle["x"] * WIDTH + math.sin(t + sparkle["phase"]) * 12)
        y = int(sparkle["y"] * HEIGHT - t * sparkle["drift"] * HEIGHT) % HEIGHT
        size = sparkle["size"] * (0.8 + 0.4 * twinkle)
        draw.ellipse((x, y, x + size, y + size), fill=(*GOLD_PALE, alpha))

    vignette_strength = int(28 + 10 * math.sin(progress * math.pi))
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(35, 8, 18, vignette_strength))

    frame_rgba = frame.convert("RGBA")
    frame_rgba = Image.alpha_composite(frame_rgba, overlay)
    return np.array(frame_rgba.convert("RGB"))


def generate_background_music() -> None:
    if BG_MUSIC.exists():
        return
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=220:duration={int(DURATION) + 2}",
        "-af",
        f"volume=0.06,afade=t=in:st=0:d=2,afade=t=out:st={int(DURATION)-2}:d=2",
        str(BG_MUSIC),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def compress_mobile(source: Path, target: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vf",
        "scale=720:1280:flags=lanczos",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "28",
        "-maxrate",
        "2500k",
        "-bufsize",
        "5000k",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-movflags",
        "+faststart",
        str(target),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_video() -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generate_background_music()

    def frame_at(t: float) -> np.ndarray:
        return render_single_frame(t)

    video = VideoClip(frame_at, duration=DURATION).with_fps(FPS)
    audio = AudioFileClip(str(BG_MUSIC)).with_duration(DURATION)
    video = video.with_audio(audio)

    video.write_videofile(
        str(OUTPUT_VIDEO),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="5000k",
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger=None,
    )
    video.close()
    audio.close()

    compress_mobile(OUTPUT_VIDEO, OUTPUT_MOBILE)
    return OUTPUT_VIDEO, OUTPUT_MOBILE


if __name__ == "__main__":
    hq, mobile = build_video()
    print(f"Created: {hq}")
    print(f"Created: {mobile}")
