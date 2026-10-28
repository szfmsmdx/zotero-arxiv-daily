"""Read public paper feedback and build signed email rating links."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from urllib.parse import urlencode, urlsplit, urlunsplit

from loguru import logger
from omegaconf import DictConfig

from .protocol import Paper


@dataclass(frozen=True)
class FeedbackPaper:
    title: str
    url: str
    score: int | None
    tldr: str

    @property
    def ranking_text(self) -> str:
        return f"Title: {self.title}\nCore contribution: {self.tldr}".strip()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def feedback_file_path(config: DictConfig | None = None) -> Path:
    configured = None
    if config is not None:
        section = config.get("feedback", {})
        configured = section.get("ratings_file") if section else None
    path = Path(configured or "feedback/ratings.md")
    return path if path.is_absolute() else _project_root() / path


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def load_feedback(path: Path) -> list[FeedbackPaper]:
    """Load four-column feedback rows; blank ratings represent sent, unrated papers."""
    if not path.exists():
        logger.warning("Feedback file not found at {}; ranking without feedback", path)
        return []

    records: list[FeedbackPaper] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _split_row(line)
        if len(cells) != 4 or cells[0] in {"论文名", "---"} or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        title, url, raw_score, tldr = cells
        try:
            score = int(raw_score) if raw_score else None
        except ValueError:
            logger.warning("Ignoring invalid feedback score {!r} for {}", raw_score, title)
            continue
        if score is not None and score not in range(1, 6):
            logger.warning("Ignoring feedback score outside 1-5 for {}", title)
            continue
        if url and tldr:
            records.append(FeedbackPaper(title=title, url=url, score=score, tldr=tldr))
    return records


def _clean_cell(value: str) -> str:
    return str(value or "").replace("|", "／").replace("\r", " ").replace("\n", " ").strip()


def save_feedback(path: Path, records: list[FeedbackPaper]) -> None:
    rows = [
        f"| {_clean_cell(record.title)} | {_clean_cell(record.url)} | {record.score if record.score is not None else ''} | {_clean_cell(record.tldr)} |"
        for record in records
    ]
    content = (
        "# Paper feedback and ranking seeds\n\n"
        "Scores 1–5 are explicit ratings. A blank score means the paper was mailed but not rated; "
        "blank-score rows are not positive seeds and contribute only a very small negative signal.\n\n"
        "| 论文名 | arXiv 页面链接 | 打分 | TLDR（核心贡献） |\n"
        "| --- | --- | ---: | --- |\n"
        + "\n".join(rows)
        + ("\n" if rows else "")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def canonical_paper_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if parsed.netloc.lower() == "arxiv.org":
        path = parsed.path.replace("/pdf/", "/abs/", 1)
        path = path.removesuffix(".pdf")
        path = re.sub(r"v\d+$", "", path)
        return urlunsplit(("https", "arxiv.org", path, "", ""))
    return url


class FeedbackClient:
    """Creates prefilled GitHub Issue rating links and logs sent papers locally."""

    def __init__(self, config: DictConfig):
        section = config.get("feedback", {})
        self.path = feedback_file_path(config)
        self.repository = str(
            section.get("repository")
            or os.environ.get("FEEDBACK_REPOSITORY")
            or "szfmsmdx/zotero-arxiv-daily"
        ).strip("/")

    def rating_links(self, papers: list[Paper]) -> dict[str, dict[int, str]]:
        result: dict[str, dict[int, str]] = {}
        for paper in papers:
            paper_url = canonical_paper_url(paper.url)
            paper_links: dict[int, str] = {}
            for score in range(1, 6):
                body = (
                    f"Paper title: {_clean_cell(paper.title)}\n"
                    f"Paper URL: {paper_url}\n"
                    f"Rating: {score}\n"
                    f"Core TLDR: {_clean_cell(paper.tldr or '')}"
                )
                query = urlencode({"title": f"[Paper Rating] {score}/5", "body": body})
                paper_links[score] = f"https://github.com/{self.repository}/issues/new?{query}"
            result[paper.url] = paper_links
        return result

    def register_sent(self, papers: list[Paper]) -> None:
        if not papers:
            return
        path = self.path
        records = load_feedback(path)
        by_url = {record.url: record for record in records}
        for paper in papers:
            url = canonical_paper_url(paper.url)
            previous = by_url.get(url)
            if previous:
                by_url[url] = FeedbackPaper(
                    title=paper.title or previous.title,
                    url=url,
                    score=previous.score,
                    tldr=paper.tldr or previous.tldr,
                )
            else:
                by_url[url] = FeedbackPaper(
                    title=paper.title,
                    url=url,
                    score=None,
                    tldr=paper.tldr or "",
                )
        save_feedback(path, list(by_url.values()))
