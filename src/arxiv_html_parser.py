import logging
from typing import Dict, Tuple

from bs4 import BeautifulSoup
import requests


def _get_arxiv_html_soup(arxiv_id: str) -> Tuple[int, BeautifulSoup]:
    try:
        resp = requests.get(f"https://arxiv.org/html/{arxiv_id}", timeout=30)
        return resp.status_code, BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logging.error(f"Failed to fetch HTML for paper {arxiv_id}: {e}")
        return 500, BeautifulSoup("", "html.parser")


def extract_fig1_authors_affils(arxiv_id: str) -> Dict:
    status, soup = _get_arxiv_html_soup(arxiv_id)
    if status != 200:
        return {"fig1": "", "authors": [], "affils": []}

    figs = []
    try:
        figure_imgs = soup.select(".ltx_figure > img")
        figure_captions = soup.select(".ltx_figure > figcaption")

        for img, cap in zip(figure_imgs, figure_captions):
            try:
                figs.append(
                    {
                        "src": f"https://arxiv.org/html/{arxiv_id}/{img['src']}",
                        "caption": cap.get_text(strip=True),
                    }
                )
            except Exception as e:
                logging.error(f"Error processing figure for paper {arxiv_id}: {e}")
    except Exception as e:
        logging.error(f"Error extracting figures for paper {arxiv_id}: {e}")
    fig1 = figs[0]["src"] if figs else ""

    authors, affils = set(), set()
    section = soup.find("div", class_="ltx_authors")
    if section:
        person_spans = section.find_all("span", class_="ltx_personname")
        for p in person_spans:
            if p:
                try:
                    for t in p.find_all(["sup", "span"]):
                        t.decompose()
                    authors.update(
                        [
                            n.strip()
                            for n in p.get_text(" ", strip=True).replace(" and ", ",").split(",")
                            if n.strip()
                        ]
                    )
                except Exception as e:
                    logging.error(f"Error processing author element for paper {arxiv_id}: {e}")

        contact_spans = section.find_all("span", class_="ltx_contact")
        for c in contact_spans:
            if c:
                try:
                    txt = c.get_text(" ", strip=True)
                    if "@" not in txt.lower():
                        affils.add(txt)
                except Exception as e:
                    logging.error(
                        f"Error processing affiliation element for paper {arxiv_id}: {e}"
                    )

    return {"fig1": fig1, "authors": sorted(authors), "affils": sorted(affils)}
