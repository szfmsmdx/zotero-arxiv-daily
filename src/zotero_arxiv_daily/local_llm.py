"""Run a GGUF model behind the existing chat-completion client, on loopback only."""

from contextlib import contextmanager
import json
import os
import subprocess
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

from huggingface_hub import hf_hub_download
from loguru import logger
from omegaconf import DictConfig


@contextmanager
def local_llm(config: DictConfig):
    backend = config.get("backend", "api")
    if backend == "api":
        yield
        return
    if backend != "local":
        raise ValueError("llm.backend must be 'local' or 'api'.")
    if config.api_mode != "chat_completion":
        raise ValueError("Local GGUF inference requires llm.api_mode=chat_completion.")

    settings = config.local
    port = int(settings.port)
    if config.api.base_url.rstrip("/") != f"http://127.0.0.1:{port}/v1":
        raise ValueError("Local LLM base_url must match its loopback address and port.")
    logger.info("Preparing local GGUF model: {}", settings.filename)
    model_path = hf_hub_download(
        repo_id=settings.repo_id,
        filename=settings.filename,
        revision=settings.revision,
    )
    command = [
        settings.server_binary,
        "--model", model_path,
        "--alias", config.generation_kwargs.model,
        "--host", "127.0.0.1",
        "--port", str(port),
        "--ctx-size", str(settings.context_size),
        "--threads", str(settings.threads),
        "--parallel", "1",
        "--n-gpu-layers", "0",
        "--jinja",
        "--chat-template-kwargs", json.dumps({"enable_thinking": False}),
        "--reasoning-budget", "0",
    ]
    with tempfile.TemporaryFile(mode="w+b") as log:
        kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        process = subprocess.Popen(command, stdout=log, stderr=log, **kwargs)
        try:
            deadline = time.monotonic() + float(settings.startup_timeout)
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    log.seek(0)
                    details = log.read().decode("utf-8", errors="replace")[-4000:]
                    raise RuntimeError(f"llama-server exited before becoming ready:\n{details}")
                try:
                    with urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
                        if response.status == 200:
                            logger.info("Local Qwen model is ready (thinking disabled)")
                            break
                except (URLError, TimeoutError):
                    pass
                time.sleep(1)
            else:
                raise TimeoutError("Local Qwen model did not become ready before its startup timeout.")
            yield
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=15)
