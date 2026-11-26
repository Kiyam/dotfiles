// PNG paths each Bash call created or replaced, by tool_use_id.
export type Plots = Record<string, string[]>

declare module 'claude-code' {
  interface PluginState {
    'inline-plots': { plots: Shaped<Plots> }
  }
}
