"""Symlink the configs in this directory into the home directory.

Anything already at a destination that isn't the expected link is moved aside
to a .bak file first, so nothing is overwritten. Safe to run repeatedly.
"""

import time
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent

# Source path in this directory, destination relative to the home directory.
LINKS: list[tuple[str, str]] = [
    ("zshrc", ".zshrc"),
    ("zsh", ".config/zsh"),
    ("nvim", ".config/nvim"),
    ("tmux.conf", ".tmux.conf"),
    ("gitconfig", ".gitconfig"),
    ("git_ignore", ".config/git/ignore"),
]


def backup_path_for(destination: Path) -> Path:
    backup = destination.with_name(destination.name + ".bak")
    if backup.exists() or backup.is_symlink():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(f"{destination.name}.bak-{timestamp}")
    return backup


def link(source: Path, destination: Path) -> None:
    if destination.is_symlink() and destination.resolve() == source:
        print(f"ok       {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        backup = backup_path_for(destination)
        destination.rename(backup)
        print(f"moved    {destination} -> {backup}")

    destination.symlink_to(source)
    print(f"linked   {destination} -> {source}")


def main() -> None:
    home = Path.home()
    for source_name, destination_name in LINKS:
        link(SOURCE_DIR / source_name, home / destination_name)


if __name__ == "__main__":
    main()
