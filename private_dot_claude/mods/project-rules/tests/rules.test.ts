import { expect, test } from 'claude-code/testing'

const CONFIG = JSON.stringify([
  { root: '~/strict-proj', compute: 'none', elsewhere: 'no compute for strict-proj.', status: '~/strict-proj/code/notes/STATUS.md' },
  { root: '~/quick-proj', compute: 'quick', elsewhere: 'keep compute off for quick-proj.', status: '~/quick-proj/code/notes/STATUS.md' },
])

const GC = '/home/u/strict-proj/code'

async function bash($: any, command: string) {
  return $.tool.call({ tool: 'Bash', command, tool_use_id: `t-${command.length}` })
}

test('strict-proj on prometheus: blocks local compute and unasked commits, reminds about STATUS.md', async ($, on) => {
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/home/u', stderr: '' } }))
  on('fs.read', () => ({ value: CONFIG }))
  on('session.cwd', () => ({ value: GC }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('tool.call', () => ({ result: {} }))

  await $.session.start({ cwd: GC, surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: 'queue the the runs' })

  expect((await bash($, 'pytest tests/')).deny).toMatch(/no compute for strict-proj/)
  expect((await bash($, 'cd x && uv run python scripts/run_snle.py')).deny).toMatch(/no compute for strict-proj/)
  expect((await bash($, 'python3 -m py_compile sfm/a.py')).deny).toBeUndefined()
  expect((await bash($, 'ssh gpu-box "cd gc && python run.py"')).deny).toBeUndefined()
  expect((await bash($, 'git status && git diff --stat')).deny).toBeUndefined()
  expect((await bash($, 'git commit -m x')).deny).toMatch(/reviews before every commit/)

  const sub = await bash($, 'ssh gpu-box "scripts/run_tasks.sh t.txt bolfi"')
  expect(sub.context?.join(' ')).toMatch(/STATUS\.md/)

  await $.prompt.submit({ text: 'yes' })
  expect((await bash($, 'git commit -m x')).deny).toBeUndefined()
  await $.prompt.submit({ text: 'ok, commit and push the latest' })
  expect((await bash($, 'git push')).deny).toBeUndefined()
})

test('quick-proj: quick checks pass, scripts blocked, chain submits remind about STATUS.md', async ($, on) => {
  const SPH = '/home/u/quick-proj/code'
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/home/u', stderr: '' } }))
  on('fs.read', () => ({ value: CONFIG }))
  on('session.cwd', () => ({ value: SPH }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('tool.call', () => ({ result: {} }))

  await $.session.start({ cwd: SPH, surface: 'terminal', isInteractive: true })
  expect((await bash($, 'python -c "import jax; print(jax.devices())"')).deny).toBeUndefined()
  expect((await bash($, 'python sim.py --sampler mams')).deny).toMatch(/quick-proj/)
  expect((await bash($, 'git commit -m x')).deny).toMatch(/reviews before every commit/)
  const sub = await bash($, 'ssh cluster "cd x && ./submit_cluster_chain.sh 3 job.sh"')
  expect(sub.context?.join(' ')).toMatch(/code\/notes\/STATUS\.md/)
})

test('without a projects.json the mod stays out of the way', async ($, on) => {
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/Users/u', stderr: '' } }))
  on('fs.read', () => { throw new Error('ENOENT') })
  on('session.cwd', () => ({ value: GC }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('tool.call', () => ({ result: {} }))

  await $.session.start({ cwd: GC, surface: 'terminal', isInteractive: true })
  expect((await bash($, 'pytest')).deny).toBeUndefined()
})
