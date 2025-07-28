import logging
from pathlib import Path

from feedgen.feed import FeedGenerator

from src.arxiv_fetcher import Paper
from src.config import DEPLOY_URL, TODAY_JST


def generate_rss_file(pushing_papers: list[Paper], other_papers: list[Paper], xml_path: Path):
    fg = FeedGenerator()
    fg.id(DEPLOY_URL)
    fg.link(href=DEPLOY_URL, rel="alternate")
    TITLE = "今日のarXiv-AI4Science" # TODO: arXiv以外も入るので適切な名前に変える
    fg.title(TITLE)
    fg.description(TITLE)
    fg.language("ja")

    for p in pushing_papers:
        fe = fg.add_entry()
        fe.id(p.id)
        fe.title(p.title)
        fe.link(href=p.link.replace("arxiv.org/abs", "alphaxiv.org/overview"))
        fe.pubDate(p.updated)
        fe.description(
            (p.summary_ja if p.summary_ja else p.summary)
            + "\n\n"
            + f'<img src="{p.fig1}"/>'
            + "<p>"
            + ", ".join(p.authors)
            + "</p>"
            + "<p>"
            + "\n".join(p.affils)
            + "</p>"
        )

    if other_papers:
        fe = fg.add_entry()
        fe.id(f"other-papers-{TODAY_JST.strftime('%Y-%m-%d')}")
        fe.title(f"other arxiv papers {TODAY_JST.strftime('%Y-%m-%d')}")
        fe.link(href=f"https://arxiv.org/{TODAY_JST.strftime('%Y-%m-%d')}")  # dummy
        fe.pubDate(TODAY_JST)
        fe.description(
            "<ol>\n<li>"
            + "</li>\n<li>".join([f'<a href="{p.link}">{p.title}</a>' for p in other_papers])
            + "</li>\n</ol>"
        )

    fg.rss_file(xml_path)
    logging.info("RSS written to %s", xml_path)
