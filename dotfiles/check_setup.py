"""Check that the installed dotfiles behave as intended on this machine.

Run after publish.py and after upgrading Neovim, plugins, or tools. Exits
non-zero if any check fails. Built for the Linux and WSL target.
"""

import json
import os
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from publish import planned_links

SOURCE_DIR = Path(__file__).resolve().parent
LOCKFILE = SOURCE_DIR / "nvim" / "nvim-pack-lock.json"

# A comment longer than the line limit is a violation sqlfluff can't fix.
UNFIXABLE_SQL = "-- " + "x" * 120 + "\nSELECT a,b from t\n"

OPTIONAL_TOOLS: list[tuple[str, str]] = [
    ("pyright-langserver", "Python type checking"),
    ("ruff", "Python linting and formatting"),
    ("bash-language-server", "shell diagnostics"),
    ("shfmt", "shell formatting"),
    ("sqlfluff", "SQL formatting and linting"),
    ("terraform", "Terraform formatting"),
    ("terraform-ls", "Terraform diagnostics"),
    ("rg", "project grep in Neovim"),
    ("deno", "Markdown preview"),
]


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"
    INFO = "INFO"


@dataclass
class Result:
    name: str
    status: Status
    detail: str = ""


def run(
    command: list[str],
    stdin: str | None = None,
    timeout: float = 60,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=cwd,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return subprocess.CompletedProcess(command, 127, "", str(error))


def is_wsl() -> bool:
    proc_version = Path("/proc/version")
    return proc_version.exists() and "microsoft" in proc_version.read_text().lower()


def nvim_lua(lua: str, cwd: Path | None = None) -> str:
    completed = run(
        ["nvim", "--headless", "-c", f"lua io.stdout:write({lua})", "-c", "qa!"],
        cwd=cwd,
    )
    return completed.stdout


def nvim_messages_after(commands: list[str], cwd: Path) -> str:
    arguments = ["nvim", "--headless"]
    for command in commands:
        arguments += ["-c", command]
    arguments += ["-c", 'lua io.stdout:write(vim.fn.execute("messages"))', "-c", "qa!"]
    return run(arguments, cwd=cwd).stdout


def check_links() -> list[Result]:
    results: list[Result] = []
    for source, destination in planned_links():
        if destination.is_symlink() and destination.resolve() == source:
            results.append(Result(f"link {destination.name}", Status.PASS))
        else:
            results.append(
                Result(
                    f"link {destination.name}",
                    Status.FAIL,
                    f"{destination} is not linked to {source}; run publish.py",
                )
            )
    return results


def check_nvim_version() -> Result:
    if shutil.which("nvim") is None:
        return Result("nvim version", Status.FAIL, "nvim is not installed")
    first_line = run(["nvim", "--version"]).stdout.splitlines()[0]
    match = re.search(r"v(\d+)\.(\d+)\.(\d+)", first_line)
    if match is None:
        return Result("nvim version", Status.FAIL, f"can't parse: {first_line}")
    major, minor = int(match.group(1)), int(match.group(2))
    if (major, minor) < (0, 12):
        return Result(
            "nvim version", Status.FAIL, f"{first_line}, needs 0.12 for vim.pack"
        )
    if (major, minor) > (0, 12):
        return Result(
            "nvim version",
            Status.WARN,
            f"{first_line}, lockfile was built against 0.12",
        )
    return Result("nvim version", Status.PASS, first_line)


def check_nvim_starts_clean() -> Result:
    # The first start may install plugins, which prints progress.
    run(["nvim", "--headless", "-c", "qa!"], timeout=300)
    messages = nvim_lua('vim.fn.execute("messages")').strip()
    if messages:
        return Result("nvim starts clean", Status.FAIL, messages[:300])
    return Result("nvim starts clean", Status.PASS)


def check_plugins_match_lockfile() -> Result:
    pinned = json.loads(LOCKFILE.read_text())["plugins"]
    plugin_dir = (
        Path(nvim_lua('vim.fn.stdpath("data")')) / "site" / "pack" / "core" / "opt"
    )
    mismatches: list[str] = []
    for name, entry in pinned.items():
        checkout = plugin_dir / name
        if not checkout.is_dir():
            mismatches.append(f"{name} not installed")
            continue
        installed = run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"]
        ).stdout.strip()
        if installed != entry["rev"]:
            mismatches.append(f"{name} at {installed[:10]}, pinned {entry['rev'][:10]}")
    if mismatches:
        return Result("plugins match lockfile", Status.FAIL, "; ".join(mismatches))
    return Result("plugins match lockfile", Status.PASS, f"{len(pinned)} plugins")


def check_filetypes() -> Result:
    expected = {"new.tf": "terraform", "deploy.sh.j2": "sh", "page.j2": "htmldjango"}
    wrong: list[str] = []
    for filename, filetype in expected.items():
        detected = nvim_lua(
            f'tostring(vim.filetype.match({{ filename = "{filename}" }}))'
        )
        if detected != filetype:
            wrong.append(f"{filename} is {detected}, expected {filetype}")
    if wrong:
        return Result("filetype detection", Status.FAIL, "; ".join(wrong))
    return Result("filetype detection", Status.PASS)


def format_on_save(
    name: str, executable: str, filename: str, before: str, expected_after: str | None
) -> Result:
    if shutil.which(executable) is None:
        return Result(name, Status.SKIP, f"{executable} not installed")
    with tempfile.TemporaryDirectory() as scratch:
        scratch_dir = Path(scratch)
        target = scratch_dir / filename
        target.write_text(before)
        messages = nvim_messages_after([f"edit {filename}", "write"], cwd=scratch_dir)
        after = target.read_text()
    if re.search(r"error|failed", messages, re.IGNORECASE):
        return Result(name, Status.FAIL, messages.strip()[:300])
    if expected_after is not None and after != expected_after:
        return Result(name, Status.FAIL, f"got {after!r}")
    if expected_after is None and after == before:
        return Result(name, Status.FAIL, "file was not changed on save")
    return Result(name, Status.PASS)


def check_format_on_save() -> list[Result]:
    return [
        format_on_save(
            "format python on save",
            "ruff",
            "sample.py",
            'import sys\nimport os\nx = {  "a":1 }\nprint(os.getcwd(),sys.argv, x)\n\n\n',
            'import os\nimport sys\n\nx = {"a": 1}\nprint(os.getcwd(), sys.argv, x)\n',
        ),
        format_on_save(
            "format sql on save",
            "sqlfluff",
            "query.sql",
            "select a,b from t where a=1\n",
            None,
        ),
        format_on_save(
            "format sql with unfixable violation",
            "sqlfluff",
            "unfixable.sql",
            UNFIXABLE_SQL,
            None,
        ),
        format_on_save(
            "format shell on save",
            "shfmt",
            "script.sh",
            "if true; then\necho hi\nfi\n",
            "if true; then\n    echo hi\nfi\n",
        ),
    ]


def check_sqlfluff_exit_code() -> Result:
    if shutil.which("sqlfluff") is None:
        return Result("sqlfluff exit code", Status.SKIP, "sqlfluff not installed")
    completed = run(["sqlfluff", "fix", "--dialect=postgres", "-"], stdin=UNFIXABLE_SQL)
    if completed.returncode == 1 and "select" in completed.stdout.lower():
        return Result(
            "sqlfluff exit code", Status.PASS, "exits 1 and still prints the fix"
        )
    return Result(
        "sqlfluff exit code",
        Status.FAIL,
        f"exit {completed.returncode}; the nvim config's exit_codes = {{ 0, 1 }} assumes 1 with output",
    )


def check_sql_lint() -> Result:
    if shutil.which("sqlfluff") is None:
        return Result("sql lint", Status.SKIP, "sqlfluff not installed")
    with tempfile.TemporaryDirectory() as scratch:
        scratch_dir = Path(scratch)
        (scratch_dir / "bad.sql").write_text("SELECT a,b from t WHERE a=1\n")
        count = nvim_lua(
            "(function() vim.cmd('edit bad.sql'); "
            "vim.wait(15000, function() return #vim.diagnostic.get(0) > 0 end); "
            "return tostring(#vim.diagnostic.get(0)) end)()",
            cwd=scratch_dir,
        )
    if count.isdigit() and int(count) > 0:
        return Result("sql lint", Status.PASS, f"{count} diagnostics on a bad file")
    return Result(
        "sql lint", Status.FAIL, f"no diagnostics on a bad file (got {count!r})"
    )


def check_lsp_attaches() -> list[Result]:
    samples = {
        "pyright": ("pyright-langserver", "sample.py", "import os\n"),
        "ruff": ("ruff", "sample.py", "import os\n"),
        "bashls": ("bash-language-server", "sample.sh", "echo hi\n"),
        "terraformls": ("terraform-ls", "main.tf", 'variable "name" {}\n'),
    }
    results: list[Result] = []
    for server, (executable, filename, content) in samples.items():
        name = f"lsp {server} attaches"
        if shutil.which(executable) is None:
            results.append(Result(name, Status.SKIP, f"{executable} not installed"))
            continue
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            run(["git", "init", "-q"], cwd=scratch_dir)
            (scratch_dir / filename).write_text(content)
            attached = nvim_lua(
                f"(function() vim.cmd('edit {filename}'); "
                f"vim.wait(20000, function() return #vim.lsp.get_clients({{ bufnr = 0, name = '{server}' }}) > 0 end); "
                f"return tostring(#vim.lsp.get_clients({{ bufnr = 0, name = '{server}' }})) end)()",
                cwd=scratch_dir,
            )
        results.append(
            Result(
                name,
                Status.PASS if attached == "1" else Status.FAIL,
                "" if attached == "1" else "did not attach within 20s",
            )
        )
    return results


def check_optional_tools() -> list[Result]:
    return [
        Result(
            f"tool {executable}",
            Status.PASS if shutil.which(executable) else Status.WARN,
            "" if shutil.which(executable) else f"missing, no {purpose}",
        )
        for executable, purpose in OPTIONAL_TOOLS
    ]


def check_fzf_version() -> Result:
    if shutil.which("fzf") is None:
        return Result("fzf version", Status.FAIL, "fzf is not installed")
    version_text = run(["fzf", "--version"]).stdout.split()[0]
    parts = [int(part) for part in re.findall(r"\d+", version_text)[:2]]
    if parts < [0, 48]:
        return Result(
            "fzf version", Status.FAIL, f"{version_text}, `fzf --zsh` needs 0.48+"
        )
    return Result("fzf version", Status.PASS, version_text)


ZSH_PROBE = """
print -r -- '@@BEGIN'
print -r -- "HISTFILE=$HISTFILE"
print -r -- "SAVEHIST=$SAVEHIST"
print -r -- "KEYMAP=$(bindkey -lL main)"
print -r -- "CTRL_R=$(bindkey -M viins '^R')"
print -r -- "SKIP_GLOBAL_COMPINIT=${skip_global_compinit:-}"
print -r -- "CAT=$(alias cat)"
print -r -- "BROWSER=${BROWSER:-}"
print -r -- "WSLVIEW=$(whence -p wslview)"
print -r -- "PBCOPY=$(whence -p pbcopy)"
print -r -- '@@END'
"""


def interactive_zsh(script_body: str) -> str:
    # zle and key bindings only exist when zsh has a terminal, so run it under
    # script(1) for a pseudo-terminal.
    command = f"zsh -i -c {shlex.quote(script_body)}"
    return run(["script", "-qec", command, "/dev/null"]).stdout.replace("\r", "")


def check_zsh() -> list[Result]:
    if shutil.which("zsh") is None:
        return [Result("zsh", Status.FAIL, "zsh is not installed")]
    if shutil.which("script") is None:
        return [Result("zsh", Status.SKIP, "script(1) is not installed")]
    output = interactive_zsh(ZSH_PROBE)
    if "@@BEGIN" not in output or "@@END" not in output:
        return [Result("zsh starts", Status.FAIL, output.strip()[:300])]
    startup_output, _, rest = output.partition("@@BEGIN")
    values = dict(
        line.split("=", 1)
        for line in rest.partition("@@END")[0].strip().splitlines()
        if "=" in line
    )

    results = [
        Result(
            "zsh starts quietly",
            Status.WARN if startup_output.strip() else Status.PASS,
            startup_output.strip()[:300],
        ),
        Result(
            "zsh saves history",
            Status.PASS
            if values.get("HISTFILE") and values.get("SAVEHIST", "0") not in ("", "0")
            else Status.FAIL,
            f"HISTFILE={values.get('HISTFILE')} SAVEHIST={values.get('SAVEHIST')}",
        ),
        Result(
            "zsh vi keymap",
            Status.PASS if "viins" in values.get("KEYMAP", "") else Status.FAIL,
            values.get("KEYMAP", ""),
        ),
        Result(
            "zsh fzf Ctrl-R",
            Status.PASS if "fzf" in values.get("CTRL_R", "") else Status.FAIL,
            values.get("CTRL_R", ""),
        ),
        Result(
            "zsh skips global compinit",
            Status.PASS if values.get("SKIP_GLOBAL_COMPINIT") == "1" else Status.FAIL,
            ""
            if values.get("SKIP_GLOBAL_COMPINIT") == "1"
            else "~/.zshenv not linked?",
        ),
        Result(
            "zsh cat alias",
            Status.PASS if "bat" in values.get("CAT", "") else Status.WARN,
            values.get("CAT") or "no alias, bat not installed",
        ),
    ]

    if is_wsl():
        shim_dir = SOURCE_DIR / "zsh" / "wsl-bin"
        shims_first = all(
            values.get(key) and Path(values[key]).resolve().parent == shim_dir
            for key in ("WSLVIEW", "PBCOPY")
        )
        results.append(
            Result(
                "zsh wsl shims on PATH",
                Status.PASS if shims_first else Status.FAIL,
                f"wslview={values.get('WSLVIEW')} pbcopy={values.get('PBCOPY')}",
            )
        )
        results.append(
            Result(
                "zsh BROWSER",
                Status.PASS if values.get("BROWSER") == "wslview" else Status.FAIL,
                values.get("BROWSER", ""),
            )
        )

    timings: list[float] = []
    for _ in range(5):
        started = time.perf_counter()
        interactive_zsh("exit")
        timings.append(time.perf_counter() - started)
    results.append(
        Result(
            "zsh startup time",
            Status.INFO,
            f"median {statistics.median(timings) * 1000:.0f} ms over 5 runs",
        )
    )
    return results


def check_tmux() -> list[Result]:
    if shutil.which("tmux") is None:
        return [Result("tmux", Status.FAIL, "tmux is not installed")]
    socket = ["tmux", "-L", "check_setup"]
    # NOTE: new-session -f exits 0 even when the config has errors. source-file
    # reports them and exits 1.
    run(socket + ["-f", "/dev/null", "new-session", "-d"])
    try:
        started = run(socket + ["source-file", str(Path.home() / ".tmux.conf")])
        if started.returncode != 0 or started.stderr.strip():
            return [
                Result("tmux loads config", Status.FAIL, started.stderr.strip()[:300])
            ]
        terminal = run(
            socket + ["show-options", "-gv", "default-terminal"]
        ).stdout.strip()
        features = run(socket + ["show-options", "-g", "terminal-features"]).stdout
        return [
            Result("tmux loads config", Status.PASS),
            Result(
                "tmux default-terminal",
                Status.PASS if terminal == "tmux-256color" else Status.WARN,
                terminal
                if terminal == "tmux-256color"
                else f"{terminal}, tmux-256color terminfo missing",
            ),
            Result(
                "tmux true color",
                Status.PASS if "xterm-256color:RGB" in features else Status.FAIL,
            ),
        ]
    finally:
        run(socket + ["kill-server"])


def check_git() -> list[Result]:
    results: list[Result] = []
    local_config = Path.home() / ".gitconfig.local"
    email = run(["git", "config", "--get", "user.email"]).stdout.strip()
    if not local_config.exists():
        results.append(
            Result(
                "git local config",
                Status.FAIL,
                "~/.gitconfig.local missing; copy gitconfig.local.example",
            )
        )
    elif not email or email == "you@example.com":
        results.append(
            Result(
                "git local config",
                Status.FAIL,
                "user.email not set in ~/.gitconfig.local",
            )
        )
    else:
        results.append(Result("git local config", Status.PASS, email))

    anonymous = run(
        ["git", "ls-remote", "https://github.com/neovim/nvim-lspconfig", "HEAD"],
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    results.append(
        Result(
            "git anonymous https clone",
            Status.PASS if anonymous.returncode == 0 else Status.FAIL,
            ""
            if anonymous.returncode == 0
            else "Neovim plugin installs need this; check url.insteadOf in ~/.gitconfig.local",
        )
    )
    return results


def check_windows_interop() -> list[Result]:
    if not is_wsl():
        return [Result("windows interop", Status.SKIP, "not running under WSL")]
    results: list[Result] = []
    for windows_path in (
        "/mnt/c/Windows/explorer.exe",
        "/mnt/c/Windows/System32/clip.exe",
    ):
        results.append(
            Result(
                f"windows {Path(windows_path).name}",
                Status.PASS if Path(windows_path).exists() else Status.FAIL,
                windows_path,
            )
        )

    powershell = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    read_clipboard = [
        powershell,
        "-NoProfile",
        "-Command",
        "[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-Clipboard",
    ]
    pbcopy = str(SOURCE_DIR / "zsh" / "wsl-bin" / "pbcopy")
    for label, sample, failure_status, advice in (
        (
            "ascii",
            "dotfiles check",
            Status.FAIL,
            "check the pbcopy shim and WSL interop",
        ),
        ("non-ascii", "héllo ✓", Status.WARN, "install win32yank.exe for UTF-8"),
    ):
        run([pbcopy], stdin=sample)
        pasted = run(read_clipboard).stdout.strip()
        detail = "" if pasted == sample else f"read back {pasted!r}; {advice}"
        results.append(
            Result(
                f"clipboard {label} round trip",
                Status.PASS if pasted == sample else failure_status,
                detail,
            )
        )
    return results


def main() -> None:
    if not sys.platform.startswith("linux"):
        print("check_setup.py is built for the Linux and WSL target.")
        sys.exit(2)

    results: list[Result] = []
    results += check_links()
    results.append(check_nvim_version())
    results.append(check_nvim_starts_clean())
    results.append(check_plugins_match_lockfile())
    results.append(check_filetypes())
    results += check_format_on_save()
    results.append(check_sqlfluff_exit_code())
    results.append(check_sql_lint())
    results += check_lsp_attaches()
    results += check_optional_tools()
    results.append(check_fzf_version())
    results += check_zsh()
    results += check_tmux()
    results += check_git()
    results += check_windows_interop()

    for result in results:
        print(f"{result.status.value:5} {result.name:38} {result.detail}")
    if any(result.status is Status.FAIL for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
