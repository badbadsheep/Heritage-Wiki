#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非遗志 · 图像资产生成器
--------------------------------------------------------------------
生成内容：
  A. 图版五式（题名 / 山川 / 纹样 / 工巧 / 名录）
     → docs/assets/img/plates/<id>/1.png ... 5.png
  B. 项目气泡（从门类大图裁切；大图未生成时退回纹样气泡）
     → docs/assets/img/bubbles/items/<id>.png
  C. 门类 / 子类气泡
     → docs/assets/img/bubbles/cat-<slug>.png / <catslug>-<subslug>.png

用法：
  python tools/build_images.py --sample 6          # 抽样 6 个
  python tools/build_images.py --only Ⅷ-7 Ⅶ-16     # 指定编号
  python tools/build_images.py                     # 全量生成
  python tools/build_images.py --bubbles           # 只（重）做气泡
"""
import argparse
import json
import math
import os
import sys

import yaml
from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "docs", "assets", "img")
PLATES = os.path.join(IMG, "plates")
BUBBLES = os.path.join(IMG, "bubbles")
HEROES = os.path.join(IMG, "heroes")
W, H = 1000, 625
ROMAN_IDX = {"Ⅰ": 1, "Ⅱ": 2, "Ⅲ": 3, "Ⅳ": 4, "Ⅴ": 5, "Ⅵ": 6, "Ⅶ": 7, "Ⅷ": 8, "Ⅸ": 9, "Ⅹ": 10}


def load_data():
    projects = json.load(open(os.path.join(ROOT, "data", "projects.json"), encoding="utf-8"))
    tax = json.load(open(os.path.join(ROOT, "data", "taxonomy.json"), encoding="utf-8"))
    cfg = yaml.safe_load(open(os.path.join(ROOT, "data", "site_config.yaml"), encoding="utf-8"))
    return projects, tax, cfg


def item_id(p) -> str:
    return f"{ROMAN_IDX[p['roman']]:02d}-{p['seq']:03d}"


def cat_color(p, cfg):
    for c in cfg["categories"]:
        if c["name"] == p["category"]:
            return tuple(int(c["color"][i:i + 2], 16) for i in (1, 3, 5))
    return S.SEAL


def save_png(img: Image.Image, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.convert("P", palette=Image.ADAPTIVE, colors=256).save(path, optimize=True)


# ================================================================ 五式图版
def _base(p, cfg, key="", noise=2400):
    cc = cat_color(p, cfg)
    img = S.paper((W, H), key=key or p["num"], noise=noise)
    d = ImageDraw.Draw(img, "RGBA")
    return img, d, cc


def _header(d, cc, type_label, p):
    f = S.font("serif", 24)
    S.text_ls(d, (54, 44), f"非 遗 志 · 图 版 · {type_label}", f, S.tint(S.INK_2, 220), ls=4)
    S.draw_seal(d, W - 104, 40, 50, S.CAT_SEAL.get(p["category"], "遗"))
    img = None
    return img


def _footer(d, p):
    f = S.font("serif", 23)
    line = f"国家级非物质文化遗产代表性项目 · {p['num']}"
    S.text_ls(d, (W / 2, H - 52), line, f, S.tint(S.INK_3, 235), ls=6, anchor="ma")


def plate_title(p, cfg) -> Image.Image:
    img, d, cc = _base(p, cfg, key=p["num"] + "t")
    # 背景纹样水印（微旋转）
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm, "RGBA")
    S.draw_motif(wd, p["category"], W / 2, H / 2 - 6, 400, S.tint(cc, 46))
    wm = wm.rotate(-3.5, resample=Image.BICUBIC, center=(W / 2, H / 2))
    img = Image.alpha_composite(img.convert("RGBA"), wm)
    d = ImageDraw.Draw(img, "RGBA")
    S.frame(d, W, H)
    _header(d, cc, "题名", p)
    # 主标题
    title = p["title"]
    if len(title) <= 8:
        f = S.font("serif", 96)
        lines = [title]
    elif len(title) <= 12:
        f = S.font("serif", 76)
        lines = [title]
    else:
        f = S.font("serif", 64)
        lines = S.wrap_cjk(d, title, f, 720)[:2]
    y = 172 if len(lines) == 1 else 150
    for ln in lines:
        S.text_ls(d, (W / 2, y), ln, f, S.tint(S.INK, 245), ls=8, anchor="ma")
        y += f.size + 26
    y += 6
    # 类别 · 批次
    f2 = S.font("serif", 30)
    S.text_ls(d, (W / 2, y), f"{p['category']} · {p['first_batch']}", f2, S.tint(cc, 240), ls=8, anchor="ma")
    y += 54
    # 申报地区（前 3）
    f3 = S.font("kai", 26)
    regs = "、".join(p["regions"][:3]) + ("…" if len(p["regions"]) > 3 else "")
    S.text_ls(d, (W / 2, y), regs, f3, S.tint(S.INK_2, 225), ls=4, anchor="ma")
    _footer(d, p)
    return img.convert("RGB")


def plate_region(p, cfg) -> Image.Image:
    img, d, cc = _base(p, cfg, key=p["num"] + "r")
    # 山水
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay, "RGBA")
    base_y = H - 150
    mounts = [(-60, 300, 210, 132), (170, 420, 150, 96), (640, 980, 240, 150), (860, 1120, 170, 100)]
    for x0, x1, hgt, halfw in [(x0, x1, hgt, halfw) for (x0, x1, hgt, halfw) in mounts]:
        cx = (x0 + x1) / 2
        ld.polygon([(cx - (x1 - x0) / 2, base_y + 26), (cx, base_y - hgt), (cx + (x1 - x0) / 2, base_y + 26)], outline=None)
    # 山用线描更雅：改为三条折线
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay, "RGBA")
    for (x0, x1, hgt, _hw) in mounts:
        cx = (x0 + x1) / 2
        pts = [(x0 + 20, base_y + 30), (cx - (x1 - x0) * 0.22, base_y - hgt * 0.6), (cx, base_y - hgt),
               (cx + (x1 - x0) * 0.24, base_y - hgt * 0.55), (x1 - 20, base_y + 30)]
        ld.line(pts, fill=S.tint(cc, 70), width=4, joint="curve")
    S.draw_waves(ld, 60, base_y + 52, W - 120, S.tint(cc, 60), lw=3, rows=3, amp=8, wave=52)
    img = Image.alpha_composite(img.convert("RGBA"), lay)
    d = ImageDraw.Draw(img, "RGBA")
    S.frame(d, W, H)
    _header(d, cc, "山川", p)
    # 左侧大字（竖排首地域）
    first = p["regions"][0] if p["regions"] else "中国"
    fbig = S.font("serif", 76)
    if len(first) <= 2:
        S.text_v(d, 168, 150, first, fbig, S.tint(S.INK, 240), ls=18)
    else:
        S.text_ls(d, (110, 190), first[:4], S.font("serif", 60), S.tint(S.INK, 240), ls=8)
    f1 = S.font("serif", 24)
    S.text_ls(d, (110, H - 186), "申 报 地 区", f1, S.tint(S.INK_3, 230), ls=6)
    # 右侧地区列（不含左侧大字）
    x0, y0 = 440, 168
    f2 = S.font("kai", 30)
    others = p["regions"][1:]
    for i, r in enumerate(others[:12]):
        cx = x0 + (i // 6) * 240
        cy = y0 + (i % 6) * 52
        d.rectangle((cx, cy + 10, cx + 8, cy + 18), fill=S.tint(cc, 190))
        S.text_ls(d, (cx + 20, cy), r, f2, S.tint(S.INK, 235), ls=2)
    extra = len(others) - 12
    if extra > 0:
        S.text_ls(d, (x0, y0 + 6 * 52), f"…… 另有 {extra} 处", S.font("kai", 24), S.tint(S.INK_3, 230), ls=2)
    # 批次信息
    f3 = S.font("serif", 26)
    S.text_ls(d, (x0, H - 148), f"{'·'.join(p['batches'])} · 子项记录 {p['n_records']} 条", f3, S.tint(cc, 235), ls=4)
    _footer(d, p)
    return img.convert("RGB")


def plate_pattern(p, cfg) -> Image.Image:
    img = S.paper((W, H), key=p["num"] + "p", noise=1800)
    cc = cat_color(p, cfg)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay, "RGBA")
    r = S.rng_of(p["num"] + "pt")
    step = 118
    for gy, y in enumerate(range(60, H - 40, step)):
        for gx, x in enumerate(range(60, W - 40, step)):
            if r.random() < 0.82:
                S.draw_motif(ld, p["category"], x + (step // 2 if gy % 2 else 0), y + step // 2, 64, S.tint(cc, r.randint(34, 64)), lw=2)
    img = Image.alpha_composite(img.convert("RGBA"), lay)
    d = ImageDraw.Draw(img, "RGBA")
    # 中部题名带
    band_y0, band_y1 = H / 2 - 84, H / 2 + 84
    d.rectangle((0, band_y0, W, band_y1), fill=(246, 241, 231, 236))
    d.line((0, band_y0, W, band_y0), fill=S.tint(S.INK, 90), width=2)
    d.line((0, band_y1, W, band_y1), fill=S.tint(S.INK, 90), width=2)
    title = p["title"]
    f = S.fit_font(d, title, "serif", 760, 62, 40)
    S.text_ls(d, (W / 2, band_y0 + 30), title, f, S.tint(S.INK, 246), ls=6, anchor="ma")
    f2 = S.font("serif", 24)
    S.text_ls(d, (W / 2, band_y0 + 34 + f.size + 18), f"{p['category']} · {p['num']}", f2, S.tint(cc, 235), ls=8, anchor="ma")
    S.frame(d, W, H)
    _header(d, cc, "纹样", p)
    _footer(d, p)
    return img.convert("RGB")


def plate_craft(p, cfg) -> Image.Image:
    img, d, cc = _base(p, cfg, key=p["num"] + "c")
    S.frame(d, W, H)
    _header(d, cc, "工巧", p)
    # 左侧圆框 + 意象
    rr = 176
    cx, cy = 330, 318
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=S.tint(cc, 120), width=3)
    d.ellipse((cx - rr + 10, cy - rr + 10, cx + rr - 10, cy + rr - 10), outline=S.tint(cc, 60), width=1)
    S.draw_motif(d, p["category"], cx, cy, 240, S.tint(cc, 200), lw=5)
    # 右侧三字
    words = []
    for c in cfg["categories"]:
        if c["name"] == p["category"]:
            words = c["plate_words"]
    f = S.font("serif", 66)
    y = 148
    for i, wch in enumerate(words[:3]):
        S.text_ls(d, (660, y), wch, f, S.tint(S.INK, 235), ls=14)
        y += f.size + 30
        if i < len(words) - 1:
            S.text_ls(d, (660, y - 22), "·", S.font("serif", 30), S.tint(cc, 220), ls=0)
    f2 = S.font("serif", 24)
    S.text_ls(d, (660, y + 6), "工 巧 之 式", f2, S.tint(S.INK_3, 230), ls=8)
    # 底部名称
    f3 = S.fit_font(d, p["title"], "serif", 680, 36, 24)
    S.text_ls(d, (W / 2, H - 112), p["title"], f3, S.tint(S.INK_2, 240), ls=6, anchor="ma")
    _footer(d, p)
    return img.convert("RGB")


def plate_record(p, cfg) -> Image.Image:
    img, d, cc = _base(p, cfg, key=p["num"] + "n")
    S.frame(d, W, H)
    _header(d, cc, "名录", p)
    # 左：编号
    f = S.font("serif", 112)
    S.text_ls(d, (92, 170), p["num"], f, S.tint(cc, 235), ls=6)
    f2 = S.font("serif", 26)
    S.text_ls(d, (96, 316), "国家级非物质文化遗产", f2, S.tint(S.INK_2, 230), ls=6)
    S.text_ls(d, (96, 356), "代表性项目", f2, S.tint(S.INK_2, 230), ls=6)
    # 竖分隔线
    d.line((520, 150, 520, H - 150), fill=S.tint(S.INK, 70), width=2)
    # 右：名称与数据
    f3 = S.fit_font(d, p["title"], "serif", 380, 54, 36)
    lines = S.wrap_cjk(d, p["title"], f3, 380)[:2]
    yy = 158
    for ln in lines:
        S.text_ls(d, (570, yy), ln, f3, S.tint(S.INK, 244), ls=4)
        yy += f3.size + 16
    rows = [
        ("批 次", "、".join(p["batches"])),
        ("子项记录", f"{p['n_records']} 条"),
        ("申报地区", f"{len(p['regions'])} 处 · " + "、".join(p["regions"][:3]) + ("…" if len(p["regions"]) > 3 else "")),
    ]
    yy = max(yy + 16, 320)
    for label, val in rows:
        S.text_ls(d, (570, yy), label, S.font("serif", 24), S.tint(S.INK_3, 235), ls=4)
        fv = S.fit_font(d, val, "kai", 350, 30, 20)
        S.text_ls(d, (706, yy - 3), val, fv, S.tint(S.INK_2, 240), ls=2)
        d.line((570, yy + 48, 930, yy + 48), fill=S.tint(S.INK, 40), width=1)
        yy += 64
    # 底部回纹
    S.draw_meander(d, 92, H - 118, W - 184, 13, S.tint(cc, 130), lw=2)
    _footer(d, p)
    return img.convert("RGB")


# ================================================================ 气泡
def bubble_from_pattern(cat: str, key: str, size=420, seal_char=None) -> Image.Image:
    img = S.paper((size, size), key=key, noise=900)
    cc = S.CAT_COLORS.get(cat, S.SEAL)
    lay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay, "RGBA")
    r = S.rng_of(key)
    step = 96
    for gy, y in enumerate(range(30, size - 20, step)):
        for gx, x in enumerate(range(30, size - 20, step)):
            if r.random() < 0.75:
                S.draw_motif(ld, cat, x + step // 2 + (step // 2 if gy % 2 else 0), y + step // 2, 52, S.tint(cc, r.randint(30, 54)), lw=2)
    ld.ellipse((22, 22, size - 22, size - 22), outline=S.tint(cc, 150), width=3)
    S.draw_motif(ld, cat, size / 2, size / 2 - 6, 150, S.tint(cc, 190), lw=4)
    img = Image.alpha_composite(img.convert("RGBA"), lay)
    return img.convert("RGB")


def bubble_from_hero(hero_path: str, key: str, size=420) -> Image.Image:
    hero = Image.open(hero_path).convert("RGB")
    w, h = hero.size
    side = int(min(w, h) * 0.92)
    r = S.rng_of(key)
    x0 = r.randint(0, max(0, w - side))
    y0 = r.randint(0, max(0, h - side)) if h - side > 0 else 0
    crop = hero.crop((x0, y0, x0 + side, y0 + side)).resize((size, size), Image.LANCZOS)
    # 提饱和、微降明度，让气泡在纸底上更醒目
    crop = ImageEnhance.Color(crop).enhance(1.30)
    crop = ImageEnhance.Contrast(crop).enhance(1.07)
    crop = ImageEnhance.Brightness(crop).enhance(0.97)
    # 柔和纸罩，边缘更实
    veil = Image.new("RGBA", (size, size), (246, 241, 231, 0))
    vd = ImageDraw.Draw(veil)
    for i in range(6):
        a = int(18 + i * 10)
        off = i * 7
        vd.ellipse((off, off, size - off, size - off), outline=(246, 241, 231, a), width=9)
    crop = Image.alpha_composite(crop.convert("RGBA"), veil)
    return crop.convert("RGB")


# ================================================================ 主流程
def gen_item_images(p, cfg, hero_path=None):
    iid = item_id(p)
    out_dir = os.path.join(PLATES, iid)
    if not os.path.exists(os.path.join(out_dir, "5.png")):
        save_png(plate_title(p, cfg), os.path.join(out_dir, "1.png"))
        save_png(plate_region(p, cfg), os.path.join(out_dir, "2.png"))
        save_png(plate_pattern(p, cfg), os.path.join(out_dir, "3.png"))
        save_png(plate_craft(p, cfg), os.path.join(out_dir, "4.png"))
        save_png(plate_record(p, cfg), os.path.join(out_dir, "5.png"))
    # 气泡
    bub = os.path.join(BUBBLES, "items", f"{iid}.png")
    if not os.path.exists(bub):
        if hero_path and os.path.exists(hero_path):
            img = bubble_from_hero(hero_path, p["num"], size=420)
        else:
            img = bubble_from_pattern(p["category"], p["num"], size=420)
        save_png(img, bub)


def hero_for(p, cfg):
    for c in cfg["categories"]:
        if c["name"] == p["category"]:
            return os.path.join(HEROES, f"{c['slug']}.png")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--bubbles", action="store_true")
    ap.add_argument("--bubbles-only", action="store_true")
    args = ap.parse_args()

    projects, tax, cfg = load_data()
    want = projects
    if args.only:
        want = [p for p in projects if p["num"] in set(args.only)]
    elif args.sample:
        picks = ["Ⅷ-7", "Ⅶ-16", "Ⅱ-28", "Ⅰ-7", "Ⅵ-11", "Ⅹ-1", "Ⅳ-28", "Ⅸ-5", "Ⅲ-27", "Ⅷ-65"][: args.sample]
        want = [p for p in projects if p["num"] in picks]

    only_bubbles = args.bubbles or args.bubbles_only
    n = 0
    for p in want:
        if not only_bubbles:
            gen_item_images(p, cfg, hero_path=hero_for(p, cfg))
        else:
            bub = os.path.join(BUBBLES, "items", f"{item_id(p)}.png")
            hero = hero_for(p, cfg)
            img = bubble_from_hero(hero, p["num"], 420) if hero and os.path.exists(hero) else bubble_from_pattern(p["category"], p["num"], 420)
            save_png(img, bub)
        n += 1
        if n % 50 == 0:
            print(f"  ... {n}/{len(want)}", flush=True)

    # 门类 / 子类气泡
    if not args.only and not args.sample:
        for c in cfg["categories"]:
            hero = os.path.join(HEROES, f"{c['slug']}.png")
            out = os.path.join(BUBBLES, f"cat-{c['slug']}.png")
            if os.path.exists(hero):
                save_png(bubble_from_hero(hero, "cat" + c["slug"], 480), out)
            else:
                save_png(bubble_from_pattern(c["name"], "cat" + c["slug"], 480), out)
            for i, sc in enumerate(c["subcats"]):
                out = os.path.join(BUBBLES, f"{c['slug']}-{sc['slug']}.png")
                if os.path.exists(hero):
                    save_png(bubble_from_hero(hero, "sub" + c["slug"] + sc["slug"], 420), out)
                else:
                    save_png(bubble_from_pattern(c["name"], "sub" + c["slug"] + sc["slug"], 420), out)
    print(f"done: {n} items processed")


if __name__ == "__main__":
    main()
