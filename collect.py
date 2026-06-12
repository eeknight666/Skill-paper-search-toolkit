#!/usr/bin/env python3
"""
Paper Search Toolkit — 多源学术论文搜索与评估工具

用法:
    # 基本搜索
    python collect.py "LLM security prompt injection"

    # 指定数据源和条数
    python collect.py --source arxiv --limit 20 "RISC-V formal verification"

    # 限定目录范围（给出领域提示，优化评估）
    python collect.py --domain security "microarchitecture side channel attack"

    # 输出 JSON 便于程序处理
    python collect.py --json "federated learning privacy"

Semantic Scholar 需要 API Key 以提高速率限制:
    在下方 SEMANTIC_SCHOLAR_API_KEY 填入你的 key
    免费申请: https://www.semanticscholar.org/product/api#api-key-form
"""

import sys
import asyncio
import logging
from pathlib import Path
from collections import OrderedDict

from paper_search import (
    ArxivClient, SemanticScholarClient, DblpClient,
    evaluate_papers, export_xlsx, download_pdfs, Paper,
)

# ============================================================
# >>> Semantic Scholar API Key（在此填入你的 key，可选）
# ============================================================
SEMANTIC_SCHOLAR_API_KEY = ""
# ============================================================

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR / "papers"
OUTPUT_XLSX = BASE_DIR / "论文筛选结果.xlsx"


def deduplicate(papers: list[Paper]) -> list[Paper]:
    """去重：保留信息最丰富的那条"""
    seen: OrderedDict[str, Paper] = OrderedDict()
    for p in papers:
        key = p.key
        if key in seen:
            existing = seen[key]
            if not existing.venue and p.venue:
                existing.venue = p.venue
            if not existing.doi and p.doi:
                existing.doi = p.doi
            if not existing.abstract and p.abstract:
                existing.abstract = p.abstract
            if not existing.pdf_url and p.pdf_url:
                existing.pdf_url = p.pdf_url
            existing.source_api += f",{p.source_api}"
            if not existing.arxiv_id and p.arxiv_id:
                existing.arxiv_id = p.arxiv_id
                existing.pdf_url = f"https://arxiv.org/pdf/{p.arxiv_id}"
        else:
            seen[key] = p
    return list(seen.values())


async def search_all_sources(
    keywords: list[str],
    limit: int = 15,
    sources: tuple[str, ...] = ("arxiv", "semantic_scholar", "dblp"),
) -> list[Paper]:
    """依次从多个数据源搜索并合并去重"""
    all_papers: list[Paper] = []

    if "arxiv" in sources:
        client = ArxivClient()
        papers = await client.search(keywords, limit)
        logger.info(f"  ArXiv: {len(papers)} 篇")
        all_papers.extend(papers)

    if "semantic_scholar" in sources:
        client = SemanticScholarClient(api_key=SEMANTIC_SCHOLAR_API_KEY)
        papers = await client.search(keywords, limit)
        logger.info(f"  Semantic Scholar: {len(papers)} 篇")
        all_papers.extend(papers)
        if papers:
            await asyncio.sleep(1)  # 避免触发限流

    if "dblp" in sources:
        client = DblpClient()
        papers = await client.search(keywords, min(limit, 10))
        logger.info(f"  DBLP: {len(papers)} 篇")
        all_papers.extend(papers)

    return deduplicate(all_papers)


def print_summary(papers: list[Paper]) -> None:
    """打印评估摘要"""
    from collections import Counter
    rel_counts = Counter(p.relevance for p in papers)
    print(f"\n{'='*60}")
    print(f"  相关性分布")
    print(f"{'='*60}")
    for label in ["强相关", "相关", "弱相关", "一般", "无关"]:
        cnt = rel_counts.get(label, 0)
        bar = "█" * (cnt // 2) if cnt else ""
        print(f"  {label:6s}: {cnt:3d} 篇  {bar}")

    strong = [p for p in papers if p.relevance == "强相关"]
    print(f"\n{'='*60}")
    print(f"  强相关论文 TOP {min(len(strong), 10)}")
    print(f"{'='*60}")
    for i, p in enumerate(
        sorted(strong, key=lambda x: x.relevance_score, reverse=True)[:10], 1
    ):
        authors = "; ".join(p.authors[:3])
        if len(p.authors) > 3:
            authors += f" 等({len(p.authors)}人)"
        print(f"\n  [{i}] {p.title}")
        print(f"      {authors}")
        ccf = f" [{p.ccf_level}]" if p.ccf_level else ""
        print(f"      {p.year}  {p.venue}{ccf}  [{p.category}]")
        ab = (p.abstract or "")[:200].replace("\n", " ")
        print(f"      {ab}...")


def parse_args():
    import argparse
    p = argparse.ArgumentParser(
        description="Paper Search Toolkit — 多源学术论文搜索与评估",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python collect.py "LLM security prompt injection"
  python collect.py --source arxiv --limit 20 "RISC-V formal verification"
  python collect.py --domain security "hardware side channel attack"
  python collect.py --json --limit 50 "federated learning privacy"
        """,
    )
    p.add_argument("keywords", nargs="+", help="搜索关键词")
    p.add_argument("--source", "-s", choices=["arxiv", "semantic_scholar", "dblp"],
                   action="append", default=None,
                   help="限定数据源（可多次指定，默认全部）")
    p.add_argument("--limit", "-n", type=int, default=15,
                   help="每个数据源返回条数（默认 15）")
    p.add_argument("--domain", "-d", default="general",
                   choices=["general", "security", "ai", "hardware", "software"],
                   help="领域提示，优化评估准确度")
    p.add_argument("--json", "-j", action="store_true", help="以 JSON 输出结果")
    p.add_argument("--no-download", action="store_true", help="不下载 PDF")
    p.add_argument("--no-xlsx", action="store_true", help="不导出 Excel")
    return p.parse_args()


async def main():
    args = parse_args()

    sources = (
        tuple(args.source) if args.source
        else ("arxiv", "semantic_scholar", "dblp")
    )

    # ---- 搜索 ----
    print(f"\n{'='*60}")
    print(f"  Paper Search Toolkit")
    print(f"{'='*60}")
    print(f"  关键词: {' '.join(args.keywords)}")
    print(f"  数据源: {', '.join(sources)}")
    print(f"  领域:   {args.domain}")
    print(f"")

    papers = await search_all_sources(args.keywords, args.limit, sources)
    print(f"  去重后: {len(papers)} 篇")

    # ---- 评估 ----
    print(f"\n  评估相关性 ...")
    evaluate_papers(papers, topic_keywords=args.keywords, domain_hint=args.domain)

    print_summary(papers)

    # ---- JSON 输出 ----
    if args.json:
        import json
        output = []
        for p in sorted(papers, key=lambda x: x.relevance_score, reverse=True):
            output.append({
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "venue": p.venue,
                "ccf_level": p.ccf_level,
                "doi": p.doi,
                "arxiv_id": p.arxiv_id,
                "category": p.category,
                "abstract": p.abstract,
                "relevance": p.relevance,
                "relevance_score": p.relevance_score,
                "source_url": p.source_url,
                "pdf_url": p.pdf_url,
                "source_api": p.source_api,
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # ---- 导出 Excel ----
    if not args.no_xlsx:
        print(f"\n  导出 Excel ...")
        export_xlsx(papers, OUTPUT_XLSX)

    # ---- 下载 PDF ----
    if not args.no_download:
        strong = [p for p in papers if p.relevance == "强相关"]
        print(f"\n  下载强相关论文 PDF ({len(strong)} 篇) ...")
        ok, total = await download_pdfs(strong, PDF_DIR)
        print(f"  下载完成: {ok}/{total}")

    print(f"\n{'='*60}")
    print(f"  完成!")
    if not args.no_xlsx:
        print(f"  Excel: {OUTPUT_XLSX.resolve()}")
    if not args.no_download:
        print(f"  PDF:   {PDF_DIR.resolve()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
