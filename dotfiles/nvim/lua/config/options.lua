local opt = vim.opt

opt.title = true
opt.number = true
opt.numberwidth = 1
opt.list = true
opt.cursorline = true
opt.colorcolumn = "80"
opt.spell = true

opt.virtualedit = "block"
opt.scrolloff = 3
opt.showmatch = true
opt.matchpairs:append("<:>")
opt.foldmethod = "indent"
opt.foldlevel = 99 -- start with every fold open

opt.tabstop = 4
opt.shiftwidth = 4
opt.softtabstop = 4
opt.expandtab = true
opt.shiftround = true

opt.ignorecase = true
opt.smartcase = true

opt.wildmode = "longest,list,full"
opt.wildignore:append({ "*.pyc", "eggs/**", "*.egg-info/**", "*.o", "*.obj", ".git" })

opt.statusline = table.concat({
  "%1* %n %*",
  "%5*%{&ff}%*",
  "%3*%y%*",
  "%4* %<%F%*",
  "%2*%m%*",
  "%1*%=%5l%*",
  "%2*/%L%*",
  "%1*%4v %*",
  "%2*0x%04B %*",
})

vim.diagnostic.config({
  virtual_text = false,
  underline = false,
  signs = true,
})

-- Plugin settings that must be set before the plugins load.
vim.g["sneak#use_ic_scs"] = 1
vim.g.sql_type_default = "pgsql"
vim.g.markdown_fenced_languages = { "python" }
