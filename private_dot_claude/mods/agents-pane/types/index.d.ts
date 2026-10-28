export type Row = {
  id: string
  kind: 'agent' | 'shell'
  label: string
  status: 'running' | 'background' | 'done' | 'failed' | 'aborted'
  owner?: string
  last?: string
  tools: number
  startedAt: number
  endedAt?: number
}

declare module 'claude-code' {
  interface PluginState {
    'agents-pane': { rows: Shaped<Row[]> }
  }
}
