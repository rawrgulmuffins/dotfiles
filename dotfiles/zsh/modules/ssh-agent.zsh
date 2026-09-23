# Load ssh keys into one agent shared by every shell. Uses keychain, which
# reuses a running agent instead of starting a new one per shell.
#
# Keys are listed one file name per line in ~/.ssh/load_keys, relative to
# ~/.ssh. That file is never committed, since key names reveal hosts.

if (( ! $+commands[keychain] )); then
    print -u2 "ssh-agent module: keychain is not installed"
    return 1
fi

if [[ ! -r ~/.ssh/load_keys ]]; then
    print -u2 "ssh-agent module: no ~/.ssh/load_keys file"
    return 1
fi

# ${(f)...} splits the file on newlines. The :# filter drops blank lines.
ssh_key_names=(${(f)"$(<~/.ssh/load_keys)"})
ssh_key_names=(${ssh_key_names:#})
eval "$(keychain --eval --quiet "${ssh_key_names[@]}")"
unset ssh_key_names
