#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 mkdocs.yml 的完整导航（nav）并按门类—子类—词条三层装配。
用法：python tools/gen_nav.py   （重写 mkdocs.yml 中 nav: 之后的内容）
"""
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = yaml.safe_load(open(os.path.join(ROOT, "data", "site_config.yaml"), encoding="utf-8"))
TAX = None
_tax_path = os.path.join(ROOT, "data", "taxonomy.json")
if os.path.exists(_tax_path):
    import json
    TAX = json.load(open(_tax_path, encoding="utf-8"))


def subcat_count(cat_name, sub_name):
    if not TAX:
        return 1
    return sum(1 for t in TAX.values() if t["category"] == cat_name and t["subcat"] == sub_name)

FEATURED = {
    "民间文学": [("Ⅰ-27", "格萨（斯）尔"), ("Ⅰ-7", "梁祝传说")],
    "传统音乐": [("Ⅱ-34", "古琴艺术"), ("Ⅱ-28", "侗族大歌")],
    "传统舞蹈": [("Ⅲ-13", "安塞腰鼓"), ("Ⅲ-5", "狮舞"), ("Ⅲ-27", "傣族孔雀舞")],
    "传统戏剧": [("Ⅳ-28", "京剧"), ("Ⅳ-1", "昆曲"), ("Ⅳ-91", "皮影戏")],
    "曲艺": [("Ⅴ-1", "苏州评弹"), ("Ⅴ-47", "相声"), ("Ⅴ-48", "京韵大鼓")],
    "传统体育、游艺与杂技": [("Ⅵ-11", "太极拳"), ("Ⅵ-1", "吴桥杂技"), ("Ⅵ-7", "少林功夫")],
    "传统美术": [("Ⅶ-16", "剪纸"), ("Ⅶ-1", "杨柳青木版年画"), ("Ⅶ-18", "苏绣")],
    "传统技艺": [("Ⅷ-7", "景德镇手工制瓷技艺"), ("Ⅷ-13", "南京云锦木机妆花手工织造技艺"), ("Ⅷ-65", "宣纸制作技艺")],
    "传统医药": [("Ⅸ-5", "针灸"), ("Ⅸ-7", "同仁堂中医药文化"), ("Ⅸ-9", "藏医药")],
    "民俗": [("Ⅹ-36", "妈祖祭典"), ("Ⅹ-1", "春节"), ("Ⅹ-68", "农历二十四节气")],
}
CRAFTSMEN = {
    "民间文学": "谭振山", "传统音乐": "李祥霆", "传统舞蹈": "约相", "传统戏剧": "梅兰芳", "曲艺": "单田芳",
    "传统体育、游艺与杂技": "陈小旺", "传统美术": "库淑兰", "传统技艺": "徐朝兴", "传统医药": "程莘农", "民俗": "林金榜",
}


def ind(n):
    return " " * n


def main():
    lines = []
    lines.append("nav:")
    lines.append(f"{ind(2)}- 首页: index.md")
    lines.append(f"{ind(2)}- 世界非遗:")
    lines.append(f"{ind(6)}- 总览: 世界非遗/index.md")
    lines.append(f"{ind(6)}- 名录机制: 世界非遗/机制.md")
    lines.append(f"{ind(6)}- 中国 44 项全录: 世界非遗/中国44项.md")
    lines.append(f"{ind(6)}- 各洲巡礼:")
    for r in ["亚洲", "欧洲", "非洲", "美洲", "大洋洲"]:
        lines.append(f"{ind(10)}- {r}: 世界非遗/{r}.md")
    lines.append(f"{ind(2)}- 中国非遗:")
    lines.append(f"{ind(6)}- 总览 · 十大门类: 中国非遗/index.md")
    lines.append(f"{ind(6)}- 匠心人物 · 十位传灯人: 中国非遗/匠心人物.md")
    for c in CFG["categories"]:
        cat, d = c["name"], c["dir"]
        lines.append(f"{ind(6)}- {cat}:")
        lines.append(f"{ind(10)}- 门类导航: 中国非遗/{d}/index.md")
        lines.append(f"{ind(10)}- 门类导览:")
        for sc in c["subcats"]:
            if subcat_count(cat, sc["name"]) == 0:
                continue
            lines.append(f"{ind(14)}- {sc['name']}: 中国非遗/{d}/{sc['name']}.md")
        lines.append(f"{ind(10)}- 代表专题:")
        for num, title in FEATURED.get(cat, []):
            lines.append(f"{ind(14)}- {title}: 中国非遗/{d}/项目/{title}.md")
        lines.append(f"{ind(10)}- 代表人物:")
        lines.append(f"{ind(14)}- {CRAFTSMEN[cat]}: 中国非遗/{d}/人物/{CRAFTSMEN[cat]}.md")
        lines.append(f"{ind(10)}- 项目名录: 中国非遗/{d}/项目名录.md")
    lines.append(f"{ind(2)}- 关于本志:")
    lines.append(f"{ind(6)}- 编例与数据说明: 关于/index.md")
    lines.append(f"{ind(6)}- 站点结构与使用: 关于/站点结构.md")
    nav = "\n".join(lines) + "\n"

    path = os.path.join(ROOT, "mkdocs.yml")
    text = open(path, encoding="utf-8").read()
    idx = text.index("\nnav:")
    open(path, "w", encoding="utf-8").write(text[:idx] + "\n" + nav)
    print("nav 已写入 mkdocs.yml（%d 行）" % len(lines))


if __name__ == "__main__":
    main()
