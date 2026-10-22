"""Exercise the real Jina/Qwen models without Zotero access or sending email."""

from pathlib import Path

from hydra import compose, initialize_config_dir
from openai import OpenAI

from zotero_arxiv_daily.local_llm import local_llm
from zotero_arxiv_daily.protocol import Paper
from zotero_arxiv_daily.reranker.local import LocalReranker


def main():
    with initialize_config_dir(config_dir=str(Path(__file__).resolve().parents[1] / "config"), version_base=None):
        config = compose(config_name="default")
    scores = LocalReranker(config).get_similarity_score(
        ["GPU kernel optimization and inference performance", "Marine biology and coral reef ecology"],
        ["GPU kernel optimization and inference performance"],
    )
    assert scores.shape == (2, 1) and scores[0, 0] > scores[1, 0]
    paper = Paper(
        source="smoke-test", title="Caching Repeated Computation in Language Model Inference",
        authors=["Example Author"], url="https://example.org/synthetic-paper",
        abstract="We propose caching repeated computation during language model inference. "
        "In a synthetic benchmark this reduces latency by 20 percent while preserving output quality.",
    )
    with local_llm(config.llm):
        with OpenAI(api_key=config.llm.api.key, base_url=config.llm.api.base_url, timeout=180, max_retries=0) as client:
            # Call the raising implementation, so API failures cannot pass as abstract fallback.
            summary = paper._generate_tldr_with_llm(client, config.llm)
    assert summary and "<think>" not in summary
    assert any("\u4e00" <= character <= "\u9fff" for character in summary)
    print(f"Local model smoke test passed. Chinese summary: {summary}")


if __name__ == "__main__":
    main()
