#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非遗志 · 全量页面生成器
--------------------------------------------------------------------
生成三类页面（均不覆盖已存在的文件，手写页面优先）：
  1. 词条页    docs/中国非遗/<门类>/项目/<名称>.md        （1557 个）
  2. 子类门览  docs/中国非遗/<门类>/<子类>.md             （约 52 个）
  3. 项目名录  docs/中国非遗/<门类>/项目名录.md           （10 个）

用法：python tools/gen_pages.py [--force]
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
CHINA = os.path.join(DOCS, "中国非遗")
ROMAN_IDX = {"Ⅰ": 1, "Ⅱ": 2, "Ⅲ": 3, "Ⅳ": 4, "Ⅴ": 5, "Ⅵ": 6, "Ⅶ": 7, "Ⅷ": 8, "Ⅸ": 9, "Ⅹ": 10}
SAFE_RE = re.compile(r'[\\/:*?"<>|\n\r\t]')


def load():
    projects = json.load(open(os.path.join(ROOT, "data", "projects.json"), encoding="utf-8"))
    tax = json.load(open(os.path.join(ROOT, "data", "taxonomy.json"), encoding="utf-8"))
    cfg = yaml.safe_load(open(os.path.join(ROOT, "data", "site_config.yaml"), encoding="utf-8"))
    return projects, tax, cfg


def safe_name(t: str) -> str:
    return SAFE_RE.sub("·", t).strip()


def item_id(p) -> str:
    return f"{ROMAN_IDX[p['roman']]:02d}-{p['seq']:03d}"


def bubble_label(t: str, cap: int = 9) -> str:
    return t if len(t) <= cap else t[: cap - 1] + "…"


def write(path: str, text: str, force=False) -> bool:
    if os.path.exists(path) and not force:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def item_fname(p) -> str:
    """词条文件名；同名项目（如两个「湘剧」）附加编号区分。"""
    t = p["title"]
    if sum(1 for q in all_projects if q["title"] == t) > 1:
        return safe_name(f"{t}（{p['num']}）") + ".md"
    return safe_name(t) + ".md"


def clean_content(t: str) -> str:
    if not t:
        return ""
    t = t.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    lines = [ln.strip() for ln in t.split("\n")]
    lines = [ln for ln in lines if ln]
    if lines and lines[0].startswith("申报地区或单位"):
        lines = lines[1:]
    return "\n\n".join(lines)


# ------------------------------------------------------------------ 词条页
def page_item(p, tax, cfg, force=False) -> bool:
    c = cfg_by_name(cfg, p["category"])
    cat_dir = c["dir"]
    slug = c["slug"]
    tc = tax[p["num"]]
    subcat, subcat_slug = tc["subcat"], tc["subcat_slug"]
    title = p["title"]
    fn = os.path.join(CHINA, cat_dir, "项目", item_fname(p))
    if os.path.exists(fn) and not force:
        return False
    iid = item_id(p)
    P = f"/assets/img/plates/{iid}"

    # 同级（同子类）条目
    siblings = [q for q in all_projects if tax[q["num"]]["subcat"] == subcat and q["num"] != p["num"]]
    sib_html = "".join(
        f'<a class="chip" href="../{safe_name(q["title"])}/">{q["title"]}</a>' for q in siblings[:10]
    )
    more = f'<a class="chip" href="../../{safe_name(subcat)}/">……全部 {len(siblings) + 1} 项</a>' if siblings else ""

    # 子项表
    rows = []
    for rec in p["records"]:
        kind = "新增" if rec["cate"] == "新增项目" else "扩展"
        rows.append(f"| {rec['title']} | {rec['province'] or rec['unit']} | {rec['batch']}（{rec['year']}） | {kind} | {rec['protect_unit'] or '—'} |")
    table = "\n".join(rows)

    content = clean_content(p["content_best"])
    content_md = content if content else "（官方简介暂缺，欢迎补充。）"

    # 深度专题叠加：若存在 data/featured/<编号>.md，用其正文替换「项目简介」区
    feat = None
    feat_path = os.path.join(ROOT, "data", "featured", f"{p['num']}.md")
    if os.path.exists(feat_path):
        raw = open(feat_path, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if m:
            fm = yaml.safe_load(m.group(1)) or {}
            feat = {"fm": fm, "body": m.group(2).strip()}
    SEAL = {"民间文学": "文", "传统音乐": "乐", "传统舞蹈": "舞", "传统戏剧": "戏", "曲艺": "曲",
            "传统体育、游艺与杂技": "武", "传统美术": "画", "传统技艺": "工", "传统医药": "医", "民俗": "俗"}

    f = []
    f.append("---")
    f.append(f"title: {title}")
    f.append(f"description: {p['category']}国家级非物质文化遗产代表性项目（{p['num']}），申报地区：{'、'.join(p['regions'][:4])}")
    f.append("---")
    f.append("")
    f.append(f'<div class="theme theme--{slug}" markdown="1">')
    if feat:
        hero_class = feat["fm"].get("hero_class") or f"hero--{slug}"
        kicker = feat["fm"].get("kicker") or f"{p['category']} · {p['num']}"
        sub = feat["fm"].get("sub", "")
        chips = [c.strip() for c in str(feat["fm"].get("chips", "")).split("|") if c.strip()]
        f.append(f'<div class="hero {hero_class}">')
        f.append(f'  <div class="hero__seal">{SEAL.get(p["category"], "遗")}</div>')
        f.append('  <div class="hero__body">')
        f.append(f'    <p class="hero__kicker">{kicker}</p>')
        f.append(f'    <h1 class="hero__title">{title}</h1>')
        if sub:
            f.append(f'    <p class="hero__sub">{sub}</p>')
        if chips:
            f.append('    <div class="hero__meta">' + "".join(f'<span class="chip{" chip--red" if i == len(chips) - 1 else ""}">{c}</span>' for i, c in enumerate(chips)) + "</div>")
        f.append("  </div>")
        f.append("</div>")
    else:
        f.append(f'<div class="hero hero--slim hero--{slug}">')
        f.append('  <div class="hero__body">')
        f.append(f'    <p class="hero__kicker">{p["category"]} · {p["num"]}</p>')
        f.append("  </div>")
        f.append("</div>")
    f.append("")
    f.append('<nav class="cat-rail">')
    f.append(f'  <span class="cat-rail__path"><a href="../../../">中国非遗</a> › <a href="../../">{p["category"]}</a> › <a href="../../{safe_name(subcat)}/">{subcat}</a></span>')
    f.append('  <span class="cat-rail__label">同子类</span>')
    f.append(f"  {sib_html}{more}")
    f.append("</nav>")
    f.append("")
    if not feat:
        f.append(f"# {title}")
        f.append("")
    f.append(f'!!! info "条目一览"')
    f.append(f"    | 项目编号 | 类　别 | 首批公布 | 申报地区 | 子项记录 |")
    f.append(f"    | :--: | :--: | :--: | :-- | :--: |")
    f.append(f"    | {p['num']} | {p['category']} | {p['first_batch']} | {'、'.join(p['regions'][:5])}{'…' if len(p['regions']) > 5 else ''} | {p['n_records']} 条 |")
    f.append("")
    f.append('<div class="plate-grid">')
    f.append(f'  <figure class="plate"><img src="{P}/1.png" alt="{title}·题名图版"><figcaption>图版一 · 题名</figcaption></figure>')
    f.append(f'  <figure class="plate"><img src="{P}/3.png" alt="{title}·纹样图版"><figcaption>图版二 · 纹样</figcaption></figure>')
    f.append("</div>")
    f.append("")
    if feat:
        f.append(feat["body"])
        f.append("")
        f.append('<figure class="plate"><img src="' + P + '/2.png" alt="' + title + '·山川图版"><figcaption>图版三 · 山川</figcaption></figure>')
    else:
        f.append("## 项目简介")
        f.append("")
        if content:
            for para in content_md.split("\n\n"):
                para = para.strip()
                if para:
                    f.append(para)
                    f.append("")
            f.append('*〔以上简介整编自项目申报资料与官方名录文本〕*')
        else:
            f.append("（官方简介暂缺，欢迎补充。）")
        f.append("")
        f.append(f'<figure class="plate"><img src="{P}/2.png" alt="{title}·山川图版"><figcaption>图版三 · 山川</figcaption></figure>')
    f.append("")
    f.append("## 子项一览")
    f.append("")
    f.append(f"本项自国务院公布名录中收录 **{p['n_records']} 条子项记录**（含扩展项目）：")
    f.append("")
    f.append("| 子项名称 | 申报地区或单位 | 公布批次 | 类型 | 保护单位 |")
    f.append("| :-- | :-- | :--: | :--: | :-- |")
    f.append(table)
    f.append("")
    f.append('<div class="plate-grid">')
    f.append(f'  <figure class="plate"><img src="{P}/4.png" alt="{title}·工巧图版"><figcaption>图版四 · 工巧</figcaption></figure>')
    f.append(f'  <figure class="plate"><img src="{P}/5.png" alt="{title}·名录图版"><figcaption>图版五 · 名录</figcaption></figure>')
    f.append("</div>")
    f.append("")
    f.append("---")
    f.append("")
    if feat:
        src = feat["fm"].get("sources")
        if src:
            f.append(f'<p style="text-align:center;color:var(--ink-3);font-size:.74rem">资料来源：{src}</p>')
        f.append(f'<p style="text-align:center;color:var(--ink-3);font-size:.8rem">本词条为深度专题 ｜ <a href="../../{safe_name(subcat)}/">回到「{subcat}」门览</a> ｜ <a href="../../项目名录/">本门类项目名录</a></p>')
    else:
        f.append(f'<p style="text-align:center;color:var(--ink-3);font-size:.8rem">本词条为名录档案 ｜ <a href="../../{safe_name(subcat)}/">回到「{subcat}」门览</a> ｜ <a href="../../项目名录/">本门类项目名录</a> ｜ 欢迎按「源流 · 形制 · 工巧 · 符号 · 守望」体例续写</p>')
    f.append("</div>")
    f.append("")
    return write(fn, "\n".join(f), force)


def cfg_by_name(cfg, name):
    for c in cfg["categories"]:
        if c["name"] == name:
            return c
    raise KeyError(name)


# ------------------------------------------------------------------ 子类门览页
def page_subcat(cfg, cat, sc, items, tax, force=False) -> bool:
    fn = os.path.join(CHINA, cat["dir"], safe_name(sc["name"]) + ".md")
    if os.path.exists(fn) and not force:
        return False
    slug = cat["slug"]
    f = []
    f.append("---")
    f.append(f"title: {sc['name']}")
    f.append(f"description: {cat['name']} · {sc['name']} 门览，共 {len(items)} 项国家级非遗代表性项目")
    f.append("---")
    f.append("")
    f.append(f'<div class="theme theme--{slug}" markdown="1">')
    f.append(f'<div class="hero hero--slim hero--{slug}">')
    f.append('  <div class="hero__body">')
    f.append(f'    <p class="hero__kicker">{cat["name"]} · 门 类 导 览</p>')
    f.append("  </div>")
    f.append("</div>")
    f.append("")
    f.append('<nav class="cat-rail">')
    f.append(f'  <span class="cat-rail__path"><a href="../../">中国非遗</a> › <a href="../">{cat["name"]}</a> › {sc["name"]}</span>')
    f.append('  <span class="cat-rail__label">本门类其他导览</span>')
    others = "".join(f'<a class="chip" href="../{safe_name(s["name"])}/">{s["name"]}</a>' for s in cat["subcats"] if s["slug"] != sc["slug"])
    f.append(f"  {others}")
    f.append("</nav>")
    f.append("")
    f.append(f"# {sc['name']}")
    f.append("")
    f.append(f'<p class="lede">「{cat["name"]}」之「{sc["name"]}」，本览共收录国家级代表性项目 <b>{len(items)}</b> 项。点开任一气泡，即达该项目的图文词条。</p>')
    f.append("")
    f.append('<div class="bubble-grid">')
    for p in items:
        iid = item_id(p)
        f.append(f'  <a class="bubble bubble--sm" href="../项目/{item_fname(p)[:-3]}/" title="{p["title"]}" style="--bg:url(\'/assets/img/bubbles/items/{iid}.png\')"><span class="bubble__name">{bubble_label(p["title"])}</span></a>')
    f.append("</div>")
    f.append("")
    f.append("## 项目明细")
    f.append("")
    f.append("| 编号 | 项目名称 | 申报地区 | 首批公布 | 子项 |")
    f.append("| :--: | :-- | :-- | :--: | :--: |")
    for p in items:
        f.append(f'| {p["num"]} | [{p["title"]}](../项目/{item_fname(p)[:-3]}/) | {"、".join(p["regions"][:4])}{"…" if len(p["regions"]) > 4 else ""} | {p["first_batch"]} | {p["n_records"]} |')
    f.append("")
    f.append(f'<p style="text-align:center;color:var(--ink-3);font-size:.8rem"><a href="../">← 返回「{cat["name"]}」门类页</a> ｜ <a href="../项目名录/">本门类全部项目名录</a></p>')
    f.append("</div>")
    f.append("")
    return write(fn, "\n".join(f), force)


# ------------------------------------------------------------------ 名录页
def page_catalog(cfg, cat, groups, tax, force=False) -> bool:
    fn = os.path.join(CHINA, cat["dir"], "项目名录.md")
    if os.path.exists(fn) and not force:
        return False
    slug = cat["slug"]
    n_items = sum(len(v) for v in groups.values())
    n_rec = sum(p["n_records"] for v in groups.values() for p in v)
    f = []
    f.append("---")
    f.append(f"title: {cat['name']} · 项目名录")
    f.append("---")
    f.append("")
    f.append(f'<div class="theme theme--{slug}" markdown="1">')
    f.append(f'<div class="hero hero--slim hero--{slug}">')
    f.append('  <div class="hero__body">')
    f.append(f'    <p class="hero__kicker">{cat["name"]} · 项 目 名 录</p>')
    f.append("  </div>")
    f.append("</div>")
    f.append("")
    f.append('<nav class="cat-rail">')
    f.append(f'  <span class="cat-rail__path"><a href="../../">中国非遗</a> › <a href="../">{cat["name"]}</a> › 项目名录</span>')
    f.append("</nav>")
    f.append("")
    f.append(f"# {cat['name']} · 项目名录")
    f.append("")
    f.append(f'<p class="lede">本门类全量收录国家级非物质文化遗产代表性项目 <b>{n_items}</b> 项（子项记录 <b>{n_rec}</b> 条）。点项目名称进入词条。</p>')
    f.append("")
    for sc in cat["subcats"]:
        items = groups.get(sc["name"], [])
        if not items:
            continue
        f.append(f'## <a href="../{safe_name(sc["name"])}/">{sc["name"]}</a>（{len(items)} 项）')
        f.append("")
        f.append("| 编号 | 项目名称 | 申报地区 | 批次 | 子项 |")
        f.append("| :--: | :-- | :-- | :--: | :--: |")
        for p in items:
            batches = "、".join(b.replace("第", "").replace("批", "") for b in p["batches"])
            f.append(f'| {p["num"]} | [{p["title"]}](../项目/{item_fname(p)[:-3]}/) | {"、".join(p["regions"][:4])}{"…" if len(p["regions"]) > 4 else ""} | {batches} | {p["n_records"]} |')
        f.append("")
    f.append(f'<p style="text-align:center;color:var(--ink-3);font-size:.8rem"><a href="../">← 返回「{cat["name"]}」门类页</a></p>')
    f.append("</div>")
    f.append("")
    return write(fn, "\n".join(f), force)


# ------------------------------------------------------------------ main
all_projects = []
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--nums", nargs="*", default=None, help="仅重新生成指定编号的项目页")
    args = ap.parse_args()

    projects, tax, cfg = load()
    all_projects = projects
    by_cat = defaultdict(list)
    for p in projects:
        by_cat[p["category"]].append(p)

    if args.nums:
        want = set(args.nums)
        n = 0
        for p in projects:
            if p["num"] in want and page_item(p, tax, cfg, True):
                n += 1
        print(f"重新生成 {n} 个词条")
        sys.exit(0)

    n_item = n_sub = n_cat = 0
    for c in cfg["categories"]:
        cat_items = by_cat[c["name"]]
        groups = defaultdict(list)
        for p in cat_items:
            groups[tax[p["num"]]["subcat"]].append(p)
        # 词条
        for p in cat_items:
            if page_item(p, tax, cfg, args.force):
                n_item += 1
        # 子类
        for sc in c["subcats"]:
            items = sorted(groups.get(sc["name"], []), key=lambda q: q["seq"])
            if items and page_subcat(c, c_note := cfg_by_name(cfg, c["name"]), sc, items, tax, args.force):
                n_sub += 1
        # 名录
        if page_catalog(c, c, groups, tax, args.force):
            n_cat += 1
        print(f"  {c['roman']} {c['name']}: {len(cat_items)} 项", flush=True)

    print(f"\n完成：新增词条 {n_item} 个 · 子类门览 {n_sub} 个 · 名录页 {n_cat} 个")
