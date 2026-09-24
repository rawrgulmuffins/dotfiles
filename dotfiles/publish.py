"""Symlink the configs in this directory into the home directory.

Anything already at a destination that isn't the expected link is moved aside
to a .bak file first, so nothing is overwritten. Missing .local files are
created from the examples, and existing ones are left alone. Safe to run
repeatedly.
"""

import os
import shutil
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


# Created only when missing, since they hold per-machine edits.
LOCAL_FILES: list[tuple[str, str]] = [
    ("zsh/zshrc.local.example", ".zshrc.local"),
    ("gitconfig.local.example", ".gitconfig.local"),
]


def backup_path_for(destination: Path) -> Path:
    backup = destination.with_name(destination.name + ".bak")
    if backup.exists() or backup.is_symlink():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(f"{destination.name}.bak-{timestamp}")
    return backup


def is_linked(source: Path, destination: Path) -> bool:
    return destination.is_symlink() and destination.resolve() == source


def link(source: Path, destination: Path) -> None:
    if is_linked(source, destination):
        print(f"ok       {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        backup = backup_path_for(destination)
        destination.rename(backup)
        print(f"moved    {destination} -> {backup}")

    destination.symlink_to(source)
    print(f"linked   {destination} -> {source}")


def create_if_missing(example: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        print(f"kept     {destination}")
        return
    shutil.copyfile(example, destination)
    print(f"created  {destination}, edit it for this machine")


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
    for example_name, destination_name in LOCAL_FILES:
        create_if_missing(SOURCE_DIR / example_name, Path.home() / destination_name)


if __name__ == "__main__":
    main()
