"""Keep the pre-refactor repository settings working without exposing Secrets."""

import os
import re
from collections.abc import Mapping

from omegaconf import DictConfig


def apply_legacy_environment(config: DictConfig, environ: Mapping[str, str] | None = None) -> None:
    env = os.environ if environ is None else environ
    # An explicitly supplied new-style configuration takes precedence.
    if env.get("CUSTOM_CONFIG", "").strip():
        return

    query = env.get("ARXIV_QUERY", "").strip()
    if query:
        categories = list(dict.fromkeys(re.split(r"[+,\s]+", query)))
        if not all(re.fullmatch(r"[a-zA-Z][a-zA-Z0-9-]*(?:\.[a-zA-Z0-9-]+)?", c) for c in categories):
            raise ValueError("ARXIV_QUERY must contain arXiv categories separated by '+' or commas.")
        config.source.arxiv.category = categories

    for name, section, key, convert in (
        ("SMTP_SERVER", "email", "smtp_server", str),
        ("SMTP_PORT", "email", "smtp_port", int),
        ("MAX_PAPER_NUM", "executor", "max_paper_num", int),
        ("LANGUAGE", "llm", "language", str),
    ):
        value = env.get(name, "").strip()
        if value:
            config[section][key] = convert(value)

    if config.executor.max_paper_num != -1 and config.executor.max_paper_num < 1:
        raise ValueError("MAX_PAPER_NUM must be -1 or a positive integer.")
