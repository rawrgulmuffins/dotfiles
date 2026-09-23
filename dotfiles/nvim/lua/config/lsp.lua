-- Server definitions come from nvim-lspconfig. A server is enabled only when
-- its executable is on PATH, so a machine missing one doesn't produce an
-- error on every file open.

vim.lsp.config("pyright", {
  settings = {
    pyright = {
      -- ruff sorts imports through conform. Two import sorters fight.
      disableOrganizeImports = true,
    },
  },
})

local servers = {
  "pyright", -- type checking
  "ruff", -- linting
  "bashls",
  "terraformls",
}

for _, server in ipairs(servers) do
  local server_config = vim.lsp.config[server]
  local command = server_config and server_config.cmd
  if type(command) == "table" and vim.fn.executable(command[1]) == 1 then
    vim.lsp.enable(server)
  end
end

vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(event)
    local client = vim.lsp.get_client_by_id(event.data.client_id)
    -- pyright's hover has types and docstrings. ruff's only explains lint
    -- rules, so it shouldn't answer K.
    if client and client.name == "ruff" then
      client.server_capabilities.hoverProvider = false
    end

    -- Neovim maps grn, gra, grr, gri, and K by default. gd is not one of them.
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, { buffer = event.buf })
  end,
})
