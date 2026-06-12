"""Semantic Scholar API 搜索客户端"""

import logging
import httpx
from .base import AbstractSearchClient, Paper

logger = logging.getLogger(__name__)


class SemanticScholarClient(AbstractSearchClient):
    """Semantic Scholar 论文搜索 (api.semanticscholar.org)

    免费 API 有速率限制（无 Key 约 1 req/s），填入 API Key 可提高到 100 req/s。
    申请地址: https://www.semanticscholar.org/product/api#api-key-form
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def search(self, keywords: list[str], limit: int = 10) -> list[Paper]:
        query = " ".join(keywords)
        papers: list[Paper] = []

        try:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/paper/search",
                    params={
                        "query": query,
                        "limit": min(limit, 100),
                        "fields": (
                            "title,authors,year,venue,journal,"
                            "externalIds,abstract,url,openAccessPdf"
                        ),
                    },
                    headers=headers,
                )

                if resp.status_code == 429:
                    logger.warning(
                        "Semantic Scholar rate limited (429). "
                        "Set api_key for higher limits: "
                        "https://www.semanticscholar.org/product/api#api-key-form"
                    )
                    return papers
                if resp.status_code != 200:
                    logger.warning(f"Semantic Scholar returned {resp.status_code}")
                    return papers

                data = resp.json()
                for item in data.get("data", []):
                    authors = [a.get("name", "") for a in item.get("authors", [])]
                    ext = item.get("externalIds", {}) or {}
                    doi = ext.get("DOI", "")
                    aid = ext.get("ArXiv", "")

                    venue = ""
                    if item.get("journal"):
                        venue = item["journal"].get("name", "")
                    elif item.get("venue"):
                        venue = item.get("venue", "")

                    pdf_url = ""
                    oa = item.get("openAccessPdf")
                    if oa:
                        pdf_url = oa.get("url", "")

                    papers.append(Paper(
                        title=item.get("title", ""), authors=authors,
                        year=item.get("year"), venue=venue, doi=doi,
                        arxiv_id=aid, abstract=item.get("abstract", ""),
                        source_url=item.get("url", ""), pdf_url=pdf_url,
                        source_api="semantic_scholar",
                    ))
        except Exception as e:
            logger.error(f"Semantic Scholar search error: {e}")
        return papers
