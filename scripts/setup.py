import shutil
import subprocess
import sys
from pathlib import Path

DOWNLOAD_LINKS = (
    ("uv", "https://docs.astral.sh/uv/getting-started/installation/"),
    ("go", "https://go.dev/dl/"),
    ("duckdb", "https://duckdb.org/install/"),
)


def print_download_links(tools: tuple[tuple[str, str], ...] = DOWNLOAD_LINKS) -> None:
    print("Download links:")
    for name, url in tools:
        print(f"  {name}: {url}")


def require_uv() -> None:
    if shutil.which("uv"):
        return
    print("uv is required but was not found on PATH.")
    print_download_links()
    sys.exit(1)


def warn_optional_tools() -> None:
    missing = [
        (name, url)
        for name, url in DOWNLOAD_LINKS
        if name != "uv" and shutil.which(name) is None
    ]
    if not missing:
        return
    print("Optional tools not found on PATH:")
    for name, url in missing:
        print(f"  {name}: {url}")


def setup() -> None:
    require_uv()
    warn_optional_tools()

    if not Path(".env").exists():
        shutil.copy(".env.example", ".env")

    subprocess.run(["uv", "run", "python", "-m", "ingestion.ducklake"], check=True)
    subprocess.run(
        ["uv", "run", "python", "-m", "scripts.ingestion_runner"], check=True
    )


if __name__ == "__main__":
    setup()
