#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 data/site_config.yaml 的子类规则为 1557 个项目分配子类（首条命中生效）。
用法:
  python tools/classify.py          # 干跑：打印统计、未命中项、单字规则命中项（人工复核用）
  python tools/classify.py --write  # 另存 data/taxonomy.json
"""
import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "data", "site_config.yaml")
PROJECTS = os.path.join(ROOT, "data", "projects.json")
OUT = os.path.join(ROOT, "data", "taxonomy.json")


def main() -> None:
    cfg = yaml.safe_load(open(CFG, encoding="utf-8"))
    cats = cfg["categories"]
    by_name = {c["name"]: c for c in cats}
    overrides = cfg.get("overrides") or {}
    projects = json.load(open(PROJECTS, encoding="utf-8"))

    counts = {}
    misses = {}
    weak_matches = []  # 单字规则命中（容易误分，需人工复核）
    result = {}

    for p in projects:
        cat = p["category"]
        c = by_name.get(cat)
        hit = None
        hit_rule = None
        ov = overrides.get(p["title"])
        if ov:
            for sc in c["subcats"]:
                if sc["name"] == ov:
                    hit, hit_rule = sc, "（特例表）"
                    break
        if hit is None:
            for sc in c["subcats"]:
                for r in sc["rules"]:
                    if r in p["title"]:
                        hit, hit_rule = sc, r
                        break
                if hit:
                    break
        if hit is None:
            misses.setdefault(cat, []).append(f"{p['num']} {p['title']}")
        elif len(hit_rule) <= 1:
            weak_matches.append(f"{cat} | {p['num']} {p['title']}  <=规则「{hit_rule}」-> {hit['name']}")
        if hit is not None:
            counts.setdefault(cat, {}).setdefault(hit["name"], []).append(p["title"])
            result[p["num"]] = {"title": p["title"], "category": cat, "subcat": hit["name"], "subcat_slug": hit["slug"]}

    total = 0
    for c in cats:
        name = c["name"]
        cc = counts.get(name, {})
        n = sum(len(v) for v in cc.values())
        total += n
        print(f"\n=== {c['roman']} {name}（{n} / {sum(1 for p in projects if p['category'] == name)}）===")
        for sc in c["subcats"]:
            items = cc.get(sc["name"], [])
            samples = "、".join(items[:6])
            print(f"  {sc['name']:　<8} {len(items):>3}  | {samples}")
        ms = misses.get(name, [])
        if ms:
            print("  【未命中】:")
            for m in ms:
                print("     ", m)
    print(f"\n总计命中: {total} / {len(projects)}")

    if weak_matches:
        print(f"\n———— 单字规则命中（{len(weak_matches)} 条，建议人工复核）————")
        for w in weak_matches:
            print("  ", w)

    if "--write" in sys.argv:
        json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\n已写出 {OUT}")


if __name__ == "__main__":
    main()
