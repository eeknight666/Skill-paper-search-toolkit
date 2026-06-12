"""DBLP API 搜索客户端"""

import logging
import httpx
from .base import AbstractSearchClient, Paper

logger = logging.getLogger(__name__)

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "over",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "can", "shall", "this", "that", "these", "those", "it", "its",
    "not", "no", "nor", "so", "as", "if", "than", "too", "very", "just",
    "also", "only", "some", "any", "each", "every", "all", "both",
    "based", "using", "used", "via", "new", "towards", "toward",
}


def _optimize_keywords(keywords: list[str]) -> str:
    """优化关键词以适配 DBLP 标题搜索。

    DBLP 基于论文标题搜索（非全文），多词短语很少原样出现在标题中。
    将短语拆分为独立技术词，去除停用词，最大化标题匹配概率。
    """
    seen: set[str] = set()
    terms: list[str] = []
    for kw in keywords:
        if len(kw.split()) == 1:
            if kw.lower() not in seen:
                terms.append(kw)
                seen.add(kw.lower())
        else:
            for word in kw.split():
                wl = word.lower()
                if wl not in _STOPWORDS and wl not in seen:
                    terms.append(word)
                    seen.add(wl)
    return " ".join(terms)


class DblpClient(AbstractSearchClient):
    """DBLP 论文搜索 (dblp.org)

    基于论文标题搜索，适合查找已发表的会议/期刊论文，自动获取 venue 和 DOI。
    """

    BASE_URL = "https://dblp.org/search/publ/api"

    async def search(self, keywords: list[str], limit: int = 10) -> list[Paper]:
        query = _optimize_keywords(keywords)
        logger.info(f"DBLP query: {keywords!r} -> {query!r}")
        papers: list[Paper] = []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    self.BASE_URL,
                    params={"q": query, "h": min(limit, 30), "format": "json"},
                )
                if resp.status_code != 200:
                    return papers

                data = resp.json()
                hits = data.get("result", {}).get("hits", {}).get("hit", [])
                if isinstance(hits, dict):
                    hits = [hits]

                for hit in hits:
                    info = hit.get("info", {})
                    title = info.get("title", "")

                    year = info.get("year")
                    if year:
                        try:
                            year = int(year)
                        except (ValueError, TypeError):
                            year = None

                    authors_list: list[str] = []
                    ai = info.get("authors", {})
                    if ai:
                        ae = ai.get("author", [])
                        if isinstance(ae, dict):
                            ae = [ae]
                        for a in ae:
                            if isinstance(a, dict):
                                authors_list.append(a.get("text", ""))

                    papers.append(Paper(
                        title=title, authors=authors_list, year=year,
                        venue=info.get("venue", ""),
                        doi=info.get("doi", ""),
                        source_url=info.get("url", ""),
                        source_api="dblp",
                    ))
        except Exception as e:
            logger.error(f"DBLP search error: {e}")
        return papers
