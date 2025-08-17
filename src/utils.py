from __future__ import annotations

"""Shared utilities for the multi-agent workflow."""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR: Path = Path(__file__).resolve().parent  # repository root

def repo_path(rel: str | Path) -> Path:
    """Return an absolute Path inside the repository given a relative string."""
    return (ROOT_DIR / rel).resolve()

print(f"Repository root: {ROOT_DIR}")

PROMPTS_DIR: Path = repo_path("prompts")

def load_prompt(name: str, **subs) -> str:
    """Load a Markdown prompt template and substitute <PLACEHOLDERS>."""
    content = (PROMPTS_DIR / name).read_text()
    for key, val in subs.items():
        content = content.replace(f"<{key}>", str(val))
    return content

print(f"Prompts directory: {PROMPTS_DIR}")