from dataclasses import dataclass
from typing import Optional, TypeVar
from datetime import datetime
import re
import tiktoken
from openai import OpenAI
from loguru import logger
import json
RawPaperItem = TypeVar('RawPaperItem')


def _request_llm(openai_client: OpenAI, llm_params: dict, messages: list[dict]) -> str:
    api_mode = llm_params.get("api_mode", "chat_completion")
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))

    if api_mode == "chat_completion":
        response = openai_client.chat.completions.create(
            messages=messages,
            **generation_kwargs,
        )
        return response.choices[0].message.content

    if api_mode == "response":
        max_tokens = generation_kwargs.pop("max_tokens", None)
        if max_tokens is not None and "max_output_tokens" not in generation_kwargs:
            generation_kwargs["max_output_tokens"] = max_tokens
        response = openai_client.responses.create(
            input=messages,
            **generation_kwargs,
        )
        return response.output_text

    raise ValueError(
        f"Unsupported llm.api_mode: {api_mode}. "
        "Expected 'chat_completion' or 'response'."
    )


@dataclass
class Paper:
    source: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    pdf_url: Optional[str] = None
    full_text: Optional[str] = None
    tldr: Optional[str] = None
    introduction: Optional[str] = None
    affiliations: Optional[list[str]] = None
    score: Optional[float] = None

    def _build_summary_prompt(self, instruction: str, llm_params: dict) -> str:
        lang = llm_params.get('language', 'English')
        prompt = f"{instruction.strip()}\n\n"
        if self.title:
            prompt += f"Title:\n {self.title}\n\n"

        if self.abstract:
            prompt += f"Abstract: {self.abstract}\n\n"

        if self.full_text:
            prompt += f"Preview of main content:\n {self.full_text}\n\n"

        if not self.full_text and not self.abstract:
            logger.warning(f"Neither full text nor abstract is provided for {self.url}")
            return ""
        
        # use gpt-4o tokenizer for estimation
        enc = tiktoken.encoding_for_model("gpt-4o")
        prompt_tokens = enc.encode(prompt)
        prompt_tokens = prompt_tokens[:4000]  # truncate to 4000 tokens
        prompt = enc.decode(prompt_tokens)

        return prompt

    def _generate_tldr_with_llm(self, openai_client:OpenAI,llm_params:dict) -> str:
        lang = llm_params.get('language', 'English')
        prompt = self._build_summary_prompt(
            f"Write exactly one sentence in {lang} that states this paper's core contribution. "
            "Be concrete about what the paper changes or enables. Use only the supplied information; "
            "do not add background, evaluation claims, or unsupported details. "
            "Format emphasis with Markdown. Put a normal space after closing **bold** or *italic* "
            "markers whenever prose follows, including Chinese text (for example, `**term** 后续`). "
            "For inline equations, use single-dollar LaTeX delimiters like `$x^2$ 后续`; use only "
            "standard Matplotlib Mathtext commands and do not use raw HTML.",
            llm_params,
        )
        if not prompt:
            return "Failed to generate TLDR. Neither full text nor abstract is provided"
        return _request_llm(
            openai_client,
            llm_params,
            [
                {
                    "role": "system",
                    "content": f"You write precise one-sentence scientific paper contribution summaries in {lang}.",
                },
                {"role": "user", "content": prompt},
            ],
        )

    def _generate_introduction_with_llm(self, openai_client: OpenAI, llm_params: dict) -> str:
        lang = llm_params.get('language', 'English')
        prompt = self._build_summary_prompt(
            f"Write a structured, specific introduction to this paper in {lang}, using only the information below. "
            "Use these four sections in this order, with headings written in the requested language:\n"
            "1. Field, background, and problem: identify the research area, context, and concrete problem or limitation addressed.\n"
            "2. Method: first give a brief overview in a few sentences, then list the main steps or components as concise bullets.\n"
            "3. Results: report the main findings, including quantitative results, baselines, and evaluation conditions when provided. Do not invent missing numbers.\n"
            "4. Underlying idea and transferability: explain the broader problem-solving idea and whether it resembles an established idea from another area, such as computer architecture or operating systems. Suggest where it could transfer and why. Separate paper claims from your interpretation.\n\n"
            "Keep each section concise but informative. Avoid generic praise and unsupported claims. If the information does not cover a section, say so.\n\n"
            "Formatting requirements for the email: use Markdown emphasis and lists, not raw HTML. Put a normal space after closing **bold** or *italic* markers whenever prose follows, including Chinese text (for example, `**term** 后续`). For inline equations, use single-dollar LaTeX delimiters like `$x^2$ 后续`; use only standard Matplotlib Mathtext commands. Do not use display equations or `\\(...\\)` delimiters.",
            llm_params,
        )
        if not prompt:
            return ""
        return _request_llm(
            openai_client,
            llm_params,
            [
                {
                    "role": "system",
                    "content": f"You are a careful research assistant. Distinguish reported facts from your analysis and do not invent details. Write in {lang}.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    
    def generate_tldr(self, openai_client:OpenAI,llm_params:dict) -> str:
        try:
            tldr = self._generate_tldr_with_llm(openai_client,llm_params)
            self.tldr = tldr
            return tldr
        except Exception as e:
            logger.warning(f"Failed to generate tldr of {self.url}: {e}")
            tldr = self._fallback_tldr()
            self.tldr = tldr
            return tldr

    def _fallback_tldr(self) -> str:
        text = (self.abstract or "").strip()
        if not text:
            return "Failed to generate TLDR. Neither full text nor abstract is provided"
        sentence = re.split(r"(?<=[.!?。！？])\s+", text, maxsplit=1)[0]
        return sentence if len(sentence) <= 320 else sentence[:317].rstrip() + "..."

    def generate_introduction(self, openai_client: OpenAI, llm_params: dict) -> str:
        """Generate the detailed email explanation in a separate LLM call from the TLDR."""
        try:
            self.introduction = self._generate_introduction_with_llm(openai_client, llm_params)
        except Exception as e:
            logger.warning(f"Failed to generate introduction of {self.url}: {e}")
            self.introduction = self.abstract or "Introduction unavailable."
        return self.introduction

    def _generate_affiliations_with_llm(self, openai_client:OpenAI,llm_params:dict) -> Optional[list[str]]:
        if self.full_text is not None:
            prompt = f"Given the beginning of a paper, extract the affiliations of the authors in a python list format, which is sorted by the author order. If there is no affiliation found, return an empty list '[]':\n\n{self.full_text}"
            # use gpt-4o tokenizer for estimation
            enc = tiktoken.encoding_for_model("gpt-4o")
            prompt_tokens = enc.encode(prompt)
            prompt_tokens = prompt_tokens[:2000]  # truncate to 2000 tokens
            prompt = enc.decode(prompt_tokens)
            affiliations = _request_llm(
                openai_client,
                llm_params,
                [
                    {
                        "role": "system",
                        "content": "You are an assistant who perfectly extracts affiliations of authors from a paper. You should return a python list of affiliations sorted by the author order, like [\"TsingHua University\",\"Peking University\"]. If an affiliation is consisted of multi-level affiliations, like 'Department of Computer Science, TsingHua University', you should return the top-level affiliation 'TsingHua University' only. Do not contain duplicated affiliations. If there is no affiliation found, you should return an empty list [ ]. You should only return the final list of affiliations, and do not return any intermediate results.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            affiliations = re.search(r'\[.*?\]', affiliations, flags=re.DOTALL).group(0)
            affiliations = json.loads(affiliations)
            affiliations = list(set(affiliations))
            affiliations = [str(a) for a in affiliations]

            return affiliations
    
    def generate_affiliations(self, openai_client:OpenAI,llm_params:dict) -> Optional[list[str]]:
        try:
            affiliations = self._generate_affiliations_with_llm(openai_client,llm_params)
            self.affiliations = affiliations
            return affiliations
        except Exception as e:
            logger.warning(f"Failed to generate affiliations of {self.url}: {e}")
            self.affiliations = None
            return None
@dataclass
class CorpusPaper:
    title: str
    abstract: str
    added_date: datetime
    paths: list[str]
