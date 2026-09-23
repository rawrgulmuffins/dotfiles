local map = vim.keymap.set
local fzf = require("fzf-lua")

-- Terminals send Ctrl+/ as either <C-_> or <C-/>, so both are mapped.
map("n", "<C-f>", fzf.git_files)
map("n", "<C-_>", fzf.live_grep)
map("n", "<C-/>", fzf.live_grep)

map("n", "j", "gj")
map("n", "k", "gk")

map({ "n", "x" }, "<C-z>", "<C-a>")

map("n", "H", "<Cmd>bprev<CR>")
map("n", "L", "<Cmd>bnext<CR>")

map("n", "<C-h>", "<C-w>h")
map("n", "<C-j>", "<C-w>j")
map("n", "<C-k>", "<C-w>k")
map("n", "<C-l>", "<C-w>l")

-- Pasting over a selection leaves the register alone, so the same text can be
-- pasted repeatedly.
map("x", "p", "P")

vim.api.nvim_create_user_command("TrimWhitespace", [[%s/\s\+$//e]], {})
