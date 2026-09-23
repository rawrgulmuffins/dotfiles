local autocmd = vim.api.nvim_create_autocmd

vim.filetype.add({
  extension = {
    html = "htmldjango",
    jinja = "htmldjango",
    j2 = "htmldjango",
    tf = "terraform",
  },
  pattern = {
    [".*%.sh%.j2"] = {
      function()
        return "sh", function(bufnr)
          vim.b[bufnr].is_bash = 1
        end
      end,
    },
  },
})

local two_space_filetypes = {
  "css",
  "eruby",
  "groovy",
  "htmldjango",
  "javascript",
  "puppet",
  "ruby",
  "tex",
  "yaml",
}
autocmd("FileType", {
  pattern = two_space_filetypes,
  callback = function()
    vim.opt_local.shiftwidth = 2
    vim.opt_local.softtabstop = 2
    vim.opt_local.tabstop = 2
  end,
})

autocmd("FileType", {
  pattern = "python",
  callback = function()
    vim.opt_local.textwidth = 0
  end,
})

autocmd("FileType", {
  pattern = "sh",
  callback = function()
    vim.opt_local.smartindent = false
    vim.opt_local.autoindent = false
    vim.opt_local.indentexpr = ""
  end,
})

-- peek.nvim is only installed when deno is on PATH.
autocmd("FileType", {
  pattern = "markdown",
  callback = function(event)
    local ok, peek = pcall(require, "peek")
    if not ok then
      return
    end
    local buffer_map = function(lhs, rhs)
      vim.keymap.set("n", lhs, rhs, { buffer = event.buf })
    end
    buffer_map("<C-s>", peek.open)
    buffer_map("<M-s>", peek.close)
    buffer_map("<C-p>", function()
      if peek.is_open() then
        peek.close()
      else
        peek.open()
      end
    end)
  end,
})

-- Reapplied on every colorscheme change, since loading a colorscheme clears
-- custom highlights.
autocmd("ColorScheme", {
  callback = function()
    local highlight = vim.api.nvim_set_hl
    highlight(0, "Search", { fg = "white", bg = "DarkMagenta", ctermfg = "white", ctermbg = "DarkMagenta" })
    highlight(0, "Visual", { fg = "white", bg = "DarkBlue", ctermfg = "white", ctermbg = "DarkBlue" })
    highlight(0, "ExtraWhitespace", { bg = "red", ctermbg = "red" })

    highlight(0, "User1", { fg = "#eea040", bg = "#222222" })
    highlight(0, "User2", { fg = "#dd3333", bg = "#222222" })
    highlight(0, "User3", { fg = "#ff66ff", bg = "#222222" })
    highlight(0, "User4", { fg = "#a0ee40", bg = "#222222" })
    highlight(0, "User5", { fg = "#eeee40", bg = "#222222" })
  end,
})

-- :match is per window, so it's set on every window a buffer is shown in.
autocmd({ "BufWinEnter", "WinNew" }, {
  callback = function()
    vim.cmd([[match ExtraWhitespace /\s\+$/]])
  end,
})

vim.o.background = "dark"
vim.cmd.colorscheme("afterglow")
