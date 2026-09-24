vim.lsp.config("pyright", {
  settings = {
    pyright = {
      -- ruff sorts imports through conform. Two import sorters fight.
      disableOrganizeImports = true,
    },
  },
})

vim.lsp.enable({ "pyright", "ruff", "bashls", "terraformls" })

vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(event)
    local client = vim.lsp.get_client_by_id(event.data.client_id)
    -- pyright's hover has types and docstrings. ruff's only explains lint
    -- rules, so it shouldn't answer K.
    if client and client.name == "ruff" then
      client.server_capabilities.hoverProvider = false
    end

    vim.keymap.set("n", "gd", vim.lsp.buf.definition, { buffer = event.buf })
  end,
})
