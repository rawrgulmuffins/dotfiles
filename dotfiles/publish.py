import os
import shutil
from os.path import expanduser


files_to_publish = [
    ("bashrc", ".bashrc"),
    ("ipythonrc", ".ipythonrc"),
    ("vimrc", ".vimrc"),
    ("vimrc", ".nvimrc"),]

current_files = os.listdir(".")
current_dir = os.getcwd()
for source_name, dest_name in files_to_publish:
   source = os.path.join(current_dir, source_name)
   user_home = expanduser("~")
   dest = os.path.join(user_home, "{}".format(dest_name))
   shutil.copyfile(source, dest)
