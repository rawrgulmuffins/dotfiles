# This file contains a number of apt-get installs of programs and services I find useful
# on any machine that I own or operate.

# TODO turn this into a installation package using something like ansible or salt stack
import shlex, subprocess
import os

# Check to make sure that our effective ID is root's ID.
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script."
         " Please try again, this time using 'sudo'.")

# Debian / ubuntu install command
install_command = "apt-get -yq install "

install_list = [
    # Terminals
    "terminology", # Current favorite unix terminal
    
    # Shells
    "bash", # Standard shell
    "zsh", # More fully features shell
    
    # Command Line Tools
    "tmux", # ssh connection manager
    "screen", # Tmux is built in screen
    "bash-completion",
    "curl", # Pull http and https websites
    "tree", # pretty display of the file system tree
    "nmap", # network mapper. Careful about scanning shit.
    "ranger", # Pretty console file system display
    "attr", # Manipulation of file attributes
    "pandoc", # Translation most text or markdown formats to any other format
    "colortest", # Tests color capabilities of current terminal
    "gparted", # Disk partition tool
    
    
    # Daemons
    "sshd", # Allows ssh sessions to your box
    "ntmp", # Network time protocal
    "etckeeper", # Configuration File Version Tracking
    
    # System Monitoring
    "htop", # Pretty system performance monitoring
    "dstat", # More in depth disk performance
    "strace", # More in depth kernal usage
    "nethogs", # More in depth network usage
    "iperf", 
    "iftop", 
    "agedu", # Tracks down wasted disk space
    
    # Network Debugging
    "ngrep", # Network grep
    "tcpdump", # TCP traffic dumped to console or file
    "wireshark", # Reads tcp dumps
    "mitmproxy", # Used to monitor traffic sent out
    "netcat", # Client server file transfer
    
    # Editors
    "vim", # Flame war generator
    
    # Python
    "python3.5",
    "python3.5-dev",
    "Python3-pip",
    
    # Source Control
    "git",
    "tig", # text-mode interface for git
    
]


update_command = shlex.split("apt-get -yq update")
dist_upgrade = shlex.split("apt-get -yq dist-upgrade")

subprocess.run(update_command)
subprocess.run(dist_upgrade)
for package in install_list:
    command = shlex.split("{install_command} {package}".format(
        install_command=install_command,
        package=package,))
    subprocess.run(command)
