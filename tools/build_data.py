#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 data/raw/ihchina_projects.json（3610 条原始记录）整理为结构化项目数据。
- 以「项目编号」为词条身份（约 1574 个），聚合其全部子项/批次/申报地区记录
- 输出 data/projects.json、data/stats.txt、data/catalog/*.txt
"""
import html
import json
import os
import re
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "ihchina_projects.json")
OUT = os.path.join(ROOT, "data", "projects.json")
STATS = os.path.join(ROOT, "data", "stats.txt")
CATALOG_DIR = os.path.join(ROOT, "data", "catalog")

ROMAN_ORDER = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ"]
ROMAN_NAME = {
    "Ⅰ": "民间文学", "Ⅱ": "传统音乐", "Ⅲ": "传统舞蹈", "Ⅳ": "传统戏剧", "Ⅴ": "曲艺",
    "Ⅵ": "传统体育、游艺与杂技", "Ⅶ": "传统美术", "Ⅷ": "传统技艺", "Ⅸ": "传统医药", "Ⅹ": "民俗",
}
BATCH_ORDER = ["第一批", "第二批", "第三批", "第四批", "第五批"]


def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("</br>", "\n").replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("\u3000", " ").replace("\r", "")
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def parse_batch(rx: str):
    """'2006</br>(第一批)' -> ('第一批', '2006')"""
    year = ""
    m = re.match(r"\s*(\d{4})", rx or "")
    if m:
        year = m.group(1)
    mb = re.search(r"第(一|二|三|四|五)批", rx or "")
    batch = f"第{mb.group(1)}批" if mb else ""
    return batch, year


def base_title(title: str) -> str:
    """去掉括号后缀：'宝卷（靖江宝卷）' -> '宝卷'"""
    return re.sub(r"[（(].*?[)）]\s*$", "", title).strip() or title


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    groups = OrderedDict()
    for r in rows:
        num = (r.get("num") or "").strip()
        if not num:
            continue
        rec = {
            "id": r.get("id"),
            "title": (r.get("title") or "").strip(),
            "province": (r.get("province") or "").strip(),
            "unit": (r.get("unit") or "").strip(),
            "protect_unit": (r.get("protect_unit") or "").strip(),
            "rx_time": r.get("rx_time") or "",
            "cate": r.get("cate") or "",
            "type": r.get("type") or "",
            "content": clean_text(r.get("content") or ""),
        }
        rec["batch"], rec["year"] = parse_batch(rec["rx_time"])
        groups.setdefault(num, []).append(rec)

    projects = []
    for num, recs in groups.items():
        roman = num.split("-")[0].strip()
        m = re.search(r"(\d+)", num)
        seq = int(m.group(1)) if m else 0
        # 规范名称：优先取最早「新增项目」且无括号的名称，其次取最短基础名
        new_recs = [r for r in recs if r["cate"] == "新增项目"]
        pool = new_recs or recs
        if not new_recs:
            new_recs = recs
        first_batch_new = None
        for b in BATCH_ORDER:
            if any(r["batch"] == b for r in new_recs):
                first_batch_new = b
                break
        base_candidates = [base_title(r["title"]) for r in recs if r["cate"] == "新增项目"] or [base_title(r["title"]) for r in recs]
        title = min(set(base_candidates), key=lambda t: (len(t), t))
        variants = sorted({r["title"] for r in recs if r["title"] != title})
        batches = [b for b in BATCH_ORDER if any(r["batch"] == b for r in recs)]
        # 省级短名（取前 2-3 字，去掉「省/市/自治区」等）用于展示
        regions, seen = [], set()
        for r in recs:
            p = r["province"] or r["unit"]
            p = re.sub(r"（.*?）$", "", p)
            short = re.sub(r"(省|市|自治区|回族|维吾尔|壮族|特别行政区).*$", "", p)[:4]
            if short and short not in seen:
                seen.add(short)
                regions.append(short)
        # 描述文本：取内容最丰富的一条
        content_best = ""
        for r in sorted(recs, key=lambda x: -len(x["content"])):
            if r["content"]:
                content_best = r["content"]
                break
        projects.append({
            "num": num,
            "roman": roman,
            "seq": seq,
            "category": ROMAN_NAME.get(roman, recs[0]["type"]),
            "title": title,
            "variants": variants,
            "batches": batches,
            "first_batch": first_batch_new or (batches[0] if batches else ""),
            "regions": regions,
            "records": recs,
            "n_records": len(recs),
            "content_best": content_best,
        })

    def sort_key(p):
        return (ROMAN_ORDER.index(p["roman"]) if p["roman"] in ROMAN_ORDER else 99, p["seq"])
    projects.sort(key=sort_key)

    json.dump(projects, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ------- 统计与校验 -------
    lines = []
    lines.append(f"总记录数: {len(rows)}")
    lines.append(f"项目编号数（词条数）: {len(projects)}")
    lines.append(f"子项记录数: {sum(p['n_records'] for p in projects)}")
    cat_cnt = Counter(p["category"] for p in projects)
    lines.append("\n按类别（编号数 / 记录数）:")
    for rn in ROMAN_ORDER:
        name = ROMAN_NAME[rn]
        n_proj = sum(1 for p in projects if p["category"] == name)
        n_rec = sum(p["n_records"] for p in projects if p["category"] == name)
        lines.append(f"  {rn} {name}: {n_proj} 项 / {n_rec} 条")
    first_batch_cnt = Counter(p["first_batch"] for p in projects)
    lines.append("\n按首次公布批次（编号数）:")
    known = {"第一批": 518, "第二批": 510, "第三批": 191, "第四批": 153, "第五批": 185}
    for b in BATCH_ORDER:
        lines.append(f"  {b}: {first_batch_cnt.get(b, 0)}（官方主项目 {known[b]}）")
    lines.append(f"  合计: {sum(first_batch_cnt.get(b, 0) for b in BATCH_ORDER)}（官方 1557）")
    ext_only = [p["num"] for p in projects if all(r["cate"] != "新增项目" for r in p["records"])]
    lines.append(f"\n仅有扩展记录、无新增记录的项目编号: {len(ext_only)} -> {ext_only[:20]}")
    n_variants = sum(1 for p in projects for _ in p["variants"])
    lines.append(f"子项变体名称（括号变体）总数: {n_variants}")
    with open(STATS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))

    # ------- 各类别名录（供策划参考） -------
    os.makedirs(CATALOG_DIR, exist_ok=True)
    for rn in ROMAN_ORDER:
        name = ROMAN_NAME[rn]
        fname = os.path.join(CATALOG_DIR, f"{rn}_{name.replace('、','-')}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            for p in projects:
                if p["category"] != name:
                    continue
                reg = "、".join(p["regions"][:4])
                var = f" ⟦含子项 {len(p['variants'])}⟧" if p["variants"] else ""
                f.write(f"{p['num']}\t{p['title']}\t{reg}\t{p['first_batch']}\t{p['n_records']}{var}\n")
    print(f"\n名录清单已输出 -> {CATALOG_DIR}")


if __name__ == "__main__":
    main()
