from pathlib import Path
import shutil
import subprocess

src = Path(".env.example")
dst = Path(".env")


def setup() -> None:
    if not Path(".env").exists():
        shutil.copy(".env.example", ".env")

    # run ingestion/ducklake.py
    subprocess.run(["uv", "run", "python", "-m", "ingestion.ducklake"], check=True)
    # run scripts/ingestion-runner.py
    subprocess.run(
        ["uv", "run", "python", "-m", "scripts.ingestion_runner"], check=True
    )


if __name__ == "__main__":
    setup()
