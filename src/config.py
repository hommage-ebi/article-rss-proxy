from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo


MAX_NJOBS = 8

# for rss gen
TODAY_JST = datetime.now(ZoneInfo("Asia/Tokyo"))

# for arxiv fetch
_CATEGORIES = [
    "cond-mat.mtrl-sci",
    "physics.chem-ph",
    "physics.comp-ph",
    "cs.AI",
    "cs.LG",
    "cs.CL",
]

# for llm
_INTERESTS = """\
- DFT・MD・MCなどの計算化学手法を機械学習で高速化する研究。ただし、流体や熱のPDEを解くものには興味がない。
- DFTの精度限界を超えるための新しい計算手法・機械学習手法の開発。ただし、量子コンピュータを用いるものには興味がない。
- 機械学習ポテンシャルを活用して材料の現象開明や探索を行う研究(この項目に関しては、機械学習ポテンシャルが関わらないものには興味がない)
- 計算化学手法を活用して半導体デバイス中の材料の現象開明や探索を行う研究。ただし、スピントロニクスには興味がない。
- 固相・液相・気相を問わず、合成可能性・合成レシピを計算化学で設計・予測する研究
- LLMの材料研究への活用\
"""


@dataclass
class Config:
    title: str = "今日のarXiv-AI4Science"  # TODO: arXiv以外も入るので適切な名前に変える
    deploy_url: str = "https://hommage-ebi.github.io/article-rss-proxy/"
    categories: list[str] = field(default_factory=lambda: _CATEGORIES)
    interests: str = _INTERESTS
