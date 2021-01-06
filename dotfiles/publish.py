import os
import shutil
from pathlib import Path
from os.path import expanduser


files_to_publish = [
    ("bashrc", ".bashrc"),
    ("profile", ".profile"),
    ("zshrc", ".zshrc"),
    ("ipythonrc", ".ipythonrc"),
    ("vimrc", ".vimrc"),
    ("vimrc", ".nvimrc"),
    ("tmux.conf", ".tmux.conf"),
    ("pip.conf", ".pip/pip.conf"),
    ("gitconfig", ".gitconfig"),]

current_files = os.listdir(".")
current_dir = os.getcwd()
for source_name, dest_name in files_to_publish:
    source = os.path.join(current_dir, source_name)
    user_home = expanduser("~")
    dest = Path(user_home) / dest_name
    # If we're writing do a directory ensure it exists first
    try:
        os.makedirs(dest.parent, exist_ok=True)
    except FileExistsError:
        pass
    shutil.copyfile(source, dest)
