import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Row } from '../types'

const PANE = 'agents-pane'
const rows = atom({ plugin: 'agents-pane', key: 'rows' } as const, [], {
  shape: 'rows-1',
})
// How far each section is scrolled, in entries from the newest.
const offsets = atom({ plugin: 'agents-pane', key: 'offsets' } as const, { agent: 0, shell: 0 }, {
  shape: 'offsets-1',
})
// Entries each section shows at once; the rest scroll.
const SHOWN = 6

// One short line for what a tool call is doing: the tool and its main argument.
const summarize = (e: Record<string, unknown>): string => {
  const arg = ['command', 'file_path', 'pattern', 'url', 'query', 'description', 'prompt']
    .map(k => e[k])
    .find(v => typeof v === 'string') as string | undefined
  const text = `${e.tool}${arg ? ` ${arg.replace(/\s+/g, ' ')}` : ''}`

  return text.length > 80 ? `${text.slice(0, 79)}…` : text
}

const age = (ms: number): string => {
  const s = Math.max(0, Math.round(ms / 1000))

  return s < 60 ? `${s}s` : s < 3600 ? `${Math.floor(s / 60)}m${s % 60}s` : `${Math.floor(s / 3600)}h${Math.floor((s % 3600) / 60)}m`
}

function patch($: EngineInterface, id: string, fn: (row: Row) => Row) {
  return update($, rows, list => list.map(row => (row.id === id ? fn(row) : row)))
}

const COLOR = { running: 'yellow', background: 'cyan', done: 'green', failed: 'red', aborted: 'red' } as const

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'agents-pane',
      description: 'Show what subagents and shells are doing in a pane',
    })
    void $.ui.open({ id: PANE, title: 'Agents & shells' })

    return next(e)
  })

  on('command.run', { command: 'agents-pane' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Agents & shells' })

    return { text: 'Agents pane opened.' }
  })

  on('agent.spawn', async ($, e, next) => {
    const started = await next(e)
    if ('agentId' in started && started.agentId) {
      const row: Row = {
        id: started.agentId,
        kind: 'agent',
        label: `${e.name ?? e.subagentType}: ${e.description}`,
        status: 'running',
        tools: 0,
        startedAt: await $.clock.now(),
      }
      await update($, rows, list => [...list, row].slice(-300))
    }

    return started
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId) {
      const now = await $.clock.now()
      await patch($, e.agentId, row => ({
        ...row,
        status: e.isAborted ? 'aborted' : e.reason === 'error' ? 'failed' : 'done',
        endedAt: now,
      }))
    }

    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const what = summarize(e as unknown as Record<string, unknown>)
    if (e.agentId) await patch($, e.agentId, row => ({ ...row, last: what, tools: row.tools + 1 }))
    if (e.tool !== 'Bash') return next(e)

    const row: Row = {
      id: e.tool_use_id,
      kind: 'shell',
      label: e.description ?? e.command,
      status: 'running',
      owner: e.agentId,
      last: e.command,
      tools: 0,
      startedAt: await $.clock.now(),
    }
    await update($, rows, list => [...list, row].slice(-300))
    const ran = await next(e)
    const now = await $.clock.now()
    // ponytail: background shells stay "background" — no event marks their exit; poll TaskOutput if that matters.
    const bg = 'result' in ran && !!(ran.result as { backgroundTaskId?: string } | undefined)?.backgroundTaskId
    const failed = 'deny' in ran || ('isError' in ran && !!ran.isError)
    await patch($, row.id, r => ({
      ...r,
      status: bg ? 'background' : failed ? 'failed' : 'done',
      endedAt: bg ? undefined : now,
    }))

    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const { Button } = $.ui.resolve(e)
    const list = await read($, rows)
    const scrolled = await read($, offsets)
    const now = await $.clock.now()
    const section = (kind: Row['kind'], title: string, up: string, down: string) => {
      const all = list.filter(row => row.kind === kind).reverse()
      const last = Math.max(0, all.length - SHOWN)
      const from = Math.min(scrolled[kind], last)
      const move = (by: number) =>
        update($, offsets, o => ({ ...o, [kind]: Math.max(0, Math.min(last, o[kind] + by)) }))

      return (
        <Box flexDirection="column">
          <Box flexDirection="row" gap={1}>
            <Text bold>{title}</Text>
            {all.length > SHOWN && (
              <Text dimColor>
                {from + 1}–{Math.min(from + SHOWN, all.length)} of {all.length}
              </Text>
            )}
            {all.length > SHOWN && (
              <Button key={`${kind}-up`} label="▲" hotkey={up} plain dimColor={from === 0} onPress={() => move(-SHOWN)} />
            )}
            {all.length > SHOWN && (
              <Button key={`${kind}-down`} label="▼" hotkey={down} plain dimColor={from === last} onPress={() => move(SHOWN)} />
            )}
          </Box>
          {all.length === 0 && <Text dimColor>none yet</Text>}
          {draw(all.slice(from, from + SHOWN))}
        </Box>
      )
    }
    const draw = (shown: Row[]) =>
      shown.map(row => (
          <Box flexDirection="column">
            <Text wrap="truncate-end" dimColor={row.status === 'done'}>
              <Text color={COLOR[row.status]}>{row.status.padEnd(10)}</Text>
              {age((row.endedAt ?? now) - row.startedAt).padStart(6)} {row.label}
              {row.kind === 'agent' ? ` (${row.tools} tools)` : ''}
            </Text>
            {row.kind === 'agent' && row.last && row.status === 'running' && (
              <Text dimColor wrap="truncate-end">
                {'           └ '}
                {row.last}
              </Text>
            )}
          </Box>
        ))

    return (
      <Box flexDirection="column" gap={1}>
        {section('agent', 'Agents', '1', '2')}
        {section('shell', 'Shells', '3', '4')}
      </Box>
    )
  })
}
