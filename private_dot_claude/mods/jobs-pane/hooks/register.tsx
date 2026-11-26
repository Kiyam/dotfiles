import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { HostJobs, Job, Snapshot } from '../types'

const PANE = 'jobs-pane'
const POLL_MS = 120_000
const snapshot = atom({ plugin: 'jobs-pane', key: 'snapshot' } as const, null, { shape: 'snapshot-1' })
// How far each host's list is scrolled, in rows from the top.
const offsets = atom({ plugin: 'jobs-pane', key: 'offsets' } as const, {} as Record<string, number>, { shape: 'offsets-1' })
// Each host gets an equal share of the pane's height (drag its edge for more); the rest pages.
const MIN_SHOWN = 3

type Target = { host: string; kind: 'slurm' | 'proc'; dir: string; off?: boolean }

// One shared connection per host: infinity refuses this machine after repeated fresh connections.
const SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'ControlMaster=auto',
  '-o', 'ControlPath=~/.ssh/cm-%C', '-o', 'ControlPersist=900']

const REMOTE = {
  slurm: `echo "HOME=$HOME"; squeue -u "$USER" -h -o '%i|%j|%T|%M|%Z|%r'`,
  // ursula has no Slurm: list the user's task runners and pythons with the folder they run in.
  proc: `echo "HOME=$HOME"; for p in $(pgrep -u "$USER" -f 'run_tasks|python'); do
    c=$(readlink /proc/$p/cwd 2>/dev/null) || continue
    echo "$p|$(ps -o comm= -p $p)|RUNNING|$(ps -o etime= -p $p | tr -d ' ')|$c|$(ps -o args= -p $p)"; done`,
}

const expand = (path: string, home: string) => path.replace(/^~(?=\/|$)/, home)
const under = (path: string, dir: string) => path === dir || path.startsWith(`${dir}/`)

async function targetsFor($: EngineInterface): Promise<Target[]> {
  const home = (await $.process.run(['sh', '-c', 'printf %s "$HOME"'])).stdout
  const cwd = await $.session.cwd()
  const map = JSON.parse(await $.fs.read(`${$.plugin.root}/projects.json`)) as Record<string, Target[]>
  const key = Object.keys(map).find(project => under(cwd, expand(project, home)))

  return key ? (map[key] ?? []).filter(t => !t.off) : []
}

async function poll($: EngineInterface, t: Target): Promise<HostJobs> {
  try {
    const ran = await $.process.run([...SSH, t.host, REMOTE[t.kind]], { timeoutMs: 30_000 })
    if (ran.exitCode !== 0) return { host: t.host, jobs: [], error: ran.stderr.trim().split('\n').pop() || `exit ${ran.exitCode}` }
    const [first, ...lines] = ran.stdout.trim().split('\n')
    const dir = expand(t.dir, (first ?? '').replace(/^HOME=/, ''))
    const jobs: Job[] = lines
      .map(line => line.split('|'))
      .filter(f => f.length >= 6 && under(f[4] ?? '', dir))
      .map(([id = '', name = '', state = '', elapsed = '', , ...rest]) => {
        const note = rest.join('|')
        // A process's own name is just "python": show its command line without the interpreter.
        return t.kind === 'proc'
          ? { id, name: note.replace(/^(\S*\/)?(python3?|bash)\s+/, ''), state, elapsed, note }
          : { id, name, state, elapsed, note }
      })

    return { host: t.host, jobs }
  } catch (err) {
    return { host: t.host, jobs: [], error: String(err) }
  }
}

async function refresh($: EngineInterface) {
  const targets = await targetsFor($)
  const hosts = await Promise.all(targets.map(t => poll($, t)))
  await update($, snapshot, () => ({ at: Date.now(), hosts }))
}

// Array tasks of one job and state collapse to a single row: "levin_sobol ×13".
function group(jobs: Job[]) {
  const rows = new Map<string, { job: Job; count: number }>()
  for (const job of jobs) {
    const key = `${job.id.split('_')[0]}|${job.name}|${job.state}`
    const row = rows.get(key)
    if (row) row.count++
    else rows.set(key, { job, count: 1 })
  }

  return [...rows.values()]
}

const COLOR: Record<string, string> = { RUNNING: 'green', PENDING: 'yellow', COMPLETING: 'cyan' }

let ticker: { cancel: () => unknown } | undefined

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'jobs-pane',
      description: "Toggle a pane of this project's cluster jobs (hypatia/ursula/infinity)",
    })

    return next(e)
  })

  on('command.run', { command: 'jobs-pane' }, async $ => {
    if ((await $.ui.panes()).some(pane => pane.id === PANE)) {
      ticker?.cancel()
      ticker = undefined
      await $.ui.close({ id: PANE })

      return { text: 'Jobs pane closed.' }
    }
    if ((await targetsFor($)).length === 0)
      return { text: `No cluster folders mapped for this project. Add it to ${$.plugin.root}/projects.json.` }
    await $.ui.open({ id: PANE, title: 'Cluster jobs' })
    void refresh($)
    ticker?.cancel()
    ticker = await $.clock.every(POLL_MS, () => refresh($))

    return { text: 'Jobs pane opened; refreshes every 2 min.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const snap: Snapshot | null = await read($, snapshot)
    if (!snap) return <Text dimColor>Checking clusters…</Text>
    const scrolled = await read($, offsets)
    const ago = Math.round((Date.now() - snap.at) / 1000)
    // Body rows minus the header line, then one title line per host.
    const body = e.props.scroll?.bodyRows ?? 20
    const SHOWN = Math.max(MIN_SHOWN, Math.floor((body - 1 - snap.hosts.length) / Math.max(1, snap.hosts.length)))
    const section = (host: HostJobs, k: number) => {
      const all = group(host.jobs)
      const last = Math.max(0, all.length - SHOWN)
      const from = Math.min(scrolled[host.host] ?? 0, last)
      const move = (by: number) =>
        update($, offsets, o => ({ ...o, [host.host]: Math.max(0, Math.min(last, (o[host.host] ?? 0) + by)) }))
      const paged = all.length > SHOWN

      return (
        <Box flexDirection="column">
          <Box flexDirection="row" gap={1}>
            <Text bold>{host.host}</Text>
            {paged && <Text dimColor>{from + 1}–{Math.min(from + SHOWN, all.length)} of {all.length}</Text>}
            {paged && (
              <Button key={`${host.host}-up`} label="▲" hotkey={String(2 * k + 1)} plain dimColor={from === 0} onPress={() => move(-SHOWN)} />
            )}
            {paged && (
              <Button key={`${host.host}-down`} label="▼" hotkey={String(2 * k + 2)} plain dimColor={from === last} onPress={() => move(SHOWN)} />
            )}
          </Box>
          {host.error && <Text color="red" wrap="truncate-end">{host.error}</Text>}
          {!host.error && all.length === 0 && <Text dimColor>no jobs</Text>}
          {all.slice(from, from + SHOWN).map(({ job, count }) => (
            <Text wrap="truncate-end">
              <Text color={COLOR[job.state] ?? 'red'}>{job.state.slice(0, 7).padEnd(8)}</Text>
              {job.elapsed.padStart(11)} {job.name}
              {count > 1 ? ` ×${count}` : ''}
              <Text dimColor> {job.state === 'PENDING' ? `(${job.note})` : job.id.split('_')[0]}</Text>
            </Text>
          ))}
        </Box>
      )
    }

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1}>
          <Text dimColor>updated {ago < 60 ? `${ago}s` : `${Math.floor(ago / 60)}m`} ago</Text>
          <Button key="refresh" label="refresh" hotkey="r" plain onPress={() => refresh($)} />
        </Box>
        {snap.hosts.map(section)}
      </Box>
    )
  })
}
