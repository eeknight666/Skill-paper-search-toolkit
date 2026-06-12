"""数据模型与公共基类"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class Paper:
    """论文实体"""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str = ""
    doi: str = ""
    arxiv_id: str = ""
    abstract: str = ""
    source_url: str = ""
    pdf_url: str = ""
    source_api: str = ""

    # 评估字段（由 evaluator 模块填充）
    relevance: str = ""        # 强相关 / 相关 / 弱相关 / 一般 / 无关
    category: str = ""          # 论文分类标签
    ccf_level: str = ""         # CCF 等级
    relevance_score: int = 0    # 内部评分

    @property
    def key(self) -> str:
        """去重键：优先 DOI，其次 arXiv ID，最后标题"""
        if self.doi:
            return self.doi.lower()
        if self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        return self.title.lower().strip().rstrip(".")[:100]

    def to_row(self) -> list[str]:
        """转为 Excel 行数据"""
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
        ]


class AbstractSearchClient(ABC):
    """搜索客户端抽象基类"""

    @abstractmethod
    async def search(self, keywords: list[str], limit: int = 10) -> list[Paper]:
        ...
