import json
import logging
import os
import time

from dotenv import load_dotenv
from google import genai
import google.genai.errors
from joblib import delayed, Parallel

from src.arxiv_fetcher import Paper
from src.config import Config, MAX_NJOBS


load_dotenv()
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def ask_gemini(prompt: str, model: str) -> str:
    """
    model:
    - gemini-2.5-pro: 5RPM 100RPD
    - gemini-2.5-flash: 10RPM 250RPD
    - gemini-2.0-flash: 15RPM 200RPD
    """
    for _ in range(10):
        try:
            res = _client.models.generate_content(
                model=model, contents=prompt, config={"temperature": 0.0}
            )
            return res.text.strip()
        except google.genai.errors.APIError as e:
            if hasattr(e, "code") and e.code in [429, 500, 502, 503]:
                logging.warning(f"Gemini API error: {e}")
                delay = 61
                if e.code == 429:
                    try:
                        delay = int(e.details["error"]["details"][-1]["retryDelay"][:-1]) + 1
                    except Exception as e2:
                        logging.warning(
                            f"Failed to parse retry delay: {e2}. Using default {delay} seconds."
                        )
                logging.info(f"Retrying after {delay} seconds...")
                time.sleep(delay)
                continue
            else:
                raise
    raise RuntimeError("Max retries exceeded.")


RECOMMEND_PROMPT = """\
あなたの役割は論文のタイトルとAbstractを読んで、読者の興味を引くかどうかを判定することです。

読者の関心領域は
{INTERESTS}
と多岐にわたります。

以下に論文タイトルとAbstractのペアが複数与えられるのでyes/noで判定してください。返答はjson形式で
{"0": "yes", "1": "no", ...}
のようにしてください。
----------
"""


def recommend_batch(papers_batch: list[Paper], wait=True) -> list[bool]:
    papers_batch_str = ""
    for i, paper in enumerate(papers_batch):
        title = paper.title.replace("\n", " ")
        papers_batch_str += f"[{i}] {title}\nAbstract: {paper.summary}\n----------\n"
    interests = Config().interests
    res_batch = ask_gemini(
        RECOMMEND_PROMPT.replace("{INTERESTS}", interests) + papers_batch_str, "gemini-2.5-flash"
    )
    if wait:
        time.sleep(60)
    res_batch_dict = json.loads(res_batch.replace("```json", "").replace("```", ""))
    return [res_batch_dict.get(str(i), "no") == "yes" for i in range(len(papers_batch))]


def recommend_papers(papers: list[Paper], batch_size: int = 25) -> list[bool]:
    n_batches = (len(papers) + batch_size - 1) // batch_size
    n_jobs = max(1, min(MAX_NJOBS, n_batches))

    def _get_batch(idx):
        start = batch_size * idx
        end = min(batch_size * (idx + 1), len(papers))
        return papers[start:end]

    res = Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(recommend_batch)(_get_batch(i)) for i in range(n_batches)
    )
    return sum(res, [])


def translate_abstract(paper: Paper, wait=True) -> str:
    prompt = (
        f"以下を日本語に翻訳してください。翻訳結果のみを答えてください。\n"
        f"---\n{paper.summary}\n---"
    )
    translated = ask_gemini(prompt, "gemini-2.0-flash")
    if wait:
        time.sleep(60)
    return translated
