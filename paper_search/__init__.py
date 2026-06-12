"""
Paper Search Toolkit — 多源学术论文搜索与评估框架

支持 ArXiv、Semantic Scholar、DBLP 三个数据源，
自动评估论文与目标研究主题的相关性，导出 Excel 筛选表并下载 PDF。

Usage:
    from paper_search import search_all, evaluate_papers, export_xlsx

    papers = await search_all(["LLM", "security", "prompt injection"], limit=20)
    evaluate_papers(papers, topic="prompt injection security")
    export_xlsx(papers, "results.xlsx")
"""

from .base import Paper
from .arxiv import ArxivClient
from .semantic_scholar import SemanticScholarClient
from .dblp import DblpClient
from .evaluator import evaluate_papers, guess_ccf, guess_category
from .xlsx_writer import export_xlsx, download_pdfs
