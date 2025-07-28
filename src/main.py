from __future__ import annotations

import argparse
from datetime import datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from joblib import delayed, Parallel

from src.arxiv_fetcher import fetch_papers_for_date
from src.arxiv_html_parser import extract_fig1_authors_affils
from src.config import MAX_NJOBS, TODAY_JST
from src.llm_utils import recommend_papers, translate_abstract
from src.rss_generator import generate_rss_file


if TYPE_CHECKING:
    from src.arxiv_fetcher import Paper


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yymmdd", type=str, default=None, help="日付 (YYMMDD)。省略時は今日")
    args = parser.parse_args()

    if args.yymmdd is not None:
        yymmdd = args.yymmdd
    else:
        yymmdd = TODAY_JST.strftime("%y%m%d")
        logging.info(f"yymmdd is not specified. Using today: {yymmdd}")

    fetched_papers = fetch_papers_for_date(
        datetime.strptime(yymmdd, "%y%m%d").replace(tzinfo=ZoneInfo("Asia/Tokyo"))
    )
    logging.info(f"Fetched {len(fetched_papers)} papers.")

    are_recommended = recommend_papers(fetched_papers)
    recommended_papers: list[Paper] = []
    other_papers = []
    for is_recommended, paper in zip(are_recommended, fetched_papers):
        if is_recommended:
            recommended_papers.append(paper)
        else:
            other_papers.append(paper)
    logging.info(f"Recommend {len(recommended_papers)} papers.")

    abstract_jas = Parallel(n_jobs=MAX_NJOBS, backend="threading")(
        delayed(translate_abstract)(paper) for paper in recommended_papers
    )
    for abstract_ja, paper in zip(abstract_jas, recommended_papers):
        paper.summary_ja = abstract_ja
    translated_papers = recommended_papers
    logging.info("Translate Done.")

    extracted_results = Parallel(n_jobs=MAX_NJOBS, backend="threading")(
        delayed(extract_fig1_authors_affils)(paper.id) for paper in translated_papers
    )
    for extracted, paper in zip(extracted_results, translated_papers):
        paper.fig1 = extracted["fig1"]
        paper.authors = extracted["authors"] if extracted["authors"] else paper.authors
        paper.affils = extracted["affils"]
    pushing_papers = translated_papers
    logging.info("Extract Done.")

    generate_rss_file(
        pushing_papers, other_papers, Path(__file__).parent.parent / "docs/index.xml"
    )


if __name__ == "__main__":
    main()
