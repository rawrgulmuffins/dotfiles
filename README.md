dotfiles
========

All of the configuration files configured to my personal taste

How it's organized
------------------

The config comes in three layers:

- Shared files in this repo apply on every machine.
- Modules add pieces that only apply on some machines. The macOS and WSL
  modules load on their own. Others, like `ssh-agent`, load only when a
  machine asks for them.
- Local files stay on one machine and are never committed. They hold the
  git identity, employer-specific settings, and the list of modules to load.

The local files load last, so they can override anything else.

| In this repo | Installed at | Purpose |
| --- | --- | --- |
| `dotfiles/zshenv` | `~/.zshenv` | Read by every zsh, before `~/.zshrc` |
| `dotfiles/zshrc` | `~/.zshrc` | History, completion, prompt, aliases, and functions for interactive shells |
| `dotfiles/zsh/` | `~/.config/zsh` | zsh modules and the WSL helper scripts |
| `dotfiles/nvim/` | `~/.config/nvim` | Neovim config and its plugin lockfile |
| `dotfiles/tmux.conf` | `~/.tmux.conf` | tmux |
| `dotfiles/gitconfig` | `~/.gitconfig` | git aliases and push/pull behavior |
| `dotfiles/git_ignore` | `~/.config/git/ignore` | Files git ignores in every repo |
| `dotfiles/zsh/zshrc.local.example` | copied to `~/.zshrc.local` | Starting point for local zsh settings |
| `dotfiles/gitconfig.local.example` | copied to `~/.gitconfig.local` | Starting point for local git settings |
| `dotfiles/python_gitignore` | not installed | `.gitignore` template for new Python projects |

`publish.py` creates the links. The `.local` files are copies, since they're
edited per machine. When `$XDG_CONFIG_HOME` is set, the `~/.config` links go
there instead.

### Load order

zsh reads its files in this order:

1. `~/.zshenv`
2. `~/.zshrc`, which loads the macOS or WSL module near the top
3. `~/.zshrc.local`, sourced at the end of `~/.zshrc`, which loads any opt-in
   modules with `load_zsh_module <name>`

git reads `~/.gitconfig` and then `~/.gitconfig.local`, which is included at
the end.

Neovim starts at `init.lua`, which loads the files in `lua/config/` in this
order:

1. `options.lua` sets editor options, plus plugin settings that have to exist
   before the plugins load.
2. `plugins.lua` installs the plugins and sets up formatting and linting.
3. `lsp.lua` turns on the language servers that are installed.
4. `keymaps.lua` holds the key mappings.
5. `autocmds.lua` covers filetype detection, per-language indentation, and
   colors.

### Where a change goes

- A setting for every machine goes in the shared file.
- A setting for one operating system goes in that OS's module.
- Something optional goes in a new module, which each machine then turns on
  from `~/.zshrc.local`.
- Anything personal, secret, or employer-specific goes in a `.local` file.

Install
-------

```bash
python3 dotfiles/publish.py
cp dotfiles/zsh/zshrc.local.example ~/.zshrc.local
cp dotfiles/gitconfig.local.example ~/.gitconfig.local
```

`publish.py` symlinks each config into the home directory. Anything already
at a destination is moved to a `.bak` file first. Edit the two `.local` files
for the machine. They hold identity, git hosting auth, work-specific settings,
and opt-in modules, and are never committed.

WSL setup
---------

Setting up a new Windows machine with WSL2 and Ubuntu 26.04, start to finish.

On the Windows side:

1. In PowerShell, run `wsl --install -d Ubuntu-26.04` and create the Linux
   user when prompted.
2. Install a [Nerd Font](https://www.nerdfonts.com/) on Windows. In Windows
   Terminal, select it for the Ubuntu profile under Appearance, then Font face.
   Without it, the icons `lsd` prints render as boxes.

Inside Ubuntu:

3. Install packages. `keychain` is only needed for the zsh `ssh-agent` module.

   ```bash
   sudo apt update
   sudo apt install zsh tmux git fzf ripgrep bat lsd shfmt sqlfluff keychain pipx npm
   pipx install ruff pyright
   sudo npm install -g bash-language-server
   ```

4. Install Neovim from the GitHub release, since apt's version is too old. Use
   the `arm64` tarball instead on an ARM laptop. Check the file's SHA-256
   against the digest on the release page before extracting it.

   ```bash
   curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
   sha256sum nvim-linux-x86_64.tar.gz
   sudo tar -C /opt -xzf nvim-linux-x86_64.tar.gz
   sudo ln -s /opt/nvim-linux-x86_64/bin/nvim /usr/local/bin/nvim
   ```

5. Optional installs:
   - Terraform and `terraform-ls` from
     [HashiCorp's apt repo](https://developer.hashicorp.com/terraform/install),
     which supports 26.04.
   - [Deno](https://deno.com/), for Markdown preview in Neovim.
   - `win32yank.exe`, for clipboard copies that keep non-ASCII text intact.
     It needs to be on `PATH`, for example in `~/.local/bin`.

6. Clone this repo under the Linux home directory, not under `/mnt/c`. Git is
   much slower across the Windows filesystem. Then run the Install steps
   above from inside the clone.

   ```bash
   mkdir -p ~/git && cd ~/git
   git clone https://github.com/rawrgulmuffins/dotfiles.git
   cd dotfiles
   ```

7. Set the work email in `~/.gitconfig.local`. Until then, git either
   refuses to commit or guesses an address from the hostname.
8. Make zsh the login shell with `chsh -s "$(which zsh)"`, then open a new
   terminal.
9. Start `nvim` once so the plugins install, then run `:checkhealth` to see
   which language servers and formatters are still missing.

Once it's running, check that Ctrl+V reaches Neovim. Press it in normal mode
and look for `-- VISUAL BLOCK --` at the bottom of the screen. If the
clipboard gets pasted instead, Windows Terminal has Ctrl+V bound to paste and
is taking the key before Neovim sees it. Visual block mode and inserting a
literal character both use Ctrl+V. Removing the binding under Actions in the
Windows Terminal settings fixes it, and Ctrl+Shift+V still pastes.

Neovim
------

The config in `dotfiles/nvim` needs Neovim 0.12 or newer for its built-in
plugin manager. Ubuntu 26.04's apt package is 0.11, so install from the
[GitHub releases](https://github.com/neovim/neovim/releases) instead.

Plugins install on first launch at the revisions pinned in
`nvim-pack-lock.json`. The exception is `peek.nvim`, which only installs when
`deno` is present and isn't pinned yet. Its first install adds it to the
lockfile, and that change should be committed. To update them, run `:lua vim.pack.update()`, review the
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
