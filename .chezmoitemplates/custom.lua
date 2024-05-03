-- every spec file under the "plugins" directory will be loaded automatically by lazy.nvim
--
-- In your plugin files, you can:
-- * add extra plugins
-- * disable/enabled LazyVim plugins
-- * override the configuration of LazyVim plugins
return {
	-- add catpuccin
	{ "catppuccin/nvim", name = "catppuccin", priority = 1000 },

	-- Configure LazyVim to load catpuccin
	{
		"LazyVim/LazyVim",
		opts = {
			colorscheme = "catppuccin-macchiato",
		},
	},
}
