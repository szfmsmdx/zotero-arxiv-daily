"""Validate an owner-created paper-rating Issue and update the feedback table."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, urlunsplit


def canonical_arxiv_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme != "https" or parsed.netloc.lower() != "arxiv.org":
        raise ValueError("Paper URL must be an https arXiv abstract link.")
    if not parsed.path.startswith("/abs/"):
        raise ValueError("Paper URL must use the /abs/ path.")
    paper_id = re.sub(r"v\d+$", "", parsed.path.removeprefix("/abs/"))
    if not re.fullmatch(r"[A-Za-z0-9.\-/]+", paper_id):
        raise ValueError("Invalid arXiv identifier.")
    return urlunsplit(("https", "arxiv.org", f"/abs/{paper_id}", "", ""))


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_records(path: Path) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    records = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = split_markdown_row(line)
        if len(cells) != 4 or cells[0] == "论文名":
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        title, url, raw_score, tldr = cells
        try:
            canonical_url = canonical_arxiv_url(url)
        except ValueError:
            continue
        score = int(raw_score) if raw_score in {"1", "2", "3", "4", "5"} else None
        records.append({"title": title, "url": canonical_url, "score": score, "tldr": tldr})
    return text, records


def clean_cell(value: str) -> str:
    return str(value).replace("|", "／").replace("\r", " ").replace("\n", " ").strip()


def write_records(path: Path, records: list[dict]) -> None:
    lines = [
        "# Paper feedback and ranking seeds",
        "",
        "Scores 1–5 are explicit preference ratings. A blank score means the paper was mailed but not rated; blank-score rows are not positive seeds and contribute only a very small negative signal.",
        "",
        "| 论文名 | arXiv 页面链接 | 打分 | TLDR（核心贡献） |",
        "| --- | --- | ---: | --- |",
    ]
    for record in records:
        score = record["score"] if record["score"] is not None else ""
        lines.append(
            f"| {clean_cell(record['title'])} | {record['url']} | {score} | {clean_cell(record['tldr'])} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def process_event(event_path: Path, ratings_path: Path) -> None:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    issue = event.get("issue", {})
    repository = event.get("repository", {})
    owner = (repository.get("owner") or {}).get("login") or repository.get("full_name", "").split("/")[0]
    author = (issue.get("user") or {}).get("login")
    if not owner or author != owner:
        raise ValueError("Only an Issue opened by the repository owner can record a rating.")

    title_match = re.fullmatch(r"\[Paper Rating\] ([1-5])/5", issue.get("title", ""))
    if not title_match:
        raise ValueError("Issue title must match [Paper Rating] N/5.")
    title_score = int(title_match.group(1))

    body = (issue.get("body") or "").replace("\r\n", "\n").replace("\r", "\n")
    body_match = re.fullmatch(
        r"Paper title: ([^\n]+)\nPaper URL: ([^\n]+)\nRating: ([1-5])\nCore TLDR: ([^\n]+)",
        body,
    )
    if not body_match:
        raise ValueError("Issue body must contain Paper title, Paper URL, Rating, and Core TLDR on separate lines.")
    paper_title, raw_url, raw_score, tldr = body_match.groups()
    score = int(raw_score)
    if score != title_score:
        raise ValueError("Issue title score and body rating must match.")
    paper_url = canonical_arxiv_url(raw_url)
    if not isinstance(paper_title, str) or not paper_title.strip() or len(paper_title) > 500:
        raise ValueError("Paper title is missing or too long.")
    if not isinstance(tldr, str) or not tldr.strip() or len(tldr) > 2000:
        raise ValueError("Paper TLDR is missing or too long.")

    _, records = read_records(ratings_path)
    by_url = {record["url"]: record for record in records}
    by_url[paper_url] = {
        "title": paper_title.strip(),
        "url": paper_url,
        "score": score,
        "tldr": tldr.strip(),
    }
    write_records(ratings_path, list(by_url.values()))
    print(f"Recorded {score}/5 for {paper_url}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: process_rating_issue.py EVENT_JSON RATINGS_MD")
    process_event(Path(sys.argv[1]), Path(sys.argv[2]))
