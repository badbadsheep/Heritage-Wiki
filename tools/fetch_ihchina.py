#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从「中国非物质文化遗产网 · 中国非物质文化遗产数字博物馆」(ihchina.cn) 抓取
国家级非物质文化遗产代表性项目名录全量数据（五批主项目 + 扩展项目，共 3610 条记录）。

用法：python tools/fetch_ihchina.py
输出：data/raw/ihchina_projects.json
"""
import json
import os
import time
import urllib.parse
import urllib.request

BASE = "https://www.ihchina.cn/getProject.html"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "raw")
LIMIT = 500  # 官方接口支持的最大分页量（已实测）


def fetch_page(page: int, limit: int = LIMIT) -> dict:
    qs = urllib.parse.urlencode({
        "province": "", "rx_time": "", "type": "", "cate": "",
        "keywords": "", "category_id": "16", "limit": str(limit), "p": str(page),
    })
    url = BASE + "?" + qs
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://www.ihchina.cn/project.html",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    })
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  [retry {attempt + 1}/4] page {page}: {e}", flush=True)
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"page {page} failed: {last_err}")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    all_rows: list[dict] = []
    page = 1
    total = None
    while True:
        d = fetch_page(page)
        rows = d.get("list") or []
        total = int(d.get("count") or 0)
        all_rows.extend(rows)
        print(f"page {page}/{((total or 1) + LIMIT - 1) // LIMIT}: +{len(rows)} -> {len(all_rows)}/{total}", flush=True)
        if not rows or len(all_rows) >= (total or 0):
            break
        page += 1
        time.sleep(0.4)

    seen = set()
    uniq = []
    for row in all_rows:
        rid = str(row.get("id"))
        if rid not in seen:
            seen.add(rid)
            uniq.append(row)

    out = os.path.join(OUT_DIR, "ihchina_projects.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=1)
    print(f"OK: saved {len(uniq)} unique rows -> {out}", flush=True)


if __name__ == "__main__":
    main()
