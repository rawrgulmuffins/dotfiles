-- Plugins are managed by vim.pack. Exact revisions are pinned in
-- nvim-pack-lock.json next to init.lua. Update with :lua vim.pack.update()
-- and commit the lockfile afterward.

local function github(repo)
  return "https://github.com/" .. repo
end

-- peek.nvim ships its preview app as TypeScript and needs Deno to build it.
-- Registered before vim.pack.add() so the hook also fires on first install.
vim.api.nvim_create_autocmd("PackChanged", {
  callback = function(event)
    local name, kind = event.data.spec.name, event.data.kind
    if name == "peek.nvim" and (kind == "install" or kind == "update") then
      vim.system({ "deno", "task", "--quiet", "build:fast" }, { cwd = event.data.path })
    end
  end,
})

local specs = {
  -- Editing
  github("justinmk/vim-sneak"),
  github("tpope/vim-repeat"),
  github("tpope/vim-surround"),

  -- Git
  github("lewis6991/gitsigns.nvim"),
  github("tpope/vim-fugitive"),

  -- Finding files and text. Uses the fzf and rg binaries.
  github("ibhagwan/fzf-lua"),

  -- Language support
  github("neovim/nvim-lspconfig"),
  github("stevearc/conform.nvim"),
  github("mfussenegger/nvim-lint"),
  github("lifepillar/pgsql.vim"),

  -- UI
  github("ap/vim-buftabline"),
  github("rafi/awesome-vim-colorschemes"),
}

if vim.fn.executable("deno") == 1 then
  table.insert(specs, github("toppair/peek.nvim"))
end

vim.pack.add(specs)

require("gitsigns").setup({
  on_attach = function(bufnr)
    local gitsigns = require("gitsigns")
    -- ]c and [c jump between hunks, as they did with vim-gitgutter. In diff
    -- mode they keep their built-in meaning.
    vim.keymap.set("n", "]c", function()
      if vim.wo.diff then
        vim.cmd.normal({ "]c", bang = true })
      else
        gitsigns.nav_hunk("next")
      end
    end, { buffer = bufnr })
    vim.keymap.set("n", "[c", function()
      if vim.wo.diff then
        vim.cmd.normal({ "[c", bang = true })
      else
        gitsigns.nav_hunk("prev")
      end
    end, { buffer = bufnr })
  end,
})

require("fzf-lua").setup({})

require("conform").setup({
  formatters_by_ft = {
    -- Import sorting plus formatting, the same job black and isort did
    -- under ALE. Lint autofixes (ruff check --fix) are left off so saving
    -- never deletes an import that is unused only because the code using it
    -- isn't written yet.
    python = { "ruff_organize_imports", "ruff_format" },
    sh = { "shfmt" },
    sql = { "sqlfluff" },
    terraform = { "terraform_fmt" },
    ["terraform-vars"] = { "terraform_fmt" },
    ["*"] = { "trim_whitespace", "trim_newlines" },
  },
  formatters = {
    sqlfluff = {
      args = { "fix", "--dialect=postgres", "-" },
      require_cwd = false,
    },
  },
  format_on_save = {
    timeout_ms = 2000, -- sqlfluff is slow on large files
    lsp_format = "fallback",
  },
})

-- conform skips formatters that aren't installed, but nvim-lint raises an
-- error on every buffer enter. Only register sqlfluff when it exists.
local lint = require("lint")
lint.linters_by_ft = {}
if vim.fn.executable("sqlfluff") == 1 then
  lint.linters_by_ft.sql = { "sqlfluff" }
end
lint.linters.sqlfluff.args = { "lint", "--format=json", "--dialect=postgres", "-" }
-- BufEnter rather than BufReadPost, since filetype detection hasn't run yet
-- when this config's BufReadPost autocmds fire.
vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
  callback = function()
    lint.try_lint()
  end,
})

if vim.fn.executable("deno") == 1 then
  require("peek").setup({ app = "browser" })
end
