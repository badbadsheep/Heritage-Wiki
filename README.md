# 非遗志 · HeritageWiki

> 人间百工，皆有来处。以图文汇录世界非物质文化遗产——中国十大门类、1557 项国家级代表性项目全量收录。

一个可离线运行、可自由编辑的**非物质文化遗产图文百科**：门类页以「气泡」引路，词条页以「源流 · 形制 · 工巧 · 符号 · 守望」五段细述，全站统一「宣纸 × 墨 × 朱砂」视觉体系，图像皆为本站自绘「图版」与生成的实景大图。

---

## ✦ 特性一览

- **全量收录**：国务院公布的五批国家级非遗代表性项目 **1557 项**（含 **3610 条子项记录**，与官方数字逐批吻合）逐项立档；
- **层层展开**：世界非遗 → 中国非遗 → 十大门类 → 子类门览 → 项目词条，每一级都有独立**导航页**，门类/子类页以**气泡**铺陈入口；
- **深度内容**：12 篇深度专题长文 + 10 篇匠人图文传记 + 世界卷（名录机制 / 中国 44 项全录 / 五大洲巡礼）；
- **图片体系**：每篇词条 **≥5 张高清 PNG**——「题名 · 山川 · 纹样 · 工巧 · 名录」五式图版，全站近 8000 张统一绘制；首页与导航页使用**半透明大图**背景；
- **全文检索**：内置中文分词（jieba）搜索；
- **纯 Markdown 编辑**：内容全部在 `docs/` 下，改完即自动刷新。

## ✦ 快速开始

> 环境要求：Python 3.9+（Windows / macOS / Linux 均可）

```bash
# 方式一（Windows）：双击 serve.bat —— 首次运行会自动建虚拟环境并装依赖
# 方式二（Git Bash / macOS / Linux）：
./serve.sh

# 方式三（手动）：
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple     # 清华镜像（可省略）
.venv/Scripts/python.exe -m mkdocs serve --dev-addr 127.0.0.1:8000
```

打开 **http://127.0.0.1:8000** 即可阅读；修改 `docs/` 下任意 Markdown，浏览器会自动刷新。

构建静态站点（输出到 `site/`）：

```bash
.venv/Scripts/python.exe -m mkdocs build
```

## ✦ 分支树（内容层级）

```
非遗志 · HeritageWiki
├─ 世界非遗
│  ├─ 名录机制（UNESCO 三大名录 · 转名录 · 中国参与）
│  ├─ 中国 44 项全录（39 代表作 + 4 急需保护 + 1 优秀实践）
│  └─ 各洲巡礼：亚洲 · 欧洲 · 非洲 · 美洲 · 大洋洲
├─ 中国非遗
│  ├─ 总览 · 十大门类（十个气泡入口）
│  ├─ 匠心人物 · 十位传灯人
│  └─ 十大门类（每门类一层）
│     ├─ 门类导航页（子类气泡 + 代表专题 + 代表人物 + 名录入口）
│     ├─ 子类门览（约 52 个 · 气泡铺陈全部项目）
│     ├─ 代表专题（深度长文 · 五段体例）
│     ├─ 代表人物（每个门类一位匠人传记）
│     ├─ 项目名录（本门类全量总表）
│     └─ 项目词条（1557 个 · 五式图版 + 子项一览）
└─ 关于本志：编例与数据说明 · 站点结构与使用
```

十大门类：**民间文学 · 传统音乐 · 传统舞蹈 · 传统戏剧 · 曲艺 · 传统体育游艺与杂技 · 传统美术 · 传统技艺 · 传统医药 · 民俗**

## ✦ 目录结构

```
Heritage-Wiki/
├── mkdocs.yml              # 站点配置与完整导航（可手改，或由 tools/gen_nav.py 生成）
├── requirements.txt        # mkdocs / mkdocs-material / jieba
├── serve.bat / serve.sh    # 一键本地预览
├── docs/                   # ← 全部内容（Markdown）
│   ├── index.md            #   首页
│   ├── 世界非遗/            #   机制 · 中国44项 · 五洲
│   ├── 中国非遗/            #   总览 · 匠心人物 · <门类>/（index/子类/项目/人物/项目名录）
│   ├── 关于/                #   编例与数据说明 · 站点结构
│   ├── assets/img/         #   图像资产（heroes 大图 / plates 五式图版 / bubbles 气泡 / articles / craftsmen）
│   └── stylesheets/        #   设计系统：extra.css（令牌与组件）、heroes.css（大图索引）
├── data/                   # 数据与内容配置
│   ├── projects.json       #   3610 条名录记录
│   ├── taxonomy.json       #   1557 项 → 子类映射
│   ├── site_config.yaml    #   门类 / 子类规则 / 视觉记号
│   └── featured/<编号>.md   #   深度专题正文（自动注入对应词条页）
└── tools/                  # 自动化脚本（见下）
```

## ✦ 数据与校验

| 批次 | 公布时间 | 主项目数 | 本站收录 |
| :-- | :--: | :--: | :--: |
| 第一批 | 2006 | 518 | 518 ✓ |
| 第二批 | 2008 | 510 | 510 ✓ |
| 第三批 | 2011 | 191 | 191 ✓ |
| 第四批 | 2014 | 153 | 153 ✓ |
| 第五批 | 2021 | 185 | 185 ✓ |
| **合计** | | **1557** | **1557 ✓**（子项记录 3610 条） |

- 数据来源：国务院公布名录，经**中国非物质文化遗产网（ihchina.cn）**整理校核；
- 深度专题与匠人传记参考公开新闻报道、地方志与机构资料撰写（文末标注来源）。

## ✦ 编辑指南

```bash
# 1) 新增 / 修改词条：直接在 docs/中国非遗/<门类>/项目/ 下编辑 Markdown
# 2) 新增深度专题：把正文写入 data/featured/<项目编号>.md（顶部元信息见现有样例），然后：
python tools/gen_pages.py --nums Ⅷ-7
# 3) 调整子类分组：编辑 data/site_config.yaml 后
python tools/classify.py --write && python tools/gen_pages.py --force && python tools/build_images.py --bubbles
# 4) 图版重绘（抽样 / 指定 / 全量）：
python tools/build_images.py --sample 6
python tools/build_images.py --only Ⅷ-7 Ⅶ-16
python tools/build_images.py
# 5) 抓取最新名录数据（如需）：
python tools/fetch_ihchina.py && python tools/build_data.py
```

> 脚本一览：`fetch_ihchina`（抓取）→ `build_data`（清洗校验）→ `classify`（子类）→ `build_images`（图版/气泡）→ `gen_pages`（词条/门览/名录/专题注入）→ `gen_nav`（导航）。

## ✦ 发布到 GitHub Pages（成为正式网站）

仓库已内置 `.github/workflows/deploy.yml`，推送即自动构建、自动发布，无需本地装环境。

```bash
# ① 在 GitHub 上新建一个空仓库（不要勾选 README / .gitignore），假设名为 Heritage-Wiki
# ② 本地初始化并推送（本目录已 git init 过，可直接从第 3 步开始）
git init -b main
git add -A
git commit -m "feat: 非遗志 HeritageWiki 首个版本"
git remote add origin https://github.com/<你的用户名>/Heritage-Wiki.git
git push -u origin main
```

```text
③ 仓库页 → Settings → Pages → Source 选「GitHub Actions」（只需设置这一次）
④ 仓库页 → Actions，等待「构建并发布非遗志」跑完（约 2–4 分钟）
⑤ 访问 https://<你的用户名>.github.io/Heritage-Wiki/
```

- 之后每次 `git push` 都会自动重新发布；
- **如果第一次运行失败**，且失败步骤是「配置 Pages」并提示 `Get Pages site failed`：说明第 ③ 步还没做。开启后回到 Actions，点该次运行的 **Re-run all jobs** 即可（`configure-pages` 无法用默认的 `GITHUB_TOKEN` 自动开启 Pages，这是 GitHub 的限制）；
- 站点默认发布 `site/` 内容（本地 `site/` 目录已被 `.gitignore` 忽略，CI 里现场构建）；
- 想要自己的域名：Settings → Pages → Custom domain 填域名，再在域名服务商加一条 CNAME 记录指向 `<用户名>.github.io`；
- 若仓库体积偏大导致首次推送缓慢，可改用 GitHub Desktop 推送，或先执行第 4 步的「图片瘦身」思路（见下）；
- 备选托管（国内访问更快，配置方式类似，构建命令同为 `mkdocs build`）：Cloudflare Pages、Gitee Pages、Vercel。

## ✦ 图片体系说明

- **图版五式**（`assets/img/plates/<编号>/1-5.png`）：题名 · 山川 · 纹样 · 工巧 · 名录，以门类色谱 + 器物意象绘制；
- **实景大图**（heroes / articles / craftsmen）：AI 生成的**意临之作**，用于半透明背景与页面配图，**非纪实影像**；
- **气泡**（bubbles）：从门类大图裁切并调色，用于门类/子类/项目的圆形入口。

## ✦ 已知事项与 Roadmap

- 深度专题当前 12 篇，其余代表项目以「名录档案」体例收录，可按五段体例持续升级（文件级操作，互不影响）；
- 世界卷各洲名录为**精选**收录，欢迎按 UNESCO 官网逐条扩充（页面已标注年份口径）；
- 后续方向：省级名录扩展、传承人图谱、口述音视频嵌入、繁体 / 多语版本。

## ✦ 致谢与说明

- 名录数据版权归国务院公布文件与官方名录网站所有；本志为**公益性知识项目**，欢迎指正补遗；
- 站点由 MkDocs + Material for MkDocs 构建，视觉系统与全部图版为本站自绘。

---

**非遗志 · HeritageWiki** ｜ 为每一项非遗，留一张安静的书签。
