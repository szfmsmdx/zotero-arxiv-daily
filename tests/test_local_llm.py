import pytest
from omegaconf import OmegaConf

from zotero_arxiv_daily import local_llm as local_module


def local_config():
    return OmegaConf.create({
        "backend": "local", "api_mode": "chat_completion",
        "api": {"base_url": "http://127.0.0.1:8080/v1"},
        "generation_kwargs": {"model": "qwen3.5-4b"},
        "local": {"repo_id": "test/model", "filename": "model.gguf", "revision": "pinned",
                  "server_binary": "llama-server", "port": 8080, "context_size": 8192,
                  "threads": 4, "startup_timeout": 3},
    })


def test_api_backend_does_not_download_or_launch(monkeypatch):
    monkeypatch.setattr(local_module, "hf_hub_download", lambda **kw: pytest.fail("Unexpected model download"))
    with local_module.local_llm(OmegaConf.create({"backend": "api"})):
        pass


def patch_server(monkeypatch, *, exit_code=None):
    calls = []

    class Process:
        def poll(self):
            return exit_code

        def terminate(self):
            calls.append("terminate")

        def kill(self):
            calls.append("kill")

        def wait(self, **kwargs):
            calls.append("wait")

    def launch(command, **kwargs):
        calls.append(command)
        return Process()

    monkeypatch.setattr(local_module, "hf_hub_download", lambda **kw: "cached-model.gguf")
    monkeypatch.setattr(local_module.subprocess, "Popen", launch)
    return calls


def test_ready_server_is_stopped_even_if_generation_fails(monkeypatch):
    calls = patch_server(monkeypatch)

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(local_module, "urlopen", lambda *a, **kw: Response())
    with pytest.raises(RuntimeError, match="generation failed"):
        with local_module.local_llm(local_config()):
            raise RuntimeError("generation failed")
    command = calls[0]
    assert command[command.index("--host") + 1] == "127.0.0.1"
    assert command[command.index("--reasoning-budget") + 1] == "0"
    assert calls[-2:] == ["terminate", "wait"]


def test_exited_server_fails_before_any_summary(monkeypatch):
    calls = patch_server(monkeypatch, exit_code=1)
    with pytest.raises(RuntimeError, match="exited before becoming ready"):
        with local_module.local_llm(local_config()):
            pytest.fail("Must not generate with a failed server")
    assert "terminate" not in calls


def test_startup_timeout_stops_process(monkeypatch):
    calls = patch_server(monkeypatch)
    times = iter([0, 10])
    monkeypatch.setattr(local_module.time, "monotonic", lambda: next(times))
    with pytest.raises(TimeoutError):
        with local_module.local_llm(local_config()):
            pytest.fail("Must not generate with an unready server")
    assert calls[-2:] == ["terminate", "wait"]


def test_mismatched_local_url_is_rejected(monkeypatch):
    config = local_config()
    config.api.base_url = "https://example.org/v1"
    with pytest.raises(ValueError, match="loopback"):
        with local_module.local_llm(config):
            pass
