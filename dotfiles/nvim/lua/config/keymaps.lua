local map = vim.keymap.set
local fzf = require("fzf-lua")

-- Fuzzy find files tracked by git, and grep the project. Terminals send
-- Ctrl+/ as either <C-_> or <C-/>, so both are mapped.
map("n", "<C-f>", fzf.git_files)
map("n", "<C-_>", fzf.live_grep)
map("n", "<C-/>", fzf.live_grep)

-- Move by screen line so wrapped lines aren't skipped.
map("n", "j", "gj")
map("n", "k", "gk")

-- Increment with Ctrl-z, kept from the vimrc for muscle memory. <C-a> also
-- still works, since the tmux prefix is the default Ctrl-b.
map({ "n", "x" }, "<C-z>", "<C-a>")

-- Switch buffers.
map("n", "H", "<Cmd>bprev<CR>")
map("n", "L", "<Cmd>bnext<CR>")

-- Move between windows.
map("n", "<C-h>", "<C-w>h")
map("n", "<C-j>", "<C-w>j")
map("n", "<C-k>", "<C-w>k")
map("n", "<C-l>", "<C-w>l")

-- Pasting over a selection keeps the register intact, so the same text can be
-- pasted repeatedly. Works with a register prefix too ("rp).
map("x", "p", "P")

vim.api.nvim_create_user_command("TrimWhitespace", [[%s/\s\+$//e]], {})
