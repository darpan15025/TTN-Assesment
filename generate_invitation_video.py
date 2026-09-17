#!/usr/bin/env python3
"""Generate a rich single-frame Ring Ceremony invitation video."""

from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy import AudioFileClip, VideoClip

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
INVITATION_IMAGE = ASSETS / "invitation_source.jpg"
OUTPUT_DIR = ROOT / "output"
OUTPUT_VIDEO = OUTPUT_DIR / "ring_ceremony_invitation.mp4"
OUTPUT_MOBILE = OUTPUT_DIR / "ring_ceremony_invitation_mobile.mp4"
BG_MUSIC = ASSETS / "bg_music.wav"

WIDTH, HEIGHT = 1080, 1920
FPS = 24
DURATION = 20.0

MAROON = (92, 18, 38)
MAROON_LIGHT = (123, 30, 58)
GOLD = (212, 175, 55)
GOLD_LIGHT = (245, 215, 120)
GOLD_PALE = (255, 236, 190)
ROSE = (170, 28, 52)
ROSE_PALE = (220, 120, 130)
CREAM = (245, 232, 210)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def fit_contain(image: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = image.size
    scale = min(width / src_w, height / src_h)
    new_size = (int(src_w * scale), int(src_h * scale))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.paste(resized, ((width - new_size[0]) // 2, (height - new_size[1]) // 2))
    return canvas


def build_particles(seed: int = 11) -> tuple[list[dict], list[dict], list[dict]]:
    rng = random.Random(seed)
    petals, bokeh, sparkles = [], [], []
    for _ in range(36):
        petals.append(
            {
                "x": rng.uniform(0.0, 1.0),
                "y": rng.uniform(-0.2, 1.1),
                "size": rng.uniform(8, 18),
                "speed": rng.uniform(0.02, 0.06),
                "sway": rng.uniform(0.5, 1.5),
                "phase": rng.uniform(0, math.tau),
                "color": rng.choice([ROSE, ROSE_PALE, GOLD_PALE, CREAM, (255, 210, 210)]),
            }
        )
    for _ in range(22):
        bokeh.append(
            {
                "x": rng.uniform(0.03, 0.97),
                "y": rng.uniform(0.03, 0.97),
                "radius": rng.uniform(16, 52),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.6, 1.4),
            }
        )
    for _ in range(90):
        sparkles.append(
            {
                "x": rng.uniform(0.0, 1.0),
                "y": rng.uniform(0.0, 1.0),
                "size": rng.uniform(2, 5),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(1.0, 3.0),
            }
        )
    return petals, bokeh, sparkles


def create_static_backdrop() -> Image.Image:
    gradient = Image.new("RGB", (WIDTH, HEIGHT), MAROON)
    draw = ImageDraw.Draw(gradient)
    for y in range(0, HEIGHT, 2):
        blend = y / HEIGHT
        r = int(lerp(MAROON[0], MAROON_LIGHT[0], blend * 0.55))
        g = int(lerp(MAROON[1], MAROON_LIGHT[1], blend * 0.55))
        b = int(lerp(MAROON[2], MAROON_LIGHT[2], blend * 0.55))
        draw.rectangle((0, y, WIDTH, y + 2), fill=(r, g, b))

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    tile = 80
    for y in range(0, HEIGHT, tile):
        for x in range(0, WIDTH, tile):
            cx, cy = x + tile // 2, y + tile // 2
            draw.pieslice((cx - 24, cy - 24, cx + 24, cy + 24), 210, 330, fill=(*GOLD, 18))
            draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(*GOLD_LIGHT, 12))

    for i in range(8):
        inset = 18 + i * 4
        draw.rounded_rectangle(
            (inset, inset, WIDTH - inset, HEIGHT - inset),
            radius=34,
            outline=(*GOLD, 130 - i * 12),
            width=2,
        )

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((WIDTH // 2 - 420, 80, WIDTH // 2 + 420, 420), fill=(*GOLD, 45))
    glow_draw.ellipse((WIDTH // 2 - 380, HEIGHT - 500, WIDTH // 2 + 380, HEIGHT - 120), fill=(*GOLD_LIGHT, 35))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=30))

    base = gradient.convert("RGBA")
    base = Image.alpha_composite(base, overlay)
    base = Image.alpha_composite(base, glow)
    return base


PETALS, BOKEH, SPARKLES = build_particles()
STATIC_BACKDROP = create_static_backdrop()
CARD_BASE = fit_contain(Image.open(INVITATION_IMAGE).convert("RGBA"), int(WIDTH * 0.88), int(HEIGHT * 0.82))
OM_FONT = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf", 88)


def draw_corner_roses(draw: ImageDraw.ImageDraw, t: float) -> None:
    corners = [(72, 96), (WIDTH - 72, 96), (72, HEIGHT - 110), (WIDTH - 72, HEIGHT - 110)]
    for idx, (cx, cy) in enumerate(corners):
        sway = math.sin(t * 1.5 + idx) * 5
        for r in range(6):
            angle = r * 60 + idx * 18 + t * 15
            rad = math.radians(angle)
            x = cx + math.cos(rad) * (24 + r * 5) + sway
            y = cy + math.sin(rad) * (20 + r * 4)
            size = 14 - r
            draw.ellipse((x - size, y - size, x + size, y + size), fill=(*ROSE, 210))
            draw.ellipse((x - size // 2, y - size // 2, x + size // 2, y + size // 2), fill=(*ROSE_PALE, 170))


def draw_hanging_bells(draw: ImageDraw.ImageDraw, t: float) -> None:
    for side in (-1, 1):
        anchor_x = WIDTH // 2 + side * 420
        for i in range(4):
            swing = math.sin(t * 2.2 + i * 0.7) * 9
            x = anchor_x + swing
            y = 118 + i * 44
            draw.line([(anchor_x, 92 if i == 0 else y - 18), (x, y - 8)], fill=(*GOLD, 210), width=2)
            draw.ellipse((x - 10, y - 8, x + 10, y + 12), fill=(*GOLD_LIGHT, 230))
            draw.arc((x - 8, y + 2, x + 8, y + 16), 190, 350, fill=(*GOLD, 255), width=2)


def draw_light_rays(draw: ImageDraw.ImageDraw, t: float) -> None:
    origin = (WIDTH // 2, 0)
    for i in range(12):
        spread = -48 + i * 8
        angle = math.radians(-90 + spread + math.sin(t + i) * 3)
        length = HEIGHT * 0.72
        end = (origin[0] + math.cos(angle) * length, origin[1] + math.sin(angle) * length)
        alpha = int(14 + 10 * math.sin(t * 1.5 + i * 0.5))
        draw.line([origin, end], fill=(*GOLD_PALE, alpha), width=5)


def draw_card_layer(t: float) -> Image.Image:
    card_w, card_h = CARD_BASE.size
    pulse = 1.0 + 0.01 * math.sin(t * 2.4)
    scaled_w, scaled_h = int(card_w * pulse), int(card_h * pulse)
    card = CARD_BASE.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
    x = (WIDTH - scaled_w) // 2
    y = (HEIGHT - scaled_h) // 2 + 20

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x + 8, y + 14, x + scaled_w + 8, y + scaled_h + 14), radius=28, fill=(20, 0, 8, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=12))
    layer = Image.alpha_composite(layer, shadow)

    frame_draw = ImageDraw.Draw(layer)
    pad = 12
    glow_alpha = int(190 + 45 * math.sin(t * 2))
    frame_draw.rounded_rectangle((x - pad, y - pad, x + scaled_w + pad, y + scaled_h + pad), radius=30, outline=(*GOLD, glow_alpha), width=5)
    frame_draw.rounded_rectangle((x - pad - 7, y - pad - 7, x + scaled_w + pad + 7, y + scaled_h + pad + 7), radius=34, outline=(*GOLD_LIGHT, int(glow_alpha * 0.6)), width=2)
    layer.paste(card, (x, y), card)
    return layer


def draw_foreground(draw: ImageDraw.ImageDraw, t: float, progress: float) -> None:
    for b in BOKEH:
        twinkle = 0.45 + 0.55 * abs(math.sin(t * b["speed"] + b["phase"]))
        radius = b["radius"] * (0.85 + 0.25 * twinkle)
        x = b["x"] * WIDTH + math.sin(t * 0.7 + b["phase"]) * 12
        y = b["y"] * HEIGHT + math.cos(t * 0.6 + b["phase"]) * 12
        alpha = int(55 * twinkle * ease_out_cubic(progress))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*GOLD_LIGHT, alpha))

    for petal in PETALS:
        y = (petal["y"] + t * petal["speed"]) % 1.2 - 0.1
        x = petal["x"] * WIDTH + math.sin(t * petal["sway"] + petal["phase"]) * 36
        alpha = int(180 * ease_out_cubic(min(1.0, progress * 1.4)))
        size = petal["size"]
        draw.ellipse((x - size, y * HEIGHT - size * 0.5, x + size, y * HEIGHT + size * 0.5), fill=(*petal["color"], alpha))
        draw.ellipse((x - size * 0.5, y * HEIGHT - size, x + size * 0.5, y * HEIGHT + size), fill=(*petal["color"], int(alpha * 0.8)))

    for sparkle in SPARKLES:
        twinkle = abs(math.sin(t * sparkle["speed"] + sparkle["phase"])) ** 2
        alpha = int(230 * twinkle * ease_out_cubic(progress))
        if alpha < 25:
            continue
        x = sparkle["x"] * WIDTH + math.sin(t + sparkle["phase"]) * 6
        y = sparkle["y"] * HEIGHT + math.cos(t * 1.2 + sparkle["phase"]) * 6
        size = sparkle["size"] * (1.2 + twinkle)
        if twinkle > 0.7:
            draw.line([(x - size, y), (x + size, y)], fill=(*GOLD_PALE, alpha), width=2)
            draw.line([(x, y - size), (x, y + size)], fill=(*GOLD_PALE, alpha), width=2)
        draw.ellipse((x, y, x + size * 0.6, y + size * 0.6), fill=(*GOLD, alpha))

    shimmer_x = int((t * 130) % (WIDTH + 500)) - 250
    for offset in range(-90, 120, 18):
        alpha = int(32 + 16 * math.sin(t * 2.5))
        draw.polygon(
            [
                (shimmer_x + offset, 0),
                (shimmer_x + offset + 55, 0),
                (shimmer_x + offset + 200, HEIGHT),
                (shimmer_x + offset + 95, HEIGHT),
            ],
            fill=(*GOLD_PALE, alpha),
        )

    diya_x, diya_y = int(WIDTH * 0.16), int(HEIGHT * 0.845)
    flame_h = 14 + 7 * abs(math.sin(t * 9))
    draw.ellipse((diya_x - 16, diya_y - 8, diya_x + 16, diya_y + 8), fill=(*GOLD, 190))
    draw.ellipse((diya_x - 7, diya_y - flame_h - 6, diya_x + 7, diya_y + 3), fill=(255, 190, 60, 230))

    ring_x, ring_y = int(WIDTH * 0.74), int(HEIGHT * 0.825)
    ring_alpha = int(90 + 110 * (0.5 + 0.5 * math.sin(t * 3)))
    draw.ellipse((ring_x - 32, ring_y - 32, ring_x + 4, ring_y + 4), outline=(*GOLD, ring_alpha), width=4)
    draw.ellipse((ring_x - 8, ring_y - 42, ring_x + 28, ring_y - 4), outline=(*GOLD_LIGHT, ring_alpha), width=4)


def render_single_frame(t: float) -> np.ndarray:
    progress = clamp01(t / DURATION)
    frame = STATIC_BACKDROP.copy()

    rays = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_light_rays(ImageDraw.Draw(rays), t)
    rays = rays.filter(ImageFilter.GaussianBlur(radius=5))
    frame = Image.alpha_composite(frame, rays)

    decor = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    decor_draw = ImageDraw.Draw(decor)
    draw_corner_roses(decor_draw, t)
    draw_hanging_bells(decor_draw, t)
    frame = Image.alpha_composite(frame, decor)

    om_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    om_draw = ImageDraw.Draw(om_layer)
    text = "ॐ"
    alpha = int(255 * ease_out_cubic(min(1.0, progress * 1.8)))
    bbox = om_draw.textbbox((0, 0), text, font=OM_FONT)
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    y = 36 + math.sin(t * 1.5) * 3
    om_draw.text((x, y), text, font=OM_FONT, fill=(*GOLD_LIGHT, alpha))
    om_layer = om_layer.filter(ImageFilter.GaussianBlur(radius=1.2))
    frame = Image.alpha_composite(frame, om_layer)

    frame = Image.alpha_composite(frame, draw_card_layer(t))

    fx = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_foreground(ImageDraw.Draw(fx), t, progress)
    fx = fx.filter(ImageFilter.GaussianBlur(radius=1.1))
    frame = Image.alpha_composite(frame, fx)

    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(vignette).rectangle((0, 0, WIDTH, HEIGHT), fill=(35, 8, 18, 34))
    frame = Image.alpha_composite(frame, vignette)
    return np.array(frame.convert("RGB"))


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
    video = VideoClip(lambda t: render_single_frame(t), duration=DURATION).with_fps(FPS)
    audio = AudioFileClip(str(BG_MUSIC)).with_duration(DURATION)
    video = video.with_audio(audio)
    video.write_videofile(
        str(OUTPUT_VIDEO),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="6000k",
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
