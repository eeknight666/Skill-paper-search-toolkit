"""ArXiv API 搜索客户端"""

import re
import logging
import xml.etree.ElementTree as ET

import httpx
from .base import AbstractSearchClient, Paper

logger = logging.getLogger(__name__)

# 从 ArXiv comment 中提取真实发表 venue 的正则
_VENUE_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        # "Accepted at X Conference", "Accepted and presented at X"
        r"Accepted\s+(?:and\s+presented\s+)?(?:at|to|by|in)\s+(.+?)(?:\.\s|,\s|\.$|,$|\s+Conference|\s+Symposium|\s+Workshop|\s+\d{4}|$)",
        # "Published in X", "To appear in X"
        r"(?:Published|To\s+appear|To\s+be\s+published)\s+(?:in|at)\s+(.+?)(?:\.\s|,\s|\.$|,$|$)",
        # "Proceedings of X"
        r"Proceedings?\s+(?:of\s+(?:the\s+)?)?(.+?)(?:\.\s|,\s|\.$|,$|$)",
        # "In X Conference", "Presented at X" — 但要求后面有会议/期刊标志词
        r"(?:In|Presented\s+at)\s+(.+?\s(?:Conference|Symposium|Workshop|Journal|Transactions|Proceedings))",
        # 知名缩写+年份+会议类型词，例如 "SECRISC-V 2019 Workshop"
        # 也匹配 "International Conference on X" 这样的全称
        r"([A-Z][A-Za-z\-]{2,}(?:\s+\d{4})?\s+(?:Conference|Symposium|Workshop|Journal|Transactions)(?:\s+on\s+[A-Z][A-Za-z\-\s]+?)?(?:\.|,|$|\s+\())",
    ]
]

# 常见误提取词（不是会议/期刊名）
_VENUE_BLACKLIST = {
    "pages", "page", "figures", "figure", "tables", "table",
    "this paper", "this work", "preprint", "submitted", "arxiv",
    "accepted", "published", "to appear", "in press",
    "international conference", "hardware conference",
    "conference", "workshop", "symposium", "journal",
}

# 已知的顶级会议/期刊别名 → 标准名
_VENUE_ALIASES = {
    "USENIX Security": "USENIX Security Symposium",
    "NDSS": "NDSS",
    "CCS": "ACM CCS",
    "S&P": "IEEE S&P",
    "ISCA": "ISCA",
    "HPCA": "HPCA",
    "MICRO": "MICRO",
    "ASPLOS": "ASPLOS",
    "DAC": "DAC",
    "DATE": "DATE",
    "PLDI": "PLDI",
    "ICSE": "ICSE",
    "NeurIPS": "NeurIPS",
    "ICML": "ICML",
    "AAAI": "AAAI",
    "IJCAI": "IJCAI",
    "ACL": "ACL",
    "EMNLP": "EMNLP",
    "EuroSys": "EuroSys",
    "OSDI": "OSDI",
    "SOSP": "SOSP",
    "SIGCOMM": "SIGCOMM",
    "SIGMOD": "SIGMOD",
    "VLDB": "VLDB",
    "CHI": "CHI",
    "CVPR": "CVPR",
    "ICCV": "ICCV",
    "ISSTA": "ISSTA",
    "FSE": "FSE",
    "ASE": "ASE",
    "DSN": "DSN",
    "RAID": "RAID",
    "ESORICS": "ESORICS",
    "HOST": "HOST",
    "CAV": "CAV",
    "FM": "FM",
    "SIGSAC": "ACM CCS",
}


def _extract_venue_from_comment(comment: str) -> str:
    """从 ArXiv comment 中提取真实发表 venue"""
    if not comment:
        return ""

    # 先检查已知缩写
    for alias, full in _VENUE_ALIASES.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", comment, re.IGNORECASE):
            return full

    # 通用模式匹配
    for pattern in _VENUE_PATTERNS:
        m = pattern.search(comment)
        if m:
            venue = m.group(1).strip().rstrip(".,; (")
            # 去掉 leading "the " 或 "the 43rd " 之类
            venue = re.sub(r"^the\s+(?:\d+(?:st|nd|rd|th)\s+)?", "", venue, flags=re.IGNORECASE)
            if len(venue) > 3 and len(venue) < 120:
                if venue.lower() not in _VENUE_BLACKLIST:
                    return venue

    return ""


class ArxivClient(AbstractSearchClient):
    """ArXiv 论文搜索 (export.arxiv.org)

    无需 API Key，按相关性排序，支持布尔组合查询。
    自动从 comment 字段解析真实发表会议/期刊。
    """

    BASE_URL = "https://export.arxiv.org/api/query"

    async def search(self, keywords: list[str], limit: int = 10) -> list[Paper]:
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

                ns = {
                    "a": "http://www.w3.org/2005/Atom",
                    "arxiv": "http://arxiv.org/schemas/atom",
                }
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

                    # ArXiv comment 通常包含真实发表信息
                    comment_el = entry.find("arxiv:comment", ns)
                    comment = ""
                    if comment_el is not None and comment_el.text:
                        comment = comment_el.text

                    # 从 comment 提取真实 venue
                    venue = _extract_venue_from_comment(comment)

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

                    doi_el = entry.find("arxiv:doi", ns)
                    doi = ""
                    if doi_el is not None and doi_el.text:
                        doi = doi_el.text.strip()

                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""

                    papers.append(Paper(
                        title=title, authors=authors, year=year, venue=venue,
                        doi=doi, arxiv_id=arxiv_id, abstract=abstract,
                        source_url=source_url, pdf_url=pdf_url, source_api="arxiv",
                    ))
        except Exception as e:
            logger.error(f"ArXiv search error: {e}")
        return papers
