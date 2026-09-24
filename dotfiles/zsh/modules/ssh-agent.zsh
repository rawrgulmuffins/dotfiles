# keychain reuses a running agent, so every shell shares one instead of each
# starting its own. Key names live in ~/.ssh/load_keys, outside the repo, since
# they reveal hosts.

if (( ! $+commands[keychain] )); then
    print -u2 "ssh-agent module: keychain is not installed"
    return 1
fi

if [[ ! -r ~/.ssh/load_keys ]]; then
    print -u2 "ssh-agent module: no ~/.ssh/load_keys file"
    return 1
fi

ssh_key_names=(${(f)"$(<~/.ssh/load_keys)"})
eval "$(keychain --eval --quiet "${ssh_key_names[@]}")"
unset ssh_key_names
