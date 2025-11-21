from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta, timezone
import logging
import re
from typing import TYPE_CHECKING

import feedparser
import requests

from src.config import Config


if TYPE_CHECKING:
    from datetime import datetime


ARXIV_API_URL = (
    "http://export.arxiv.org/api/query?"
    "search_query=cat:{cat}+AND+submittedDate:[{start}+TO+{end}]"
    "&start=0&max_results=1000"
)


@dataclass
class Paper:
    id: str
    title: str
    link: str
    summary: str
    category: str
    updated: str
    summary_ja: str = ""
    fig1: str = ""
    authors: list = field(default_factory=list)
    affils: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "category": self.category,
            "updated": self.updated,
            "summary_ja": self.summary_ja,
            "fig1": self.fig1,
            "authors": self.authors,
            "affils": self.affils,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Paper":
        return cls(
            id=d["id"],
            title=d["title"],
            link=d["link"],
            summary=d["summary"],
            category=d["category"],
            updated=d["updated"],
            summary_ja=d.get("summary_ja", ""),
            fig1=d.get("fig1", ""),
            authors=d.get("authors", []),
            affils=d.get("affils", []),
        )


def jst_date_to_arxiv_range(date_jst: datetime) -> tuple[str, str]:
    """
    arXivはJST10:00更新。前日の11:00~今日の11:00の24hの論文を取得するためのstringを返す。
    火曜日の場合は金曜11:00~
    """
    date_jst11 = date_jst.replace(hour=11, minute=0, second=0, microsecond=0)
    end_utc = date_jst11.astimezone(timezone.utc)
    days_back = 4 if date_jst.weekday() == 1 else 1
    start_utc = end_utc - timedelta(days=days_back)
    return start_utc.strftime("%Y%m%d%H%M"), end_utc.strftime("%Y%m%d%H%M")


def fetch_papers_for_date(date_jst: datetime) -> list[Paper]:
    start_str, end_str = jst_date_to_arxiv_range(date_jst)
    papers: list[Paper] = []
    categories = Config().categories
    for cat in categories:
        url = ARXIV_API_URL.format(cat=cat, start=start_str, end=end_str)
        try:
            response = requests.get(url, timeout=30)
            feed = feedparser.parse(response.text)
            for entry in feed.entries:
                paper = Paper(
                    id=entry.id.split("/")[-1],
                    title=re.sub(r"\s+", " ", entry.title).strip(),
                    link=entry.link,
                    summary=entry.summary.strip(),
                    authors=[a.name for a in entry.authors],
                    category=cat,
                    updated=entry.updated,
                )
                papers.append(paper)
        except Exception as e:
            logging.error(f"Error fetching papers for category {cat}: {e}")
    seen = set()
    unique_papers = []
    for paper in papers:
        if paper.id not in seen:
            unique_papers.append(paper)
            seen.add(paper.id)
    return unique_papers
