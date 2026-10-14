#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非遗志 · 图版设计系统（PIL）
--------------------------------------------------------------------
设计语言：宣纸 × 墨线 × 朱砂印 × 门类色谱
图版五式：题名（扉页）· 山川（地域）· 纹样（pattern）· 工巧（意象）· 名录（数据）
被 tools/build_images.py 调用。
"""
import hashlib
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- 字体
FONT_DIR = "C:/Windows/Fonts/"
F_SERIF = ["STZHONGS.TTF", "simsun.ttc", "msyh.ttc"]        # 华文中宋 → 宋体
F_KAI = ["STKAITI.TTF", "simkai.ttf", "STZHONGS.TTF"]       # 华文楷体 → 楷体
F_HEI = ["simhei.ttf", "msyhbd.ttc", "msyh.ttc"]            # 黑体
_FONT_CACHE = {}


def font(family: str, size: int) -> ImageFont.FreeTypeFont:
    key = (family, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    cands = {"serif": F_SERIF, "kai": F_KAI, "hei": F_HEI}[family]
    for name in cands:
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size, index=0)
                _FONT_CACHE[key] = f
                return f
            except Exception:  # noqa: BLE001
                continue
    f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f

# ---------------------------------------------------------------- 色板
PAPER = (246, 241, 231)
PAPER_D = (236, 228, 212)
INK = (43, 38, 32)
INK_2 = (93, 86, 74)
INK_3 = (142, 132, 113)
SEAL = (160, 58, 44)
CREAM = (247, 241, 228)

CAT_COLORS = {
    "民间文学": (74, 101, 145),
    "传统音乐": (63, 122, 114),
    "传统舞蹈": (166, 74, 92),
    "传统戏剧": (140, 58, 51),
    "曲艺": (156, 106, 52),
    "传统体育、游艺与杂技": (86, 122, 78),
    "传统美术": (176, 131, 39),
    "传统技艺": (70, 86, 107),
    "传统医药": (109, 124, 62),
    "民俗": (158, 53, 39),
}

CAT_SEAL = {
    "民间文学": "文", "传统音乐": "乐", "传统舞蹈": "舞", "传统戏剧": "戏", "曲艺": "曲",
    "传统体育、游艺与杂技": "武", "传统美术": "画", "传统技艺": "工", "传统医药": "医", "民俗": "俗",
}


def seed_of(key: str) -> int:
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)


def rng_of(key: str) -> random.Random:
    return random.Random(seed_of(key))


def tint(color, alpha):
    return (color[0], color[1], color[2], alpha)


# ---------------------------------------------------------------- 纸底
def paper(size, key="", noise=2600) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    r = rng_of(key or "paper")
    for _ in range(noise):
        x, y = r.randrange(w), r.randrange(h)
        v = r.choice([(0, 0, 0, r.randint(3, 8)), (255, 255, 255, r.randint(4, 10))])
        d.point((x, y), fill=v)
    # 纸筋（细短纤维）
    for _ in range(int(noise * 0.05)):
        x, y = r.randrange(w), r.randrange(h)
        ln = r.randint(6, 22)
        if r.random() < 0.5:
            d.line((x, y, x + ln, y), fill=(0, 0, 0, 5))
        else:
            d.line((x, y, x, y + ln), fill=(255, 255, 255, 6))
    # 四边微暗（vignette）
    v = Image.new("L", size, 0)
    vd = ImageDraw.Draw(v)
    m = 46
    vd.rectangle((0, 0, w - 1, h - 1), outline=46, width=m)
    v = v.filter(ImageFilter.GaussianBlur(38))
    dark = Image.new("RGB", size, (120, 104, 80))
    img = Image.composite(dark, img, v.point(lambda p: int(p * 0.34)))
    return img


# ---------------------------------------------------------------- 纹样 / 笔画
def draw_meander(d: ImageDraw.ImageDraw, x, y, length, unit, color, lw=3, vertical=False):
    """回纹（雷纹）连续带。"""
    n = max(1, int(length // (unit * 2)))
    for i in range(n):
        bx = x + i * unit * 2
        if not vertical:
            d.line((bx, y + unit, bx, y), fill=color, width=lw)
            d.line((bx, y, bx + unit, y), fill=color, width=lw)
            d.line((bx + unit, y, bx + unit, y + unit * 0.62), fill=color, width=lw)
            d.line((bx + unit, y + unit * 0.62, bx + unit * 0.42, y + unit * 0.62), fill=color, width=lw)
            d.line((bx + unit * 0.42, y + unit * 0.62, bx + unit * 0.42, y + unit * 0.3), fill=color, width=lw)
        else:
            by = y + i * unit * 2
            d.line((x, by, x + unit, by), fill=color, width=lw)
            d.line((x + unit, by, x + unit, by + unit), fill=color, width=lw)
            d.line((x + unit, by + unit, x + unit * 0.38, by + unit), fill=color, width=lw)
            d.line((x + unit * 0.38, by + unit, x + unit * 0.38, by + unit * 0.62), fill=color, width=lw)


def draw_clouds(d, x, y, w, color, lw=3, rows=2):
    """云纹：一行圆弧卷云。"""
    for r_ in range(rows):
        yy = y + r_ * 46
        unit = 88
        n = max(1, int(w // unit))
        for i in range(n + 1):
            bx = x + i * unit
            d.arc((bx, yy, bx + unit * 0.9, yy + unit * 0.9), 180, 360, fill=color, width=lw)
            d.arc((bx + unit * 0.3, yy + unit * 0.22, bx + unit * 0.72, yy + unit * 0.68), 180, 340, fill=color, width=lw)


def draw_waves(d, x, y, w, color, lw=3, rows=3, amp=9, wave=46):
    """水波纹。"""
    for r_ in range(rows):
        yy = y + r_ * 24
        pts = []
        for i in range(0, int(w) + wave, 4):
            pts.append((x + i, yy + amp * math.sin(i / wave * math.pi * 2)))
        d.line(pts, fill=color, width=lw)


# ---------------------------------------------------------------- 门类意象纹
def draw_motif(d, cat, cx, cy, size, color, lw=None):
    """十门类意象（线描）。size 为外接尺寸。"""
    lw = lw or max(3, int(size * 0.02))
    s = size
    if cat == "民间文学":  # 卷轴
        w = s * 0.62
        h = s * 0.78
        d.rounded_rectangle((cx - w / 2 - 10, cy - h / 2, cx - w / 2 + 8, cy + h / 2), radius=8, outline=color, width=lw)
        d.rounded_rectangle((cx + w / 2 - 8, cy - h / 2, cx + w / 2 + 10, cy + h / 2), radius=8, outline=color, width=lw)
        for i in range(5):
            yy = cy - h / 2 + h * (0.18 + i * 0.16)
            d.line((cx - w / 2 + 26, yy, cx + w / 2 - 26 - (18 if i % 2 else 0), yy), fill=color, width=max(2, lw - 2))
    elif cat == "传统音乐":  # 琴弦
        w = s * 0.8
        for i in range(5):
            yy = cy - s * 0.22 + i * s * 0.11
            d.line((cx - w / 2, yy, cx + w / 2, yy - 4), fill=color, width=max(2, lw - 2))
        d.ellipse((cx - s * 0.16, cy + s * 0.1, cx + s * 0.16, cy + s * 0.34), outline=color, width=lw)
        d.line((cx - w / 2 - 8, cy - s * 0.26, cx - w / 2 - 8, cy + s * 0.3), fill=color, width=lw + 1)
        d.line((cx + w / 2 + 8, cy - s * 0.26, cx + w / 2 + 8, cy + s * 0.3), fill=color, width=lw + 1)
    elif cat == "传统舞蹈":  # 飘带
        for k, (off, amp) in enumerate([(-0.28, 0.3), (0.0, 0.42), (0.28, 0.34)]):
            pts = []
            for i in range(0, int(s * 0.86), 6):
                t = i / (s * 0.86)
                yy = cy + off * s + amp * s * 0.5 * math.sin(t * math.pi * 1.6 + k)
                pts.append((cx - s * 0.43 + i, yy))
            d.line(pts, fill=color, width=max(3, lw - k))
    elif cat == "传统戏剧":  # 脸谱
        R = s * 0.42
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=color, width=lw)
        for sx in (-1, 1):
            d.arc((cx + sx * R * 0.52 - R * 0.26, cy - R * 0.38, cx + sx * R * 0.52 + R * 0.26, cy - R * 0.38 + R * 0.5),
                  200 if sx < 0 else 340, 340 if sx < 0 else 120, fill=color, width=lw)
        d.line((cx, cy - R * 0.9, cx, cy + R * 0.12), fill=color, width=lw - 1)
        d.arc((cx - R * 0.3, cy + R * 0.08, cx + R * 0.3, cy + R * 0.62), 20, 160, fill=color, width=lw)
        d.line((cx - R * 1.05, cy, cx - R * 0.86, cy), fill=color, width=lw)
        d.line((cx + R * 0.86, cy, cx + R * 1.05, cy), fill=color, width=lw)
    elif cat == "曲艺":  # 醒木与扇
        d.rounded_rectangle((cx - s * 0.4, cy + s * 0.16, cx - s * 0.02, cy + s * 0.34), radius=6, outline=color, width=lw)
        d.arc((cx - s * 0.12, cy - s * 0.44, cx + s * 0.62, cy + s * 0.3), 180, 360, fill=color, width=lw)
        for i in range(4):
            a0 = math.radians(180 + 20 * (i + 1))
            x1 = cx + s * 0.25 + math.cos(a0) * s * 0.36
            y1 = cy - s * 0.07 + math.sin(a0) * s * 0.36
            d.line((cx + s * 0.25, cy - s * 0.22, x1, y1), fill=color, width=max(2, lw - 2))
    elif cat == "传统体育、游艺与杂技":  # 靶环与器械
        for k, r_ in enumerate([0.17, 0.3, 0.42]):
            d.ellipse((cx - s * r_, cy - s * r_, cx + s * r_, cy + s * r_), outline=color, width=max(2, lw - k))
        d.line((cx - s * 0.52, cy + s * 0.5, cx + s * 0.5, cy - s * 0.5), fill=color, width=lw + 1)
    elif cat == "传统美术":  # 剪刀
        cxx, cyy = cx, cy + s * 0.06
        d.line((cxx - s * 0.3, cyy + s * 0.38, cxx + s * 0.34, cyy - s * 0.32), fill=color, width=lw + 1)
        d.line((cxx + s * 0.3, cyy + s * 0.38, cxx - s * 0.05, cyy - s * 0.05), fill=color, width=lw + 1)
        d.line((cxx - s * 0.3, cyy + s * 0.38, cxx - s * 0.05, cyy - s * 0.05), fill=color, width=lw + 1)
        r1 = s * 0.1
        d.ellipse((cxx - s * 0.3 - r1, cyy + s * 0.38 - r1, cxx - s * 0.3 + r1, cyy + s * 0.38 + r1), outline=color, width=lw - 2)
        d.ellipse((cxx + s * 0.3 - r1, cyy + s * 0.38 - r1, cxx + s * 0.3 + r1, cyy + s * 0.38 + r1), outline=color, width=lw - 2)
        d.arc((cxx + s * 0.02, cyy - s * 0.46, cxx + s * 0.5, cyy - s * 0.02), 90, 300, fill=color, width=lw)
    elif cat == "传统技艺":  # 瓶与轮
        d.arc((cx - s * 0.1, cy - s * 0.46, cx + s * 0.1, cy - s * 0.3), 0, 180, fill=color, width=lw)
        d.line((cx - s * 0.1, cy - s * 0.38, cx - s * 0.1, cy - s * 0.3), fill=color, width=lw)
        d.line((cx + s * 0.1, cy - s * 0.38, cx + s * 0.1, cy - s * 0.3), fill=color, width=lw)
        pts = [(cx - s * 0.1, cy - s * 0.3), (cx - s * 0.3, cy - s * 0.08), (cx - s * 0.3, cy + s * 0.3)]
        d.line(pts + [(cx - s * 0.18, cy + s * 0.42)], fill=color, width=lw)
        d.line([(cx + s * 0.1, cy - s * 0.3), (cx + s * 0.3, cy - s * 0.08), (cx + s * 0.3, cy + s * 0.3), (cx + s * 0.18, cy + s * 0.42)], fill=color, width=lw)
        d.line((cx - s * 0.18, cy + s * 0.42, cx + s * 0.18, cy + s * 0.42), fill=color, width=lw)
        d.ellipse((cx - s * 0.5, cy + s * 0.3, cx + s * 0.5, cy + s * 0.56), outline=color, width=max(2, lw - 1))
    elif cat == "传统医药":  # 葫芦与针
        d.ellipse((cx - s * 0.34, cy - s * 0.02, cx + s * 0.34, cy + s * 0.5), outline=color, width=lw)
        d.ellipse((cx - s * 0.2, cy - s * 0.44, cx + s * 0.2, cy), outline=color, width=lw)
        d.line((cx - s * 0.12, cy, cx + s * 0.12, cy), fill=color, width=lw - 2)
        d.line((cx + s * 0.52, cy - s * 0.5, cx + s * 0.52, cy - s * 0.18), fill=color, width=max(2, lw - 1))
        d.line((cx + s * 0.52, cy - s * 0.18, cx + s * 0.44, cy - s * 0.3), fill=color, width=max(2, lw - 1))
    elif cat == "民俗":  # 灯笼
        w = s * 0.56
        h = s * 0.6
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=int(w * 0.46), outline=color, width=lw)
        for i in range(4):
            xx = cx - w / 2 + w * (0.2 + i * 0.2)
            d.arc((xx - w * 0.1, cy - h / 2, xx + w * 0.1, cy + h / 2), 0, 360, fill=color, width=max(2, lw - 2))
        d.line((cx - w * 0.22, cy - h / 2, cx - w * 0.22, cy + h / 2), fill=color, width=max(2, lw - 2))
        d.line((cx + w * 0.22, cy - h / 2, cx + w * 0.22, cy + h / 2), fill=color, width=max(2, lw - 2))
        d.line((cx, cy + h / 2, cx, cy + h / 2 + s * 0.16), fill=color, width=lw - 1)
        d.line((cx - s * 0.05, cy + h / 2 + s * 0.16, cx + s * 0.05, cy + h / 2 + s * 0.16), fill=color, width=lw - 1)


def draw_seal(d, x, y, size, char, fill=SEAL, fg=CREAM):
    r = int(size * 0.2)
    d.rounded_rectangle((x, y, x + size, y + size), radius=r, fill=fill)
    d.rounded_rectangle((x + 4, y + 4, x + size - 4, y + size - 4), radius=max(2, r - 3), outline=tint(fg, 200), width=max(2, int(size * 0.05)))
    f = font("serif", int(size * 0.56))
    bbox = d.textbbox((0, 0), char, font=f)
    d.text((x + (size - bbox[2] + bbox[0]) / 2 - bbox[0], y + (size - bbox[3] + bbox[1]) / 2 - bbox[1]), char, font=f, fill=fg)


# ---------------------------------------------------------------- 文字工具
def text_ls(d, xy, s, f, fill, ls=0, anchor="la"):
    """带字距的文字。anchor: la(默认) / ma(水平居中)"""
    total = 0
    widths = []
    for ch in s:
        w = d.textlength(ch, font=f)
        widths.append(w)
        total += w + ls
    total -= ls
    x, y = xy
    if anchor == "ma":
        x -= total / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + ls
    return total


def text_v(d, x, y, s, f, fill, ls=6, align="center"):
    """竖排文字（每字符下移）。"""
    for ch in s:
        w = d.textlength(ch, font=f)
        xx = x - (w / 2 if align == "center" else 0)
        d.text((xx, y), ch, font=f, fill=fill)
        y += f.size + ls
    return y


def fit_font(d, s, family, max_w, start, min_size=20):
    size = start
    while size > min_size:
        f = font(family, size)
        if d.textlength(s, font=f) <= max_w:
            return f
        size -= 2
    return font(family, min_size)


def wrap_cjk(d, s, f, max_w):
    lines, cur = [], ""
    for ch in s:
        if d.textlength(cur + ch, font=f) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- 版面杂项
def frame(d, w, h, color_ink=INK, m=26, lw=2):
    d.rectangle((m, m, w - m, h - m), outline=tint(color_ink, 130), width=lw)
    d.rectangle((m + 12, m + 12, w - m - 12, h - m - 12), outline=tint(color_ink, 70), width=1)
    # 四角短线
    c = 22
    for (cx, cy, sx, sy) in [(m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)]:
        d.line((cx + sx * 12, cy, cx + sx * (12 + c), cy), fill=tint(color_ink, 150), width=lw)
        d.line((cx, cy + sy * 12, cx, cy + sy * (12 + c)), fill=tint(color_ink, 150), width=lw)


def footer(d, w, h, left_text, right_text=""):
    f = font("serif", 22)
    text_ls(d, (52, h - 54), "非 遗 志", f, tint(INK_2, 230), ls=2)
    text_ls(d, (w - 52 - d.textlength(right_text, font=f) - 8 * len(right_text), h - 54), right_text, f, tint(INK_3, 230), ls=8)
