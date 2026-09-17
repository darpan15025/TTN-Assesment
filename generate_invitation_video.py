#!/usr/bin/env python3
"""Premium animated Ring Ceremony invitation video — single view."""

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
FPS = 30
DURATION = 24.0

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
TEAL = (32, 110, 112)

PANEL = (58, 140, WIDTH - 58, HEIGHT - 140)
PANEL_W = PANEL[2] - PANEL[0]

FONT_MAP = {
    "great-vibes": "GreatVibes-Regular.ttf",
    "cinzel": "Cinzel.ttf",
    "cormorant": "CormorantGaramond.ttf",
    "cormorant-italic": "CormorantGaramond-Italic.ttf",
}


def load_font(key: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / FONT_MAP[key]), size)


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_out_back(t: float) -> float:
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_elastic(t: float) -> float:
    if t in (0, 1):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def segment_progress(t: float, start: float, end: float) -> float:
    if end <= start:
        return 1.0 if t >= start else 0.0
    return clamp01((t - start) / (end - start))


FONTS_CACHE = {
    "om": ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf", 70),
    "quote": load_font("cormorant-italic", 26),
    "intro": load_font("cormorant", 25),
    "title": load_font("great-vibes", 82),
    "of": load_font("cinzel", 28),
    "name": load_font("great-vibes", 68),
    "amp": load_font("cinzel", 32),
    "msg": load_font("cormorant-italic", 23),
    "detail": load_font("cormorant", 21),
    "label": load_font("cinzel", 18),
    "close": load_font("cormorant", 25),
    "sign": load_font("cormorant-italic", 23),
    "family": load_font("great-vibes", 50),
}


def build_particles() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    rng = random.Random(42)
    petals, bokeh, sparkles, embers = [], [], [], []
    for _ in range(55):
        petals.append(
            {
                "x": rng.uniform(0, 1),
                "y": rng.uniform(-0.3, 1.1),
                "size": rng.uniform(7, 20),
                "speed": rng.uniform(0.025, 0.07),
                "sway": rng.uniform(0.6, 1.8),
                "phase": rng.uniform(0, math.tau),
                "color": rng.choice([ROSE, ROSE_PALE, GOLD_PALE, CREAM, (255, 200, 200)]),
            }
        )
    for _ in range(30):
        bokeh.append(
            {
                "x": rng.uniform(0.02, 0.98),
                "y": rng.uniform(0.02, 0.98),
                "r": rng.uniform(14, 58),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.7, 1.8),
            }
        )
    for _ in range(110):
        sparkles.append(
            {
                "x": rng.uniform(0, 1),
                "y": rng.uniform(0, 1),
                "size": rng.uniform(1.5, 5),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(1.2, 3.5),
            }
        )
    for _ in range(40):
        embers.append(
            {
                "x": rng.uniform(0.1, 0.9),
                "y": rng.uniform(0.5, 1.1),
                "speed": rng.uniform(0.03, 0.09),
                "size": rng.uniform(2, 5),
                "phase": rng.uniform(0, math.tau),
            }
        )
    return petals, bokeh, sparkles, embers


PETALS, BOKEH, SPARKLES, EMBERS = build_particles()


def create_static_backdrop() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), MAROON)
    draw = ImageDraw.Draw(img)
    for y in range(0, HEIGHT, 3):
        blend = y / HEIGHT
        r = int(lerp(MAROON[0], MAROON_LIGHT[0], blend * 0.6))
        g = int(lerp(MAROON[1], MAROON_LIGHT[1], blend * 0.6))
        b = int(lerp(MAROON[2], MAROON_LIGHT[2], blend * 0.6))
        draw.rectangle((0, y, WIDTH, y + 3), fill=(r, g, b))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(9):
        inset = 14 + i * 4
        od.rounded_rectangle(
            (inset, inset, WIDTH - inset, HEIGHT - inset),
            radius=36,
            outline=(*GOLD, 135 - i * 12),
            width=2,
        )
    return Image.alpha_composite(img.convert("RGBA"), overlay)


STATIC_BACKDROP = create_static_backdrop()


def prepare_invitation_art() -> dict[str, Image.Image]:
    inv = Image.open(INVITATION_IMAGE).convert("RGBA")
    iw, ih = inv.size
    top = inv.crop((int(iw * 0.04), 0, int(iw * 0.96), int(ih * 0.13)))
    bottom = inv.crop((0, int(ih * 0.72), iw, ih))
    left = inv.crop((0, int(ih * 0.12), int(iw * 0.17), int(ih * 0.88)))
    right = inv.crop((int(iw * 0.83), int(ih * 0.12), iw, int(ih * 0.88)))
    paisley_tile = inv.crop((int(iw * 0.02), int(ih * 0.28), int(iw * 0.16), int(ih * 0.42)))

    top_h = int(PANEL_W * top.height / top.width * 0.75)
    bottom_h = int(PANEL_W * bottom.height / bottom.width * 0.58)
    side_w = int(PANEL_W * 0.11)
    tile = paisley_tile.resize((120, 120), Image.Resampling.LANCZOS)

    return {
        "top": top.resize((PANEL_W, top_h), Image.Resampling.LANCZOS),
        "bottom": bottom.resize((PANEL_W, bottom_h), Image.Resampling.LANCZOS),
        "left": left.resize((side_w, int((PANEL[3] - PANEL[1]) * 0.72)), Image.Resampling.LANCZOS),
        "right": right.resize((side_w, int((PANEL[3] - PANEL[1]) * 0.72)), Image.Resampling.LANCZOS),
        "tile": tile,
    }


INVITATION_ART = prepare_invitation_art()


def draw_panel_rich_fill(base: Image.Image, prc: tuple[int, int, int, int], t: float, alpha: int) -> Image.Image:
    pl, pt, pr, pb = prc
    pw, ph = pr - pl, pb - pt
    panel_img = base.copy()

    tile = INVITATION_ART["tile"]
    tiled = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    for yy in range(0, ph, tile.height):
        for xx in range(0, pw, tile.width):
            ghost = tile.copy()
            ghost.putalpha(28)
            tiled.paste(ghost, (xx, yy), ghost)
    panel_img.paste(tiled, (pl, pt), tiled)

    paisley = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(paisley)
    for yy in range(0, ph, 52):
        for xx in range(0, pw, 52):
            cx, cy = xx + 26, yy + 26
            a = 16 + int(8 * math.sin(t * 1.2 + xx * 0.01 + yy * 0.01))
            pd.pieslice((cx - 16, cy - 16, cx + 16, cy + 16), 210, 330, fill=(*TEAL, a))
            pd.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(*GOLD, a + 8))
    panel_img.paste(paisley, (pl, pt), paisley)

    left = INVITATION_ART["left"].copy()
    right = INVITATION_ART["right"].copy()
    left.putalpha(int(alpha * 0.88))
    right.putalpha(int(alpha * 0.88))
    panel_img.paste(left, (pl + 6, pt + int(ph * 0.13)), left)
    panel_img.paste(right, (pr - right.width - 6, pt + int(ph * 0.13)), right)

    top = INVITATION_ART["top"].copy()
    top.putalpha(int(alpha * 0.94))
    panel_img.paste(top, (pl + (pw - top.width) // 2, pt - int(top.height * 0.16)), top)

    bottom = INVITATION_ART["bottom"].copy()
    bottom.putalpha(int(alpha * 0.96))
    by = pb - bottom.height + 6
    panel_img.paste(bottom, (pl + (pw - bottom.width) // 2, by), bottom)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((pl + 10, pt + 10, pr - 10, pb - 10), radius=26, outline=(*GOLD, int(120 + 40 * math.sin(t * 2))), width=2)
    od.line([(pl + 28, by - 6), (pr - 28, by - 6)], fill=(*GOLD, 100), width=2)
    return Image.alpha_composite(panel_img, overlay)


def draw_panel_corner_flowers(base: Image.Image, prc: tuple[int, int, int, int], t: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    pl, pt, pr, pb = prc
    corners = [(pl + 34, pt + 130), (pr - 34, pt + 130), (pl + 34, pb - 140), (pr - 34, pb - 140)]
    for idx, (cx, cy) in enumerate(corners):
        sway = math.sin(t * 1.4 + idx) * 4
        for r in range(8):
            ang = math.radians(r * 45 + idx * 22 + t * 12)
            dist = 15 + r * 4
            x = cx + math.cos(ang) * dist + sway
            y = cy + math.sin(ang) * (dist * 0.82)
            sz = max(4, 12 - r)
            draw.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(*ROSE, 220))
            if r % 2 == 0:
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255, 180))
    return Image.alpha_composite(base, layer)


def draw_footer_ornaments(draw: ImageDraw.ImageDraw, prc: tuple[int, int, int, int], t: float, alpha: int) -> None:
    pl, pt, pr, pb = prc
    base_y = pb - 108
    dx = pl + 92
    dy = base_y + 8
    flame = 12 + 8 * abs(math.sin(t * 10))
    draw.ellipse((dx - 22, dy, dx + 22, dy + 22), fill=(*GOLD, alpha))
    draw.polygon([(dx - 16, dy + 2), (dx + 16, dy + 2), (dx + 24, dy + 20), (dx - 24, dy + 20)], fill=(*GOLD_LIGHT, alpha))
    draw.ellipse((dx - 7, dy - flame, dx + 7, dy + 4), fill=(255, 180, 50, alpha))
    for px in (dx - 28, dx - 8, dx + 14, dx + 32):
        draw.ellipse((px - 5, dy + 24, px + 5, dy + 30), fill=(*ROSE, int(alpha * 0.85)))

    rx, ry = pr - 125, base_y + 10
    rot = t * 15
    for i, (ox, oy, r) in enumerate([(0, 0, 21), (15, -9, 18)]):
        ang = math.radians(rot + i * 24)
        rcx = rx + ox + math.cos(ang) * 2
        rcy = ry + oy + math.sin(ang) * 2
        draw.ellipse((rcx - r, rcy - r, rcx + r, rcy + r), outline=(*GOLD, alpha), width=4)

    fx = (pl + pr) // 2
    for i in range(7):
        x = fx - 84 + i * 24 + math.sin(t * 2 + i) * 3
        h = 32 + i * 4
        c = [(20, 130, 80), (30, 90, 150), (15, 110, 70)][i % 3]
        draw.line([(x, base_y + 20), (x + 8, base_y + 20 - h)], fill=(*c, alpha), width=3)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        cand = f"{cur} {word}".strip()
        if font.getbbox(cand)[2] - font.getbbox(cand)[0] <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bb = font.getbbox(text)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_rotating_mandala(base: Image.Image, t: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = WIDTH // 2, HEIGHT // 2 - 40
    for ring in range(4):
        radius = 280 + ring * 90
        start = math.degrees(t * (12 + ring * 4))
        for i in range(16):
            a1 = math.radians(start + i * 22.5)
            a2 = math.radians(start + i * 22.5 + 14)
            x1, y1 = cx + math.cos(a1) * radius, cy + math.sin(a1) * radius
            x2, y2 = cx + math.cos(a2) * radius, cy + math.sin(a2) * radius
            draw.line([(x1, y1), (x2, y2)], fill=(*GOLD, 22 - ring * 3), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    return Image.alpha_composite(base, layer)


def draw_light_burst(base: Image.Image, t: float, intro: float) -> Image.Image:
    if intro <= 0:
        return base
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    alpha = int(90 * (1 - intro) * intro * 4)
    draw.ellipse((WIDTH // 2 - 500, 40, WIDTH // 2 + 500, 700), fill=(*GOLD_LIGHT, alpha))
    for i in range(16):
        ang = math.radians(-90 + i * 11 + t * 8)
        end = (WIDTH // 2 + math.cos(ang) * 900, math.sin(ang) * 900)
        draw.line([(WIDTH // 2, 0), end], fill=(*GOLD_PALE, int(alpha * 0.5)), width=6)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=12))
    return Image.alpha_composite(base, layer)


def draw_corner_roses(base: Image.Image, t: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for idx, (cx, cy) in enumerate([(64, 88), (WIDTH - 64, 88), (64, HEIGHT - 96), (WIDTH - 64, HEIGHT - 96)]):
        sway = math.sin(t * 1.6 + idx) * 6
        bloom = 0.7 + 0.3 * math.sin(t * 1.2 + idx)
        for r in range(7):
            ang = math.radians(r * 52 + idx * 20 + t * 18)
            x = cx + math.cos(ang) * (22 + r * 5) * bloom + sway
            y = cy + math.sin(ang) * (18 + r * 4) * bloom
            sz = int((13 - r) * bloom)
            draw.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(*ROSE, 215))
            draw.ellipse((x - sz // 2, y - sz // 2, x + sz // 2, y + sz // 2), fill=(*ROSE_PALE, 180))
    return Image.alpha_composite(base, layer)


def draw_hanging_bells(base: Image.Image, t: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for side in (-1, 1):
        ax = WIDTH // 2 + side * 430
        for i in range(5):
            swing = math.sin(t * 2.4 + i * 0.65) * 11
            x, y = ax + swing, 108 + i * 42
            draw.line([(ax, 82 if i == 0 else y - 16), (x, y - 6)], fill=(*GOLD, 220), width=2)
            draw.ellipse((x - 11, y - 8, x + 11, y + 12), fill=(*GOLD_LIGHT, 240))
            draw.arc((x - 9, y + 2, x + 9, y + 18), 190, 350, fill=(*GOLD, 255), width=2)
    return Image.alpha_composite(base, layer)


def draw_ambient_fx(base: Image.Image, t: float, reveal: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for b in BOKEH:
        tw = 0.4 + 0.6 * abs(math.sin(t * b["speed"] + b["phase"]))
        r = b["r"] * (0.85 + 0.3 * tw)
        x = b["x"] * WIDTH + math.sin(t * 0.8 + b["phase"]) * 16
        y = b["y"] * HEIGHT + math.cos(t * 0.7 + b["phase"]) * 16
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*GOLD_LIGHT, int(50 * tw * reveal)))

    for p in PETALS:
        y = (p["y"] + t * p["speed"]) % 1.25 - 0.12
        x = p["x"] * WIDTH + math.sin(t * p["sway"] + p["phase"]) * 42
        a = int(195 * reveal)
        s = p["size"]
        draw.ellipse((x - s, y * HEIGHT - s * 0.5, x + s, y * HEIGHT + s * 0.5), fill=(*p["color"], a))

    for e in EMBERS:
        y = 1.0 - ((1.0 - e["y"] + t * e["speed"]) % 1.0)
        x = e["x"] * WIDTH + math.sin(t * 3 + e["phase"]) * 20
        a = int(200 * abs(math.sin(t * 4 + e["phase"])) * reveal)
        s = e["size"]
        draw.ellipse((x, y * HEIGHT, x + s, y * HEIGHT + s * 1.8), fill=(*GOLD, a))

    for s in SPARKLES:
        tw = abs(math.sin(t * s["speed"] + s["phase"])) ** 1.8
        a = int(240 * tw * reveal)
        if a < 20:
            continue
        x = s["x"] * WIDTH + math.sin(t + s["phase"]) * 8
        y = s["y"] * HEIGHT + math.cos(t * 1.3 + s["phase"]) * 8
        sz = s["size"] * (1.3 + tw)
        if tw > 0.72:
            draw.line([(x - sz, y), (x + sz, y)], fill=(*GOLD_PALE, a), width=2)
            draw.line([(x, y - sz), (x, y + sz)], fill=(*GOLD_PALE, a), width=2)
        draw.ellipse((x, y, x + sz * 0.5, y + sz * 0.5), fill=(*GOLD, a))

    sx = int((t * 160) % (WIDTH + 600)) - 300
    for off in range(-110, 150, 14):
        draw.polygon(
            [(sx + off, 0), (sx + off + 50, 0), (sx + off + 210, HEIGHT), (sx + off + 90, HEIGHT)],
            fill=(*GOLD_PALE, int(36 * reveal)),
        )

    layer = layer.filter(ImageFilter.GaussianBlur(radius=1.2))
    return Image.alpha_composite(base, layer)


def draw_animated_rings(base: Image.Image, cx: int, cy: int, t: float, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rot = t * 18
    for i, (ox, oy, r) in enumerate([(0, 0, 36), (18, -12, 32)]):
        angle = math.radians(rot + i * 28)
        rcx = cx + math.cos(angle) * 4
        rcy = cy + math.sin(angle) * 3
        draw.ellipse((rcx + ox - r, rcy + oy - r, rcx + ox + r, rcy + oy + r), outline=(*GOLD, alpha), width=4)
        pulse = int(alpha * (0.5 + 0.5 * math.sin(t * 4 + i)))
        draw.ellipse((rcx + ox - r - 6, rcy + oy - r - 6, rcx + ox + r + 6, rcy + oy + r + 6), outline=(*GOLD_LIGHT, pulse), width=1)
    return Image.alpha_composite(base, layer)


def draw_hero_glow(base: Image.Image, top: int, bottom: int, t: float, strength: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    pulse = 0.55 + 0.45 * math.sin(t * 2.8)
    alpha = int(55 * strength * pulse)
    draw.rounded_rectangle(
        (PANEL[0] + 40, top - 20, PANEL[2] - 40, bottom + 24),
        radius=40,
        fill=(*GOLD, alpha),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(base, layer)


def anim_alpha(prog: float, delay: float = 0.0, duration: float = 0.5) -> int:
    p = segment_progress(prog, delay, delay + duration)
    return int(255 * ease_out_cubic(p))


def anim_offset(prog: float, delay: float, duration: float, distance: float = 40) -> float:
    p = segment_progress(prog, delay, delay + duration)
    return (1 - ease_out_back(p)) * distance


def anim_scale(prog: float, delay: float, duration: float) -> float:
    p = segment_progress(prog, delay, delay + duration)
    return 0.82 + 0.18 * ease_out_elastic(p)


def draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    tw, th = text_size(text, font)
    x = PANEL[0] + (PANEL_W - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return x, y, x + tw, y + th


def draw_invitation_panel(t: float) -> Image.Image:
    prog = clamp01(t / DURATION)
    intro = segment_progress(prog, 0.0, 0.18)
    panel_in = segment_progress(prog, 0.08, 0.28)
    hero_in = segment_progress(prog, 0.22, 0.42)
    details_in = segment_progress(prog, 0.42, 0.62)
    rest_in = segment_progress(prog, 0.52, 0.72)

    panel_scale = 0.88 + 0.12 * ease_out_back(panel_in)
    panel_alpha = int(250 * ease_out_cubic(panel_in))
    panel_dy = int((1 - ease_out_back(panel_in)) * 80)

    pl, pt, pr, pb = PANEL
    pcx, pcy = (pl + pr) // 2, (pt + pb) // 2
    pw, ph = int((pr - pl) * panel_scale), int((pb - pt) * panel_scale)
    prc = (pcx - pw // 2, pcy - ph // 2 + panel_dy, pcx + pw // 2, pcy + ph // 2 + panel_dy)

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (prc[0] + 10, prc[1] + 18, prc[2] + 10, prc[3] + 18), radius=34, fill=(15, 0, 6, 140)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
    layer = Image.alpha_composite(layer, shadow)

    panel_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel_img)
    pd.rounded_rectangle(prc, radius=34, fill=(*CREAM, panel_alpha))
    border_pulse = int(170 + 60 * math.sin(t * 2.2))
    pd.rounded_rectangle(
        (prc[0] + 12, prc[1] + 12, prc[2] - 12, prc[3] - 12),
        radius=28,
        outline=(*GOLD, border_pulse),
        width=4,
    )
    # animated corner sparks
    for corner in ((prc[0] + 20, prc[1] + 20), (prc[2] - 20, prc[1] + 20), (prc[0] + 20, prc[3] - 20), (prc[2] - 20, prc[3] - 20)):
        spark_a = int(180 * abs(math.sin(t * 3 + corner[0])))
        pd.ellipse((corner[0] - 6, corner[1] - 6, corner[0] + 6, corner[1] + 6), fill=(*GOLD_LIGHT, spark_a))
    layer = Image.alpha_composite(layer, panel_img)
    layer = draw_panel_rich_fill(layer, prc, t, panel_alpha)
    layer = draw_panel_corner_flowers(layer, prc, t)

    if panel_in < 0.05:
        return layer

    content = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(content)
    y = prc[1] + 34

    om_a = anim_alpha(prog, 0.12, 0.35)
    otw, oth = text_size("ॐ", FONTS_CACHE["om"])
    ox = PANEL[0] + (PANEL_W - otw) // 2
    draw.text((ox, y + anim_offset(prog, 0.12, 0.35, 25)), "ॐ", font=FONTS_CACHE["om"], fill=(*GOLD, om_a))
    y += 78

    qa = anim_alpha(prog, 0.14, 0.38)
    y = y + int(anim_offset(prog, 0.14, 0.38, 20))
    for line in wrap_text("Two hearts, one journey, a lifetime of togetherness...", FONTS_CACHE["quote"], PANEL_W - 70):
        tw, th = text_size(line, FONTS_CACHE["quote"])
        draw.text((PANEL[0] + (PANEL_W - tw) // 2, y), line, font=FONTS_CACHE["quote"], fill=(*TEXT_MUTED, qa))
        y += th + 4
    y += 12

    ia = anim_alpha(prog, 0.16, 0.38)
    for line in wrap_text("With the blessings of our families, we cordially invite you to the", FONTS_CACHE["intro"], PANEL_W - 70):
        tw, th = text_size(line, FONTS_CACHE["intro"])
        draw.text((PANEL[0] + (PANEL_W - tw) // 2, y + int(anim_offset(prog, 0.16, 0.38, 18))), line, font=FONTS_CACHE["intro"], fill=(*TEXT_DARK, ia))
        y += th + 3
    y += 8

    hero_top = y
    hero_a = anim_alpha(prog, 0.22, 0.38)
    hero_dy = int(anim_offset(prog, 0.22, 0.38, 45))

    title_bb = draw_text_centered(
        draw, "Ring Ceremony", y + hero_dy, FONTS_CACHE["title"], (*MAROON_LIGHT, hero_a),
    )
    y = title_bb[3] + 4

    sweep_w = int((PANEL_W - 140) * segment_progress(prog, 0.28, 0.48))
    if sweep_w > 0:
        sx = PANEL[0] + (PANEL_W - sweep_w) // 2
        draw.rounded_rectangle((sx, y, sx + sweep_w, y + 4), radius=2, fill=(*GOLD, int(210 * hero_in)))
    y += 12

    of_bb = draw_text_centered(draw, "of", y + hero_dy // 2, FONTS_CACHE["of"], (*TEXT_DARK, hero_a))
    y = of_bb[3] + 2

    n1_bb = draw_text_centered(draw, "Tanya Goel", y + hero_dy // 3, FONTS_CACHE["name"], (*MAROON_LIGHT, hero_a))
    y = n1_bb[3]
    amp_bb = draw_text_centered(draw, "&", y, FONTS_CACHE["amp"], (*GOLD, hero_a))
    y = amp_bb[3]
    n2_bb = draw_text_centered(draw, "Prabhat Goel", y, FONTS_CACHE["name"], (*MAROON_LIGHT, hero_a))
    hero_bottom = n2_bb[3]

    glow_layer = draw_hero_glow(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)), hero_top, hero_bottom, t, hero_in)
    content = Image.alpha_composite(content, glow_layer)
    draw = ImageDraw.Draw(content)

    y = hero_bottom + 12
    ma = anim_alpha(prog, 0.48, 0.35)
    for line in wrap_text(
        "As we begin this beautiful journey of love and togetherness, we would be delighted to have you grace the occasion with your presence and blessings.",
        FONTS_CACHE["msg"], PANEL_W - 60,
    ):
        tw, th = text_size(line, FONTS_CACHE["msg"])
        draw.text((PANEL[0] + (PANEL_W - tw) // 2, y + int(anim_offset(prog, 0.48, 0.35, 15))), line, font=FONTS_CACHE["msg"], fill=(*TEXT_MUTED, ma))
        y += th + 3
    y += 10

    col_w = PANEL_W // 3
    box_y = y
    box_h = 132
    details = [("DATE", "Saturday,\n24 October"), ("TIME", "11:00 AM"), ("VENUE", "The Tonight Rooms\nand Party Hall,\nRailway Road, Hapur")]
    for idx, (label, value) in enumerate(details):
        da = anim_alpha(prog, 0.44 + idx * 0.05, 0.3)
        bx1 = PANEL[0] + col_w * idx + 10
        bx2 = PANEL[0] + col_w * (idx + 1) - 10
        pop = 0.9 + 0.1 * ease_out_elastic(segment_progress(prog, 0.44 + idx * 0.05, 0.58))
        mid_y = box_y + int((1 - pop) * 20)
        draw.rounded_rectangle(
            (bx1, mid_y, bx2, mid_y + box_h),
            radius=14,
            fill=(255, 255, 255, int(da * 0.9)),
            outline=(*GOLD, int(da * 0.85)),
            width=2,
        )
        cx = (bx1 + bx2) // 2
        ltw, _ = text_size(label, FONTS_CACHE["label"])
        draw.text((cx - ltw // 2, mid_y + 10), label, font=FONTS_CACHE["label"], fill=(*MAROON_LIGHT, da))
        vy = mid_y + 40
        for line in value.split("\n"):
            vtw, vth = text_size(line, FONTS_CACHE["detail"])
            draw.text((cx - vtw // 2, vy), line, font=FONTS_CACHE["detail"], fill=(*TEXT_DARK, da))
            vy += 24

    y = box_y + box_h + 10
    ca = anim_alpha(prog, 0.58, 0.35)
    for line in wrap_text("Your presence will make our celebration even more special.", FONTS_CACHE["close"], PANEL_W - 60):
        tw, th = text_size(line, FONTS_CACHE["close"])
        draw.text((PANEL[0] + (PANEL_W - tw) // 2, y), line, font=FONTS_CACHE["close"], fill=(*TEXT_DARK, ca))
        y += th + 3
    y += 6
    stw, sth = text_size("With Love,", FONTS_CACHE["sign"])
    draw.text((PANEL[0] + (PANEL_W - stw) // 2, y), "With Love,", font=FONTS_CACHE["sign"], fill=(*TEXT_MUTED, ca))
    y += sth + 2
    draw_text_centered(draw, "Goel Family", y + 12, FONTS_CACHE["family"], (*MAROON_LIGHT, ca))
    draw_footer_ornaments(draw, prc, t, int(220 * ease_out_cubic(min(1.0, prog * 1.2))))

    layer = Image.alpha_composite(layer, content)
    return layer


def render_single_frame(t: float) -> np.ndarray:
    prog = clamp01(t / DURATION)
    reveal = ease_out_cubic(min(1.0, prog * 1.6))
    intro = segment_progress(prog, 0.0, 0.2)

    frame = STATIC_BACKDROP.copy()
    frame = draw_rotating_mandala(frame, t)
    frame = draw_light_burst(frame, t, intro)
    frame = draw_corner_roses(frame, t)
    frame = draw_hanging_bells(frame, t)
    frame = Image.alpha_composite(frame, draw_invitation_panel(t))
    frame = draw_ambient_fx(frame, t, reveal)

    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(vignette).rectangle((0, 0, WIDTH, HEIGHT), fill=(30, 6, 16, 32))
    frame = Image.alpha_composite(frame, vignette)
    return np.array(frame.convert("RGB"))


def generate_background_music() -> None:
    if BG_MUSIC.exists():
        return
    dur = int(DURATION) + 3
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:duration={dur}",
        "-f", "lavfi", "-i", f"sine=frequency=247:duration={dur}",
        "-f", "lavfi", "-i", f"sine=frequency=294:duration={dur}",
        "-filter_complex",
        f"[0:a][1:a][2:a]amix=inputs=3:duration=longest,volume=0.05,afade=t=in:st=0:d=2.5,afade=t=out:st={int(DURATION)-1}:d=2.5",
        str(BG_MUSIC),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def compress_mobile(source: Path, target: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-vf", "scale=720:1280:flags=lanczos",
            "-c:v", "libx264", "-preset", "slow", "-crf", "27",
            "-maxrate", "2800k", "-bufsize", "5600k",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(target),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def build_video() -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generate_background_music()
    video = VideoClip(lambda t: render_single_frame(t), duration=DURATION).with_fps(FPS)
    audio = AudioFileClip(str(BG_MUSIC)).with_duration(DURATION)
    video = video.with_audio(audio)
    video.write_videofile(
        str(OUTPUT_VIDEO), fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", bitrate="7000k",
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
