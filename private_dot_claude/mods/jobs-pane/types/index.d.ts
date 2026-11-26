export type Job = {
  id: string
  name: string
  state: string
  elapsed: string
  // Slurm's pending reason, or the command line of a process.
  note: string
}

export type HostJobs = { host: string; jobs: Job[]; error?: string }

export type Snapshot = { at: number; hosts: HostJobs[] }

declare module 'claude-code' {
  interface PluginState {
    'jobs-pane': { snapshot: Shaped<Snapshot | null>; offsets: Shaped<Record<string, number>> }
  }
}
