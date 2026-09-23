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
  github("justinmk/vim-sneak"),
  github("tpope/vim-repeat"),
  github("tpope/vim-surround"),

  github("lewis6991/gitsigns.nvim"),
  github("tpope/vim-fugitive"),

  github("ibhagwan/fzf-lua"),

  github("neovim/nvim-lspconfig"),
  github("stevearc/conform.nvim"),
  github("mfussenegger/nvim-lint"),
  github("lifepillar/pgsql.vim"),

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
      -- NOTE: sqlfluff exits 1 when violations remain that it can't fix, but
      -- still prints the fixed SQL. Treating that as failure discards the fixes.
      exit_codes = { 0, 1 },
    },
  },
  format_on_save = {
    timeout_ms = 2000, -- sqlfluff is slow on large files
    lsp_format = "fallback",
  },
})

local lint = require("lint")
lint.linters_by_ft = {}
if vim.fn.executable("sqlfluff") == 1 then
  lint.linters_by_ft.sql = { "sqlfluff" }
end
lint.linters.sqlfluff.args = { "lint", "--format=json", "--dialect=postgres", "-" }
vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
  callback = function()
    lint.try_lint()
  end,
})

if vim.fn.executable("deno") == 1 then
  require("peek").setup({ app = "browser" })
end
