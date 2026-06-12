"""ArXiv API 搜索客户端"""

import re
import logging
import xml.etree.ElementTree as ET

import httpx
from .base import AbstractSearchClient, Paper

logger = logging.getLogger(__name__)


class ArxivClient(AbstractSearchClient):
    """ArXiv 论文搜索 (export.arxiv.org)

    无需 API Key，按相关性排序，支持布尔组合查询。
    """

    BASE_URL = "https://export.arxiv.org/api/query"

    async def search(self, keywords: list[str], limit: int = 10) -> list[Paper]:
        # ArXiv 要求用 + 表示 AND，不能经过 httpx params URL 编码
        query = "+AND+".join(f"all:{kw}" for kw in keywords)
        url = (
            f"{self.BASE_URL}?search_query={query}"
            f"&start=0&max_results={min(limit, 50)}&sortBy=relevance"
        )
        papers: list[Paper] = []

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    logger.warning(f"ArXiv returned {resp.status_code}")
                    return papers

                ns = {"a": "http://www.w3.org/2005/Atom"}
                root = ET.fromstring(resp.text)

                for entry in root.findall("a:entry", ns):
                    title_el = entry.find("a:title", ns)
                    title = title_el.text.strip() if title_el is not None else ""

                    authors: list[str] = []
                    for au in entry.findall("a:author", ns):
                        name_el = au.find("a:name", ns)
                        if name_el is not None and name_el.text:
                            authors.append(name_el.text)

                    published = entry.find("a:published", ns)
                    year = None
                    if published is not None and published.text:
                        m = re.search(r"(\d{4})", published.text)
                        if m:
                            year = int(m.group(1))

                    summary_el = entry.find("a:summary", ns)
                    abstract = ""
                    if summary_el is not None and summary_el.text:
                        abstract = summary_el.text.strip()

                    id_el = entry.find("a:id", ns)
                    source_url = ""
                    if id_el is not None and id_el.text:
                        source_url = id_el.text.strip()

                    arxiv_id = ""
                    if source_url:
                        m = re.search(r"abs/([^/]+)$", source_url)
                        if m:
                            arxiv_id = m.group(1)

                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""

                    papers.append(Paper(
                        title=title, authors=authors, year=year, venue="arXiv",
                        arxiv_id=arxiv_id, abstract=abstract,
                        source_url=source_url, pdf_url=pdf_url, source_api="arxiv",
                    ))
        except Exception as e:
            logger.error(f"ArXiv search error: {e}")
        return papers
