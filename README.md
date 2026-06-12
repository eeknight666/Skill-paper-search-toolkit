<h1 align="center">
  <img src="https://img.icons8.com/color/48/search--v1.png" width="36" alt="">
  Paper Search Toolkit
</h1>

<p align="center">
  <b>多源学术论文搜索 · 相关性评估 · Excel 筛选表 · PDF 批量下载</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/sources-ArXiv%20%7C%20Semantic%20Scholar%20%7C%20DBLP-green" alt="Sources">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License">
  <img src="https://img.shields.io/badge/CCF-第七版(2026.03)-orange" alt="CCF">
</p>
---

# Paper Search Toolkit

## 这是什么？

一个通用的学术论文搜索与筛选工具，输入研究主题，自动完成：

| 步骤 | 说明 |
|------|------|
| 🔍 **多源搜索** | 同时查询 ArXiv、Semantic Scholar、DBLP，合并去重 |
| 📊 **智能评估** | 基于关键词 + 领域知识，自动评估相关性（强相关 / 相关 / 弱相关 / 一般 / 无关） |
| 🏷️ **自动分类** | 识别子领域（形式化方法 / 模糊测试 / 微架构安全 / ML-AI / Prompt注入 / 软件工程...） |
| 🏅 **CCF 定级** | 自动匹配 CCF 推荐目录（第七版·2026年3月更新） |
| 📥 **生成 Excel** | 带颜色标记、冻结首行、自动筛选的完整筛选表 |
| 💾 **下载 PDF** | 批量下载强相关论文的 PDF 全文 |

不限于特定领域——LLM 安全、Prompt 注入、RISC-V 验证、联邦学习、供应链安全……输入主题即可开始。

---

## 项目结构

```
├── collect.py               # 命令行入口（含 API Key 配置）
├── ccf/
│   └── CCF-2026-推荐目录.md  # CCF 第七版参考文档
├── paper_search/            # Python 包
│   ├── base.py              # Paper 数据模型
│   ├── arxiv.py             # ArXiv 客户端
│   ├── semantic_scholar.py  # Semantic Scholar 客户端
│   ├── dblp.py              # DBLP 客户端
│   ├── evaluator.py         # 相关性评估 & CCF 定级
│   └── xlsx_writer.py       # Excel 导出 & PDF 下载
└── CLAUDE.md                # Claude Code 集成说明
```

---

## 数据源

| 源               | 特点                               | API Key |
| ---------------- | ---------------------------------- | :-----: |
| ArXiv            | 预印本全文，覆盖 CS/AI/数学/物理   |   否    |
| Semantic Scholar | 引用网络 + 元数据 + OpenAccess PDF |  建议   |
| DBLP             | 标题搜索，venue/DOI 齐全           |   否    |

---

## 快速开始

### 安装

```bash
git clone https://github.com/eeknight666/paper-search-toolkit.git
cd paper-search-toolkit
pip install -r requirements.txt
```

---

### 使用

```bash
# 搜索大模型 Prompt 注入安全论文
python collect.py --domain security "LLM" "prompt injection" "jailbreak" "adversarial"

# 搜索 RISC-V 形式化验证论文，限定 ArXiv
python collect.py --source arxiv --limit 20 "RISC-V" "formal verification" "ISA"

# 搜索微架构侧信道攻击
python collect.py --domain security "microarchitecture" "side channel" "cache attack"

# 搜索联邦学习隐私保护，JSON 输出
python collect.py --domain ai --json "federated learning" "privacy" "differential privacy"
```

---

### API Key

Semantic Scholar 免费 API 无 Key 约 1 req/s，建议申请免费 Key 提升至 100 req/s。

[申请地址](https://www.semanticscholar.org/product/api#api-key-form) → 填入 `collect.py` 第 37 行：

```python
SEMANTIC_SCHOLAR_API_KEY = "your-key"
```

---

### 输出

运行后生成：
- `论文筛选结果.xlsx` — 完整筛选表，按相关性降序，颜色标记，支持筛选
- `papers/` — 强相关论文 PDF 全文

<details>
<summary>终端输出示例（点击展开）</summary>

```
============================================================
  Paper Search Toolkit
============================================================
  关键词: LLM prompt injection jailbreak adversarial
  数据源: arxiv, semantic_scholar, dblp
  领域:   security

  ArXiv: 15 篇
  Semantic Scholar: 15 篇
  DBLP: 6 篇
  去重后: 28 篇

============================================================
  相关性分布
============================================================
  强相关 :   9 篇  ████
  相关   :  12 篇  ██████
  弱相关 :   5 篇  ██
  一般   :   2 篇  █

============================================================
  强相关论文 TOP 9
============================================================
  [1] Prompt Injection Attacks on Large Language Models: A Survey
      John Doe; Jane Smith; Alice Wang 等(5人)
      2024  USENIX Security [CCF-A]  [Prompt注入/安全]
      ...
```
---

## 自定义 Excel 列

默认 9 列：论文名、发表时间、期刊/会议、CCF等级、作者、论文分类、简要描述、相关性、下载链接。

如需增删，改两个地方：

**1. 列内容** — `paper_search/base.py` 的 `Paper.to_row()`：

```python
def to_row(self) -> list[str]:
    abstract = (self.abstract or "").replace("\n", " ")
    return [
        self.title,
        str(self.year) if self.year else "",
        self.venue,
        self.ccf_level,
        "; ".join(self.authors),
        self.category,
        abstract[:500],
        self.relevance,
        self.pdf_url or self.source_url,
        # self.doi,          # ← 加新列
    ]
```

**2. 表头 + 列宽** — `paper_search/xlsx_writer.py`：

```python
EXCEL_HEADERS = [
    "论文名", "发表时间", "期刊/会议", "CCF等级", "作者",
    "论文分类", "简要描述", "相关性", "论文下载链接",
    # "DOI",               # ← 对应
]

col_widths = [45, 12, 28, 10, 35, 22, 60, 10, 50]  # 补一个宽度
```

---

## Python API

```python
import asyncio
from paper_search import (
    ArxivClient, SemanticScholarClient, DblpClient,
    evaluate_papers, export_xlsx, download_pdfs,
)

async def main():
    arxiv = ArxivClient()
    ss = SemanticScholarClient(api_key="")  # 可选
    dblp = DblpClient()

    papers = []
    papers += await arxiv.search(["LLM", "prompt injection", "security"], limit=20)
    papers += await ss.search(["LLM", "prompt injection", "security"], limit=20)
    papers += await dblp.search(["LLM", "prompt injection", "security"], limit=10)

    evaluate_papers(
        papers,
        topic_keywords=["LLM", "prompt injection", "security", "jailbreak"],
        domain_hint="security",
    )

    export_xlsx(papers, "output.xlsx")

    strong = [p for p in papers if p.relevance == "强相关"]
    await download_pdfs(strong, "pdfs/")

asyncio.run(main())
```

---

## FAQ

**Q: Semantic Scholar 报 429？**  

A: 免费 API 速率限制。申请 Key 填入即可：[申请链接](https://www.semanticscholar.org/product/api#api-key-form)

**Q: 提高搜索精度？** 

A: 用 `--domain` 指定领域（`security` / `ai` / `hardware` / `software`），或增加关键词。

**Q: 加自定义 CCF 等级？**  

A: 编辑 `paper_search/evaluator.py` 的 `CCF_VENUE_MAP`。

**Q: 相关性不准？**  

A: 增加主题关键词，或调整 `evaluate_papers()` 的评分权重。

---

## License

MIT
