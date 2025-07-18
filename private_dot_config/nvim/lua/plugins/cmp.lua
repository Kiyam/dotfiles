return {
	{
		"saghen/blink.cmp",
		--completion = {
		--  list = {
		--    selection = { preselect = false, auto_insert = false },
		--  },
		--},
		opts = {
			keymap = {
				preset = "super-tab",
				["<Tab>"] = {
					require("blink.cmp.keymap.presets").get("super-tab")["<Tab>"][1],
					require("lazyvim.util.cmp").map({ "snippet_forward", "ai_accept" }),
					"fallback",
				},
			},
		},
	},
}
