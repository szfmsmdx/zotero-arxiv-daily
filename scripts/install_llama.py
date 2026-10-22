"""Install a pinned CPU-only llama.cpp build (no Python inference bindings)."""

import hashlib
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
from urllib.request import urlopen
import zipfile

VERSION = "b11804"
ASSETS = {
    "Linux": ("llama-b11804-bin-ubuntu-x64.tar.gz", "bb800fbd5e905fb8b9887c9a6cb0ab4f14c7267c5f99302874521e7558b0613f"),
    "Windows": ("llama-b11804-bin-win-cpu-x64.zip", "3a3e417a0816329829081bdd443e3045ff3b2dbe866fcef89a1d919e941ce23f"),
}


def install(destination: Path) -> Path:
    if platform.machine().lower() not in {"amd64", "x86_64"} or platform.system() not in ASSETS:
        raise RuntimeError("Automatic installation supports Linux/Windows x64; set LLAMA_SERVER for other systems.")
    name, expected = ASSETS[platform.system()]
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / name
    url = f"https://github.com/ggml-org/llama.cpp/releases/download/{VERSION}/{name}"
    with urlopen(url, timeout=120) as response, archive.open("wb") as output:
        shutil.copyfileobj(response, output)
    with archive.open("rb") as content:
        actual = hashlib.file_digest(content, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError("llama.cpp archive checksum mismatch.")
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(destination)
    else:
        with tarfile.open(archive) as bundle:
            bundle.extractall(destination, filter="data")
    binary_name = "llama-server.exe" if platform.system() == "Windows" else "llama-server"
    binary = next(destination.rglob(binary_name))
    if github_path := os.environ.get("GITHUB_PATH"):
        with open(github_path, "a", encoding="utf-8") as output:
            output.write(f"{binary.parent.resolve()}\n")
    print(f"Installed llama.cpp {VERSION}: {binary}")
    return binary


if __name__ == "__main__":
    install(Path(sys.argv[1]).resolve())
