dotfiles
========

All of the configuration files configured to my personal taste

Install
-------

```bash
python3 dotfiles/publish.py
cp dotfiles/zsh/zshrc.local.example ~/.zshrc.local
cp dotfiles/gitconfig.local.example ~/.gitconfig.local
gh auth login
```

`publish.py` symlinks each config into the home directory. Anything already
at a destination is moved to a `.bak` file first. Edit the two `.local` files
for the machine. They hold identity, work-specific settings, and opt-in
modules, and are never committed. `gh auth login` sets up the GitHub HTTPS
credentials the gitconfig uses.

Neovim
------

The config in `dotfiles/nvim` needs Neovim 0.12 or newer for its built-in
plugin manager. Ubuntu 26.04's apt package is 0.11, so install from the
[GitHub releases](https://github.com/neovim/neovim/releases) instead.

Plugins install on first launch at the revisions pinned in
`nvim-pack-lock.json`. To update them, run `:lua vim.pack.update()`, review the
changes, confirm with `:write`, and commit the lockfile. The config is
symlinked, so the update writes the lockfile straight into this repo.

Language servers and formatters are separate installs. Each one is used only
when its executable is on `PATH`.

| Tool | Used for |
| --- | --- |
| `fzf`, `rg` | File and text search |
| `pyright` | Python type checking |
| `ruff` | Python linting, formatting, and import sorting |
| `shfmt`, `bash-language-server` | Shell formatting and diagnostics |
| `sqlfluff` | SQL formatting and linting, Postgres dialect |
| `terraform`, `terraform-ls` | Terraform formatting and diagnostics |
| `deno` | Markdown preview (`peek.nvim`), which is skipped without it |

On WSL, `peek.nvim` opens the preview by running `wslview`. Ubuntu 26.04
doesn't package `wslu`, which provides it. The zsh `wsl` module puts a
replacement on `PATH`.

zsh
---

See `dotfiles/zsh/README.md` for the module layout.
