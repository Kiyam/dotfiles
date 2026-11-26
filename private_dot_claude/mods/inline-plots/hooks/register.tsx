import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Plots } from '../types'

const plots = atom({ plugin: 'inline-plots', key: 'plots' } as const, {}, { shape: 'plots-1' })
const MAX_PER_CALL = 4
const COLUMNS = 72
const MAX_BYTES = 2 * 1024 * 1024 // Image's base64 source limit

// ctime, not mtime: rsync -a keeps the remote mtime, so a plot copied back from a cluster
// would look old. ponytail: maxdepth 6 + 10 s timeout bound the scan on big sim trees.
const FIND = (since: number) =>
  `find . -maxdepth 6 \\( -name .git -o -name '.venv*' -o -name node_modules -o -name __pycache__ \\) -prune ` +
  `-o -type f -name '*.png' -newerct @${since} -printf '%C@ %p\\n' 2>/dev/null | sort -rn | head -${MAX_PER_CALL} | cut -d' ' -f2-`

// Width and height from the PNG header (IHDR at bytes 16–23).
function pngSize(b64: string) {
  const head = atob(b64.slice(0, 32))
  const u32 = (at: number) =>
    ((head.charCodeAt(at) << 24) | (head.charCodeAt(at + 1) << 16) | (head.charCodeAt(at + 2) << 8) | head.charCodeAt(at + 3)) >>> 0

  return { width: u32(16), height: u32(20) }
}

const cache = new Map<string, string>()

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    // find's -newerct takes whole seconds; back off one so a plot written in the first second counts.
    const since = Math.floor((await $.clock.now()) / 1000) - 1
    const ran = await next(e)
    if ('deny' in ran && ran.deny !== undefined) return ran
    const found = await $.process.run(['bash', '-c', FIND(since)], { timeoutMs: 10_000 }).catch(() => undefined)
    const paths = found?.stdout.split('\n').filter(Boolean) ?? []
    if (paths.length > 0) {
      const cwd = await $.session.cwd()
      const abs = paths.map(p => `${cwd}/${p.replace(/^\.\//, '')}`)
      abs.forEach(p => cache.delete(p))
      await update($, plots, all => ({ ...all, [e.tool_use_id]: abs }))
    }

    return ran
  })

  on('ui.render', { component: 'ToolUse' }, async ($, e, next) => {
    const row = await next(e)
    if (e.surface !== 'terminal' || e.props.tool !== 'Bash') return row
    const paths = (await read($, plots))[e.props.tool_use_id]
    if (!paths) return row
    const { Box, Image, Text } = $.ui.resolve(e)
    const shown = await Promise.all(
      paths.map(async path => {
        try {
          let b64 = cache.get(path)
          if (!b64) {
            const { size } = await $.fs.stat(path)
            if (size > MAX_BYTES) return <Text dimColor>  {path} (too big to show inline)</Text>
            b64 = (await $.fs.read(path, { as: 'bytes' })).base64
            cache.set(path, b64)
          }
          const { width, height } = pngSize(b64)
          // Terminal cells are about twice as tall as wide.
          const rows = Math.max(1, Math.min(255, Math.round((COLUMNS * height) / width / 2)))

          return (
            <Box flexDirection="column">
              <Text dimColor>  {path.split('/').slice(-2).join('/')}</Text>
              <Image key={path} source={{ png: b64 }} columns={COLUMNS} rows={rows} alt={path} />
            </Box>
          )
        } catch {
          return <Text dimColor>  {path} (gone)</Text>
        }
      }),
    )

    return (
      <Box flexDirection="column">
        {row}
        {shown}
      </Box>
    )
  })
}
