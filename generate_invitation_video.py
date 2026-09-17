#!/usr/bin/env python3
"""Generate a cinematic Ring Ceremony invitation video."""

from __future__ import annotations

import math
import os
import random
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips
from moviepy.video.fx import CrossFadeIn

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
INVITATION_IMAGE = ASSETS / "invitation_source.jpg"
OUTPUT_DIR = ROOT / "output"
OUTPUT_VIDEO = OUTPUT_DIR / "ring_ceremony_invitation.mp4"
BG_MUSIC = ASSETS / "bg_music.wav"

WIDTH, HEIGHT = 1080, 1920
FPS = 30

COLORS = {
    "cream": (245, 232, 210),
    "cream_dark": (232, 210, 178),
    "maroon": (123, 30, 58),
    "maroon_deep": (92, 18, 38),
    "gold": (201, 162, 39),
    "gold_light": (232, 196, 84),
    "gold_pale": (245, 228, 170),
    "text_dark": (74, 34, 34),
    "text_muted": (110, 72, 72),
    "white": (255, 255, 255),
}


@dataclass
class Scene:
    duration: float
    builder: callable


FONT_MAP = {
    "cinzel-bold": "Cinzel.ttf",
    "cinzel-regular": "Cinzel.ttf",
    "cormorant-bold": "CormorantGaramond.ttf",
    "cormorant-regular": "CormorantGaramond.ttf",
    "cormorant-italic": "CormorantGaramond-Italic.ttf",
    "great-vibes": "GreatVibes-Regular.ttf",
}


def load_font(key: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / FONT_MAP[key]), size)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    return 4 * t * t * t if t < 0.5 else 1 - ((-2 * t + 2) ** 3) / 2


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def alpha_blend(base: Image.Image, overlay: Image.Image) -> Image.Image:
    if overlay.mode != "RGBA":
        overlay = overlay.convert("RGBA")
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def draw_radial_glow(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    for step in range(radius, 0, -8):
        a = int(alpha * (step / radius) ** 2)
        bbox = (center[0] - step, center[1] - step, center[0] + step, center[1] + step)
        draw.ellipse(bbox, fill=(*color, a))


def create_background(seed: int = 0) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGBA", (WIDTH, HEIGHT), COLORS["maroon_deep"])
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(lerp(COLORS["maroon_deep"][0], COLORS["maroon"][0], t))
        g = int(lerp(COLORS["maroon_deep"][1], COLORS["maroon"][1], t))
        b = int(lerp(COLORS["maroon_deep"][2], COLORS["maroon"][2], t))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    draw_radial_glow(glow_draw, (WIDTH // 2, HEIGHT // 3), 520, COLORS["gold"], 70)
    draw_radial_glow(glow_draw, (WIDTH // 2, HEIGHT * 2 // 3), 420, COLORS["gold_light"], 45)
    img = alpha_blend(img, glow)

    border = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    inset = 36
    for i in range(6):
        offset = inset + i * 3
        alpha = 120 - i * 15
        border_draw.rounded_rectangle(
            (offset, offset, WIDTH - offset, HEIGHT - offset),
            radius=28,
            outline=(*COLORS["gold"], alpha),
            width=2,
        )
    img = alpha_blend(img, border)

    sparkle_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sparkle_draw = ImageDraw.Draw(sparkle_layer)
    for _ in range(90):
        x = rng.randint(40, WIDTH - 40)
        y = rng.randint(40, HEIGHT - 40)
        size = rng.randint(1, 3)
        alpha = rng.randint(40, 130)
        sparkle_draw.ellipse((x, y, x + size, y + size), fill=(*COLORS["gold_pale"], alpha))
    sparkle_layer = sparkle_layer.filter(ImageFilter.GaussianBlur(radius=0.6))
    img = alpha_blend(img, sparkle_layer)
    return img


def draw_om_symbol(draw: ImageDraw.ImageDraw, center: tuple[int, int], scale: float, alpha: int) -> None:
    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf", int(110 * scale))
    text = "ॐ"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = center[0] - tw // 2
    y = center[1] - th // 2
    draw.text((x, y), text, font=font, fill=(*COLORS["gold_light"], alpha))


def draw_decorative_arch(base: Image.Image, alpha: int = 180) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx = WIDTH // 2
    top = 180
    arch_width = 760
    arch_height = 220

    points = []
    for i in range(61):
        t = i / 60
        angle = math.pi * t
        x = cx + (arch_width / 2) * math.cos(angle)
        y = top + arch_height - arch_height * math.sin(angle)
        points.append((x, y))
    draw.line(points, fill=(*COLORS["gold"], alpha), width=4)

    for side in (-1, 1):
        x = cx + side * (arch_width / 2 + 18)
        for bell in range(4):
            by = top + 40 + bell * 42
            draw.ellipse((x - 8, by - 8, x + 8, by + 8), fill=(*COLORS["gold_light"], alpha))
            draw.line([(x, by + 8), (x, by + 24)], fill=(*COLORS["gold"], alpha), width=2)

    return alpha_blend(base, layer)


def draw_center_panel(base: Image.Image, alpha: int = 235) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    panel = (90, 250, WIDTH - 90, HEIGHT - 180)
    draw.rounded_rectangle(panel, radius=36, fill=(*COLORS["cream"], alpha))
    inner = (panel[0] + 18, panel[1] + 18, panel[2] - 18, panel[3] - 18)
    draw.rounded_rectangle(inner, radius=28, outline=(*COLORS["gold"], 180), width=3)
    return alpha_blend(base, layer)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = font.getbbox(candidate)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text_block(
    base: Image.Image,
    lines: list[str],
    y_start: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    line_spacing: float = 1.35,
    align: str = "center",
) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bbox = font.getbbox("Ay")
    line_height = int((bbox[3] - bbox[1]) * line_spacing)
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        if align == "center":
            x = (WIDTH - tw) // 2
        else:
            x = 120
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return alpha_blend(base, layer)


def draw_title_script(
    base: Image.Image,
    text: str,
    y: int,
    size: int,
    alpha: int,
) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = load_font("great-vibes", size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    draw.text((x + 2, y + 2), text, font=font, fill=(*COLORS["maroon_deep"], alpha // 3))
    draw.text((x, y), text, font=font, fill=(*COLORS["maroon"], alpha))
    return alpha_blend(base, layer)


def draw_detail_card(
    base: Image.Image,
    label: str,
    value_lines: list[str],
    x_center: int,
    y: int,
    alpha: int,
) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    card_w, card_h = 280, 220
    left = x_center - card_w // 2
    top = y
    draw.rounded_rectangle(
        (left, top, left + card_w, top + card_h),
        radius=22,
        fill=(*COLORS["white"], int(alpha * 0.92)),
        outline=(*COLORS["gold"], alpha),
        width=2,
    )
    label_font = load_font("cinzel-bold", 28)
    value_font = load_font("cormorant-regular", 30)
    icon_font = load_font("cinzel-regular", 34)

    icon_map = {"Date": "◷", "Time": "◔", "Venue": "◉"}
    icon = icon_map.get(label, "✦")
    icon_bbox = draw.textbbox((0, 0), icon, font=icon_font)
    draw.text(
        (x_center - (icon_bbox[2] - icon_bbox[0]) // 2, top + 18),
        icon,
        font=icon_font,
        fill=(*COLORS["gold"], alpha),
    )

    label_bbox = draw.textbbox((0, 0), label.upper(), font=label_font)
    draw.text(
        (x_center - (label_bbox[2] - label_bbox[0]) // 2, top + 62),
        label.upper(),
        font=label_font,
        fill=(*COLORS["maroon"], alpha),
    )

    vy = top + 108
    for line in value_lines:
        bbox = draw.textbbox((0, 0), line, font=value_font)
        draw.text(
            (x_center - (bbox[2] - bbox[0]) // 2, vy),
            line,
            font=value_font,
            fill=(*COLORS["text_dark"], alpha),
        )
        vy += 34
    return alpha_blend(base, layer)


def render_opening(progress: float) -> np.ndarray:
    img = create_background(seed=1)
    img = draw_decorative_arch(img, alpha=int(180 * ease_out_cubic(clamp01(progress * 1.5))))
    img = draw_center_panel(img, alpha=int(220 * ease_out_cubic(clamp01(progress * 1.2))))

    om_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.05) / 0.35)))
    if om_alpha > 0:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw_om_symbol(draw, (WIDTH // 2, 360), 1.0, om_alpha)
        img = alpha_blend(img, layer)

    quote_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.25) / 0.45)))
    if quote_alpha > 0:
        font = load_font("cormorant-italic", 42)
        lines = wrap_text(
            "Two hearts, one journey, a lifetime of togetherness...",
            font,
            WIDTH - 220,
        )
        img = draw_text_block(img, lines, 470, font, (*COLORS["text_muted"], quote_alpha))

    return np.array(img.convert("RGB"))


def render_invitation(progress: float) -> np.ndarray:
    img = create_background(seed=2)
    img = draw_decorative_arch(img)
    img = draw_center_panel(img)

    intro_alpha = int(255 * ease_out_cubic(clamp01(progress / 0.45)))
    if intro_alpha > 0:
        font = load_font("cormorant-regular", 36)
        lines = wrap_text(
            "With the blessings of our families, we cordially invite you to the",
            font,
            WIDTH - 220,
        )
        img = draw_text_block(img, lines, 360, font, (*COLORS["text_dark"], intro_alpha))

    title_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.25) / 0.35)))
    if title_alpha > 0:
        img = draw_title_script(img, "Ring Ceremony", 520, 96, title_alpha)

    suffix_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.45) / 0.35)))
    if suffix_alpha > 0:
        font = load_font("cormorant-regular", 38)
        img = draw_text_block(img, ["of"], 650, font, (*COLORS["text_dark"], suffix_alpha))

    return np.array(img.convert("RGB"))


def render_names(progress: float) -> np.ndarray:
    img = create_background(seed=3)
    img = draw_decorative_arch(img)
    img = draw_center_panel(img)

    name1_alpha = int(255 * ease_out_cubic(clamp01(progress / 0.4)))
    if name1_alpha > 0:
        img = draw_title_script(img, "Tanya Goel", 430, 92, name1_alpha)

    amp_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.25) / 0.25)))
    if amp_alpha > 0:
        font = load_font("cinzel-regular", 42)
        img = draw_text_block(img, ["&"], 560, font, (*COLORS["gold"], amp_alpha))

    name2_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.45) / 0.4)))
    if name2_alpha > 0:
        img = draw_title_script(img, "Prabhat Goel", 640, 92, name2_alpha)

    message_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.65) / 0.35)))
    if message_alpha > 0:
        font = load_font("cormorant-italic", 34)
        lines = wrap_text(
            "As we begin this beautiful journey of love and togetherness, "
            "we would be delighted to have you grace the occasion with your presence and blessings.",
            font,
            WIDTH - 220,
        )
        img = draw_text_block(img, lines, 820, font, (*COLORS["text_muted"], message_alpha), line_spacing=1.4)

    return np.array(img.convert("RGB"))


def render_details(progress: float) -> np.ndarray:
    img = create_background(seed=4)
    img = draw_decorative_arch(img)
    img = draw_center_panel(img)

    header_alpha = int(255 * ease_out_cubic(clamp01(progress / 0.25)))
    if header_alpha > 0:
        font = load_font("cinzel-bold", 34)
        img = draw_text_block(img, ["SAVE THE DATE"], 320, font, (*COLORS["maroon"], header_alpha))

    cards = [
        ("Date", ["Saturday,", "24 October"], WIDTH // 2, 430),
        ("Time", ["11:00 AM"], WIDTH // 2, 690),
        ("Venue", ["The Tonight Rooms", "and Party Hall,", "Railway Road, Hapur"], WIDTH // 2, 930),
    ]

    for idx, (label, lines, x, y) in enumerate(cards):
        start = 0.15 + idx * 0.22
        card_alpha = int(255 * ease_out_cubic(clamp01((progress - start) / 0.25)))
        if card_alpha > 0:
            img = draw_detail_card(img, label, lines, x, y, card_alpha)

    return np.array(img.convert("RGB"))


def render_closing(progress: float) -> np.ndarray:
    img = create_background(seed=5)
    img = draw_decorative_arch(img)
    img = draw_center_panel(img)

    msg_alpha = int(255 * ease_out_cubic(clamp01(progress / 0.45)))
    if msg_alpha > 0:
        font = load_font("cormorant-regular", 40)
        lines = wrap_text(
            "Your presence will make our celebration even more special.",
            font,
            WIDTH - 220,
        )
        img = draw_text_block(img, lines, 520, font, (*COLORS["text_dark"], msg_alpha), line_spacing=1.45)

    sign_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.35) / 0.35)))
    if sign_alpha > 0:
        font = load_font("cormorant-italic", 38)
        img = draw_text_block(img, ["With Love,"], 760, font, (*COLORS["text_muted"], sign_alpha))

    family_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.55) / 0.35)))
    if family_alpha > 0:
        img = draw_title_script(img, "Goel Family", 830, 78, family_alpha)

    rings_alpha = int(255 * ease_out_cubic(clamp01((progress - 0.7) / 0.3)))
    if rings_alpha > 0:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        cx, cy = WIDTH // 2, 1120
        draw.ellipse((cx - 58, cy - 58, cx - 8, cy - 8), outline=(*COLORS["gold"], rings_alpha), width=5)
        draw.ellipse((cx - 18, cy - 68, cx + 32, cy - 18), outline=(*COLORS["gold_light"], rings_alpha), width=5)
        img = alpha_blend(img, layer)

    return np.array(img.convert("RGB"))


def fit_cover(image: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = image.size
    scale = max(width / src_w, height / src_h)
    new_size = (int(src_w * scale), int(src_h * scale))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    left = (new_size[0] - width) // 2
    top = (new_size[1] - height) // 2
    return resized.crop((left, top, left + width, top + height))


def render_card_reveal(progress: float) -> np.ndarray:
    invitation = Image.open(INVITATION_IMAGE).convert("RGB")
    fitted = fit_cover(invitation, WIDTH, HEIGHT)

    zoom = lerp(1.08, 1.0, ease_in_out_cubic(progress))
    w, h = fitted.size
    crop_w = int(WIDTH / zoom)
    crop_h = int(HEIGHT / zoom)
    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    cropped = fitted.crop((left, top, left + crop_w, top + crop_h)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    vignette_alpha = int(lerp(120, 35, progress))
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(40, 8, 18, vignette_alpha))
    frame_alpha = int(lerp(0, 180, ease_out_cubic(clamp01(progress / 0.4))))
    if frame_alpha:
        draw.rounded_rectangle((24, 24, WIDTH - 24, HEIGHT - 24), radius=20, outline=(*COLORS["gold"], frame_alpha), width=4)

    result = alpha_blend(cropped.convert("RGBA"), overlay)
    fade = ease_out_cubic(clamp01(progress / 0.25))
    if fade < 1:
        black = Image.new("RGBA", (WIDTH, HEIGHT), (*COLORS["maroon_deep"], int(255 * (1 - fade))))
        result = alpha_blend(black, result)
    return np.array(result.convert("RGB"))


def make_scene_clip(duration: float, renderer) -> VideoClip:
    def frame_at(t: float) -> np.ndarray:
        return renderer(clamp01(t / duration))

    return VideoClip(frame_at, duration=duration).with_fps(FPS)


def generate_background_music() -> None:
    if BG_MUSIC.exists():
        return
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=220:duration=32",
        "-af",
        "volume=0.06,afade=t=in:st=0:d=2,afade=t=out:st=28:d=4",
        str(BG_MUSIC),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_video() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generate_background_music()

    scenes = [
        make_scene_clip(4.0, render_opening),
        make_scene_clip(4.0, render_invitation),
        make_scene_clip(5.0, render_names),
        make_scene_clip(6.0, render_details),
        make_scene_clip(4.5, render_closing),
        make_scene_clip(4.5, render_card_reveal),
    ]

    transition = 0.6
    faded_scenes = [scenes[0]]
    for clip in scenes[1:]:
        faded_scenes.append(clip.with_effects([CrossFadeIn(transition)]))

    video = concatenate_videoclips(faded_scenes, method="compose", padding=-transition)
    audio = AudioFileClip(str(BG_MUSIC)).with_duration(video.duration)
    video = video.with_audio(audio)

    video.write_videofile(
        str(OUTPUT_VIDEO),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="8000k",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        logger=None,
    )
    video.close()
    audio.close()
    return OUTPUT_VIDEO


if __name__ == "__main__":
    output = build_video()
    print(f"Created: {output}")
