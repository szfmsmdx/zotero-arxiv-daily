from abc import ABC, abstractmethod
from omegaconf import DictConfig
from ..protocol import Paper, CorpusPaper
import numpy as np
from typing import Type
class BaseReranker(ABC):
    def __init__(self, config:DictConfig):
        self.config = config

    def rerank(self, candidates:list[Paper], corpus:list) -> list[Paper]:
        if not candidates:
            return candidates
        if not corpus:
            for paper in candidates:
                paper.score = 0.0
            return candidates
        if corpus and hasattr(corpus[0], "tldr") and hasattr(corpus[0], "score"):
            return self._rerank_with_feedback(candidates, corpus)

        # Keep the legacy corpus path available for callers that still provide Zotero
        # papers. The daily executor now supplies the explicitly rated feedback set.
        corpus = sorted(corpus,key=lambda x: x.added_date,reverse=True)
        time_decay_weight = 1 / (1 + np.log10(np.arange(len(corpus)) + 1))
        time_decay_weight: np.ndarray = time_decay_weight / time_decay_weight.sum()
        sim = self.get_similarity_score([c.abstract for c in candidates], [c.abstract for c in corpus])
        assert sim.shape == (len(candidates), len(corpus))
        scores = (sim * time_decay_weight).sum(axis=1) * 10 # [n_candidate]
        for s,c in zip(scores,candidates):
            c.score = s
        candidates = sorted(candidates,key=lambda x: x.score,reverse=True)
        return candidates

    def _rerank_with_feedback(self, candidates: list[Paper], feedback: list) -> list[Paper]:
        if not candidates:
            return candidates

        candidate_texts = [f"Title: {paper.title}\nAbstract: {paper.abstract}".strip() for paper in candidates]
        preference_texts = [paper.ranking_text for paper in feedback]
        similarities = self.get_similarity_score(candidate_texts, preference_texts)
        assert similarities.shape == (len(candidates), len(feedback))

        positive_indices = [i for i, paper in enumerate(feedback) if paper.score is not None and paper.score > 3]
        positive_weights = np.array([feedback[i].score - 3 for i in positive_indices], dtype=float)
        negative_indices = [i for i, paper in enumerate(feedback) if paper.score is not None and paper.score < 3]
        negative_weights = np.array([3 - feedback[i].score for i in negative_indices], dtype=float)
        unrated_indices = [i for i, paper in enumerate(feedback) if paper.score is None]

        if positive_indices:
            positive_signal = (
                similarities[:, positive_indices] * positive_weights
            ).sum(axis=1) / positive_weights.sum()
        else:
            positive_signal = np.zeros(len(candidates), dtype=float)

        if negative_indices:
            negative_signal = (
                similarities[:, negative_indices] * negative_weights
            ).sum(axis=1) / negative_weights.sum()
        else:
            negative_signal = np.zeros(len(candidates), dtype=float)

        if unrated_indices:
            # Silence after delivery is deliberately only a 2.5% signal. Average it
            # across exposures so that a growing log cannot swamp explicit ratings.
            unrated_signal = similarities[:, unrated_indices].mean(axis=1) * 0.025
        else:
            unrated_signal = np.zeros(len(candidates), dtype=float)

        preference_score = positive_signal - 0.5 * negative_signal - unrated_signal
        for paper, score in zip(candidates, preference_score):
            # Map cosine-derived preference to the familiar 0-10 display range.
            paper.score = float((score + 1.0) * 5.0)
        return sorted(candidates, key=lambda paper: paper.score, reverse=True)
    
    @abstractmethod
    def get_similarity_score(self, s1:list[str], s2:list[str]) -> np.ndarray:
        raise NotImplementedError

registered_rerankers = {}

def register_reranker(name:str):
    def decorator(cls):
        registered_rerankers[name] = cls
        return cls
    return decorator

def get_reranker_cls(name:str) -> Type[BaseReranker]:
    if name not in registered_rerankers:
        raise ValueError(f"Reranker {name} not found")
    return registered_rerankers[name]
