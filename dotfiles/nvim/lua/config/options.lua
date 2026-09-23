local opt = vim.opt

-- Display
opt.title = true
opt.number = true
opt.numberwidth = 1
opt.list = true -- show tabs and trailing spaces
opt.cursorline = true
opt.colorcolumn = "80"
opt.spell = true

-- Moving around and editing
opt.virtualedit = "block" -- let the cursor move past end of line in <C-v> mode
opt.scrolloff = 3
opt.showmatch = true
opt.matchpairs:append("<:>")
opt.foldmethod = "indent"
opt.foldlevel = 99 -- don't fold by default

-- Indentation defaults. Per-filetype overrides live in autocmds.lua.
opt.tabstop = 4
opt.shiftwidth = 4
opt.softtabstop = 4
opt.expandtab = true
opt.shiftround = true

-- Searching
opt.ignorecase = true
opt.smartcase = true

-- Command-line completion
opt.wildmode = "longest,list,full"
opt.wildignore:append({ "*.pyc", "eggs/**", "*.egg-info/**", "*.o", "*.obj", ".git" })

-- Status line. The UserN highlight groups are defined in autocmds.lua.
opt.statusline = table.concat({
  "%1* %n %*", -- buffer number
  "%5*%{&ff}%*", -- file format
  "%3*%y%*", -- file type
  "%4* %<%F%*", -- full path
  "%2*%m%*", -- modified flag
  "%1*%=%5l%*", -- current line
  "%2*/%L%*", -- total lines
  "%1*%4v %*", -- virtual column number
  "%2*0x%04B %*", -- character under cursor
})

-- Diagnostics show in the sign column only, matching the old ALE setup with
-- virtual text and highlights turned off.
vim.diagnostic.config({
  virtual_text = false,
  underline = false,
  signs = true,
})

-- Plugin settings that must be set before the plugins load.
vim.g["sneak#use_ic_scs"] = 1
vim.g.sql_type_default = "pgsql"
vim.g.markdown_fenced_languages = { "python" }
