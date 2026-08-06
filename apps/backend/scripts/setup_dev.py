#!/usr/bin/env python3
"""Development setup script for CodeWhisper PR."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, cwd: Path = None) -> bool:
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr}")
        return False


def setup_development():
    print("Setting up development environment...")

    root_dir = Path(__file__).parent.parent
    env_file = root_dir / ".env"

    if not env_file.exists():
        print(".env file not found. Creating from .env.example...")
        example_file = root_dir / ".env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("Created .env file from .env.example")
            print("Please update .env with your API keys")
        else:
            print(".env.example not found!")
            return False

    print("Installing dependencies...")
    if not run_command("poetry install", root_dir):
        return False

    print("Running database migrations...")
    if not run_command("poetry run alembic upgrade head", root_dir):
        return False

    print("Seeding database with test data...")
    if not run_command("poetry run python scripts/seed_db.py", root_dir):
        return False

    print("Installing pre-commit hooks...")
    if not run_command("poetry run pre-commit install", root_dir):
        print("Pre-commit hooks installation failed")

    print("Development environment setup complete!")
    print("\nTo start the server:")
    print("  cd apps/backend")
    print("  poetry run uvicorn src.main:app --reload")

    return True


if __name__ == "__main__":
    success = setup_development()
    sys.exit(0 if success else 1)
