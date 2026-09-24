local function github(repo)
  return "https://github.com/" .. repo
end

local has_deno = vim.fn.executable("deno") == 1

-- peek.nvim ships its preview app as TypeScript and needs Deno to build it.
-- The lockfile installs it even without Deno, so the build is skipped there.
-- Registered before vim.pack.add() so the hook also fires on first install.
-- Waits for the build, since opening a preview needs its output.
vim.api.nvim_create_autocmd("PackChanged", {
  callback = function(event)
    local name, kind = event.data.spec.name, event.data.kind
    if
      name == "peek.nvim"
      and (kind == "install" or kind == "update")
      and has_deno
    then
      -- The bundle is gitignored, so an update keeps the old one. Removing it
      -- first means a failed build leaves no output instead of a stale one.
      os.remove(event.data.path .. "/public/main.bundle.js")
      local build = vim
        .system({ "deno", "task", "--quiet", "build:fast" }, { cwd = event.data.path, text = true })
        :wait(120000)
      if build.code ~= 0 then
        vim.notify(
          "peek.nvim build failed (exit " .. build.code .. "):\n" .. (build.stderr or ""),
          vim.log.levels.ERROR
        )
      end
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

if has_deno then
  table.insert(specs, github("toppair/peek.nvim"))
end

vim.pack.add(specs)

require("gitsigns").setup({
  on_attach = function(bufnr)
    local gitsigns = require("gitsigns")
    local function hunk_jump(key, direction)
      vim.keymap.set("n", key, function()
        if vim.wo.diff then
          vim.cmd.normal({ key, bang = true })
        else
          gitsigns.nav_hunk(direction)
        end
      end, { buffer = bufnr })
    end
    hunk_jump("]c", "next")
    hunk_jump("[c", "prev")
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

if has_deno then
  require("peek").setup({ app = "browser" })
end
