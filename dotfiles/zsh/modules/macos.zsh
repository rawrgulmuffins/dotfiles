if [[ ! -x /opt/homebrew/bin/brew ]]; then
    print -u2 "macos module: Homebrew not found at /opt/homebrew"
    return 1
fi

eval "$(/opt/homebrew/bin/brew shellenv)"

# GNU make ahead of the older BSD make that ships with macOS.
export PATH="$HOMEBREW_PREFIX/opt/make/libexec/gnubin:$PATH"

# Homebrew doesn't link libpq, so its psql isn't on PATH otherwise.
export PATH="$HOMEBREW_PREFIX/opt/libpq/bin:$PATH"

# openssl@3 for packages that compile against it, like psycopg2.
export PATH="$HOMEBREW_PREFIX/opt/openssl@3/bin:$PATH"
export LIBRARY_PATH="${LIBRARY_PATH:+$LIBRARY_PATH:}$HOMEBREW_PREFIX/opt/openssl@3/lib"
