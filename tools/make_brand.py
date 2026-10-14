#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成站点标识：朱砂印章 Logo 与 favicon（宣纸 × 朱砂 设计语言）。"""
import os
import random

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets", "brand")

FONT_CANDIDATES = [
    "C:/Windows/Fonts/STZHONGS.TTF",   # 华文中宋
    "C:/Windows/Fonts/msyhbd.ttc",     # 微软雅黑 Bold
    "C:/Windows/Fonts/simhei.ttf",     # 黑体
    "C:/Windows/Fonts/simkai.ttf",     # 楷体
]


def load_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:  # noqa: BLE001
                continue
    return ImageFont.load_default()


def draw_seal(size: int = 512) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * 0.045)
    r = int(size * 0.15)
    # 朱砂章身
    d.rounded_rectangle((pad, pad, size - pad, size - pad), radius=r, fill=(158, 56, 42, 255))
    # 深浅渐变（左下略深）
    grad = Image.new("L", (size, size), 0)
    gd = ImageDraw.Draw(grad)
    gd.ellipse((-size * 0.4, -size * 0.2, size * 1.1, size * 1.2), fill=70)
    dark = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dark.putalpha(grad)
    img = Image.alpha_composite(img, dark)
    d = ImageDraw.Draw(img)
    # 内框
    inner = int(size * 0.115)
    d.rounded_rectangle(
        (pad + inner, pad + inner, size - pad - inner, size - pad - inner),
        radius=int(r * 0.72), outline=(247, 241, 228, 205), width=max(2, int(size * 0.013)),
    )
    # 印章文字
    font = load_font(int(size * 0.50))
    ch = "遗"
    bbox = d.textbbox((0, 0), ch, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), ch,
           font=font, fill=(247, 241, 228, 255))
    # 斑驳做旧
    random.seed(2026)
    px = img.load()
    n = int(size * size * 0.022)
    for _ in range(n):
        x, y = random.randrange(size), random.randrange(size)
        r0, g0, b0, a0 = px[x, y]
        if a0 > 0:
            k = random.uniform(0.86, 1.02)
            px[x, y] = (min(255, int(r0 * k)), min(255, int(g0 * k)), min(255, int(b0 * k)), a0)
    return img


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    seal = draw_seal(512)
    seal.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "logo.png"))
    seal.resize((128, 128), Image.LANCZOS).save(os.path.join(OUT, "logo-128.png"))
    seal.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, "favicon.png"))
    print("brand ->", OUT)


if __name__ == "__main__":
    main()
