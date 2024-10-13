return {
  {
    "hrsh7th/nvim-cmp",
    opts = function(_, opts)
      local cmp = require("cmp")
      local auto_select = false
      opts.preselect = auto_select and cmp.PreselectMode.Item or cmp.PreselectMode.None
      opts.completion = { completeopt = "menu,menuone,noselect" }
      opts.mapping = cmp.mapping.preset.insert({
        ["<CR>"] = LazyVim.cmp.confirm({ select = auto_select }),
      })
    end,
  },
}
