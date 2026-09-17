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
FONTS = ASSETS / "fonts"
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
TEXT_DARK = (74, 34, 34)
TEXT_MUTED = (110, 72, 72)

FONT_MAP = {
    "great-vibes": "GreatVibes-Regular.ttf",
    "cinzel": "Cinzel.ttf",
    "cormorant": "CormorantGaramond.ttf",
    "cormorant-italic": "CormorantGaramond-Italic.ttf",
}


def load_font(key: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / FONT_MAP[key]), size)


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
OM_FONT = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf", 72)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.getbbox(candidate)[2] - font.getbbox(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    panel_left: int,
    panel_width: int,
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = panel_left + (panel_width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + th


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    panel_left: int,
    panel_width: int,
    spacing: float = 1.35,
) -> int:
    line_h = int((font.getbbox("Ay")[3] - font.getbbox("Ay")[1]) * spacing)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = panel_left + (panel_width - tw) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def draw_invitation_panel(t: float, progress: float) -> Image.Image:
    panel_left, panel_top = 72, 210
    panel_right, panel_bottom = WIDTH - 72, HEIGHT - 210
    panel_width = panel_right - panel_left

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (panel_left + 8, panel_top + 14, panel_right + 8, panel_bottom + 14),
        radius=34,
        fill=(20, 0, 8, 130),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=14))
    layer = Image.alpha_composite(layer, shadow)

    panel = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_alpha = int(245 * ease_out_cubic(min(1.0, progress * 2.5)))
    panel_draw.rounded_rectangle(
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=34,
        fill=(*CREAM, panel_alpha),
    )
    glow_alpha = int(180 + 45 * math.sin(t * 2))
    panel_draw.rounded_rectangle(
        (panel_left + 14, panel_top + 14, panel_right - 14, panel_bottom - 14),
        radius=28,
        outline=(*GOLD, glow_alpha),
        width=3,
    )
    layer = Image.alpha_composite(layer, panel)

    content = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(content)
    text_alpha = int(255 * ease_out_cubic(min(1.0, progress * 2.2)))
    y = panel_top + 36

    om_bbox = draw.textbbox((0, 0), "ॐ", font=OM_FONT)
    om_x = panel_left + (panel_width - (om_bbox[2] - om_bbox[0])) // 2
    draw.text((om_x, y), "ॐ", font=OM_FONT, fill=(*GOLD, text_alpha))
    y += 82

    quote_font = load_font("cormorant-italic", 30)
    y = draw_centered_lines(
        draw,
        wrap_text("Two hearts, one journey, a lifetime of togetherness...", quote_font, panel_width - 80),
        y,
        quote_font,
        (*TEXT_MUTED, text_alpha),
        panel_left,
        panel_width,
        1.3,
    )
    y += 18

    intro_font = load_font("cormorant", 28)
    y = draw_centered_lines(
        draw,
        wrap_text(
            "With the blessings of our families, we cordially invite you to the",
            intro_font,
            panel_width - 80,
        ),
        y,
        intro_font,
        (*TEXT_DARK, text_alpha),
        panel_left,
        panel_width,
        1.28,
    )
    y += 10

    title_font = load_font("great-vibes", 88)
    title_glow = int(40 + 25 * math.sin(t * 2.2))
    y = draw_centered_text(draw, "Ring Ceremony", y, title_font, (*MAROON_LIGHT, text_alpha), panel_left, panel_width)
    y += 8
    draw.rounded_rectangle(
        (panel_left + 120, y - 4, panel_right - 120, y + 4),
        radius=4,
        fill=(*GOLD, title_glow),
    )
    y += 18

    of_font = load_font("cinzel", 30)
    y = draw_centered_text(draw, "of", y, of_font, (*TEXT_DARK, text_alpha), panel_left, panel_width)
    y += 8

    name_font = load_font("great-vibes", 72)
    name_pulse = int(255 * (0.92 + 0.08 * math.sin(t * 2.5)))
    y = draw_centered_text(draw, "Tanya Goel", y, name_font, (*MAROON_LIGHT, min(text_alpha, name_pulse)), panel_left, panel_width)
    y += 4

    amp_font = load_font("cinzel", 34)
    y = draw_centered_text(draw, "&", y, amp_font, (*GOLD, text_alpha), panel_left, panel_width)
    y += 2

    y = draw_centered_text(draw, "Prabhat Goel", y, name_font, (*MAROON_LIGHT, min(text_alpha, name_pulse)), panel_left, panel_width)
    y += 20

    msg_font = load_font("cormorant-italic", 26)
    y = draw_centered_lines(
        draw,
        wrap_text(
            "As we begin this beautiful journey of love and togetherness, "
            "we would be delighted to have you grace the occasion with your presence and blessings.",
            msg_font,
            panel_width - 70,
        ),
        y,
        msg_font,
        (*TEXT_MUTED, text_alpha),
        panel_left,
        panel_width,
        1.32,
    )
    y += 16

    detail_font = load_font("cormorant", 24)
    label_font = load_font("cinzel", 20)
    col_w = panel_width // 3
    details = [
        ("DATE", "Saturday,\n24 October"),
        ("TIME", "11:00 AM"),
        ("VENUE", "The Tonight Rooms\nand Party Hall,\nRailway Road, Hapur"),
    ]
    for idx, (label, value) in enumerate(details):
        cx = panel_left + col_w * idx + col_w // 2
        box_left = panel_left + col_w * idx + 12
        box_right = panel_left + col_w * (idx + 1) - 12
        draw.rounded_rectangle(
            (box_left, y, box_right, y + 150),
            radius=16,
            fill=(255, 255, 255, int(text_alpha * 0.85)),
            outline=(*GOLD, int(text_alpha * 0.8)),
            width=2,
        )
        label_bbox = draw.textbbox((0, 0), label, font=label_font)
        draw.text(
            (cx - (label_bbox[2] - label_bbox[0]) // 2, y + 14),
            label,
            font=label_font,
            fill=(*MAROON_LIGHT, text_alpha),
        )
        vy = y + 48
        for line in value.split("\n"):
            bbox = draw.textbbox((0, 0), line, font=detail_font)
            draw.text(
                (cx - (bbox[2] - bbox[0]) // 2, vy),
                line,
                font=detail_font,
                fill=(*TEXT_DARK, text_alpha),
            )
            vy += 28

    y += 168
    close_font = load_font("cormorant", 28)
    y = draw_centered_lines(
        draw,
        wrap_text("Your presence will make our celebration even more special.", close_font, panel_width - 70),
        y,
        close_font,
        (*TEXT_DARK, text_alpha),
        panel_left,
        panel_width,
        1.35,
    )
    y += 8
    sign_font = load_font("cormorant-italic", 26)
    y = draw_centered_text(draw, "With Love,", y, sign_font, (*TEXT_MUTED, text_alpha), panel_left, panel_width)
    family_font = load_font("great-vibes", 58)
    draw_centered_text(draw, "Goel Family", y, family_font, (*MAROON_LIGHT, text_alpha), panel_left, panel_width)

    layer = Image.alpha_composite(layer, content)
    return layer


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


def draw_invitation_panel_layer(t: float, progress: float) -> Image.Image:
    return draw_invitation_panel(t, progress)


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

    frame = Image.alpha_composite(frame, draw_invitation_panel_layer(t, progress))

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
