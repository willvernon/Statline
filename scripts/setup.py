import os
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


def ensure_dagster_home() -> Path:
    """Create the local Dagster instance dir. `dagster dev` ignores .env."""
    home = Path(".dagster_home").resolve()
    home.mkdir(exist_ok=True)
    return home


def setup() -> None:
    require_uv()
    warn_optional_tools()
    root = Path(".").resolve()
    env = {
        **os.environ,
        "LAKE_CATALOG_PATH": str(root / "lake/metadata.ducklake"),
        "LAKE_DATA_PATH": str(root / "lake/data"),
    }

    if not Path(".env").exists():
        shutil.copy(".env.example", ".env")

    dagster_home = ensure_dagster_home()

    subprocess.run(["uv", "run", "python", "-m", "ingestion.ducklake"], check=True)
    subprocess.run(
        ["uv", "run", "python", "-m", "scripts.ingestion_runner"], check=True
    )
    subprocess.run(
        [
            "uv",
            "run",
            "dbt",
            "build",
            "--project-dir",
            "statline_dbt",
            "--profiles-dir",
            "statline_dbt",
        ],
        check=True,
        env=env,
    )

    print(
        "Dagster instance dir is ready. Set an absolute DAGSTER_HOME before "
        "`dagster dev` (it does not read .env):"
    )
    print(f'  bash/zsh: export DAGSTER_HOME="{dagster_home}"')
    print(f"  fish:     set -x DAGSTER_HOME {dagster_home}")
    print(f'  nushell:  $env.DAGSTER_HOME = "{dagster_home}"')
    print("  uv run dagster dev -m orchestration.definitions")


if __name__ == "__main__":
    setup()
