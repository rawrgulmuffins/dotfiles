zsh
===

`../zshrc` is the shared config. This directory holds the pieces that only
apply to some machines.

| Path | Purpose |
| --- | --- |
| `modules/macos.zsh` | Homebrew paths. Loads automatically on macOS. |
| `modules/wsl.zsh` | Puts `wsl-bin` on `PATH` and sets `BROWSER`. Loads automatically under WSL. |
| `modules/ssh-agent.zsh` | Opt-in. Loads the keys listed in `~/.ssh/load_keys` into one agent through `keychain`. |
| `modules/infracost.zsh` | Opt-in. Exports `INFRACOST_API_KEY` from `~/.infracost_api_key`. |
| `wsl-bin/` | `wslview` and `pbcopy` shims that call into Windows. |
| `zshrc.local.example` | Starting point for `~/.zshrc.local`. |

Install
-------

`publish.py` links `zshrc` to `~/.zshrc` and this directory to
`~/.config/zsh`, where the zshrc looks for modules. It also links `zshenv` to
`~/.zshenv`, which stops Ubuntu's global zshrc from running compinit a second
time. Without that link, every
new shell on macOS or WSL prints a "module not found" error.

Local config
------------

`~/.zshrc.local` is sourced last and is never committed. It opts into modules
with `load_zsh_module <name>` and holds anything specific to one machine or
one employer.
