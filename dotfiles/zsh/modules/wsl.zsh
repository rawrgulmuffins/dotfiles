# Windows Subsystem for Linux. Loaded automatically under WSL.

# Shims for wslview and pbcopy, which call into Windows. Ubuntu 26.04 doesn't
# package wslu, and peek.nvim runs wslview to open its preview. The tmux
# config copies with pbcopy.
export PATH="$ZSH_CONFIG_DIR/wsl-bin:$PATH"

# Tools that open URLs (gh, Python's webbrowser, xdg-open) read $BROWSER.
export BROWSER=wslview
