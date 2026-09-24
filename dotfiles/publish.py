"""Symlink the configs in this directory into the home directory.

Anything already at a destination that isn't the expected link is moved aside
to a .bak file first, so nothing is overwritten. Safe to run repeatedly.
"""

import os
import time
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent

HOME_LINKS: list[tuple[str, str]] = [
    ("zshenv", ".zshenv"),
    ("zshrc", ".zshrc"),
    ("tmux.conf", ".tmux.conf"),
    ("gitconfig", ".gitconfig"),
]

# zsh, Neovim, and git all look in $XDG_CONFIG_HOME when it's set.
CONFIG_LINKS: list[tuple[str, str]] = [
    ("zsh", "zsh"),
    ("nvim", "nvim"),
    ("git_ignore", "git/ignore"),
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


def planned_links() -> list[tuple[Path, Path]]:
    home = Path.home()
    config_home = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
    return [
        (SOURCE_DIR / source_name, home / destination_name)
        for source_name, destination_name in HOME_LINKS
    ] + [
        (SOURCE_DIR / source_name, config_home / destination_name)
        for source_name, destination_name in CONFIG_LINKS
    ]


def main() -> None:
    for source, destination in planned_links():
        link(source, destination)


if __name__ == "__main__":
    main()
