import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'agents-pane',
  component: 'Pane',
  requestId: 'agents-pane',
  surface: 'terminal',
  props: {
    title: 'Agents & shells',
    isFocused: false,
    bodyColumns: 120,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 30 },
    view: {},
  },
} as const

test('agents and shells show with their state', async ($, on) => {
  on('command.register', () => ({ value: { command: 'agents-pane' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('agent.spawn', () => ({ model: 'x', agentId: 'a1' }))
  on('tool.call', (_, e) =>
    e.tool === 'Bash' && e.run_in_background ? { result: { backgroundTaskId: 't1' } } : { result: {} },
  )
  on('turn.complete', () => ({ text: '' }))
  on('clock.now', () => ({ value: 1000 }))

  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn({ prompt: 'p', description: 'find bugs', subagentType: 'Explore' })
  await $.tool.call({ tool: 'Grep', pattern: 'TODO', agentId: 'a1' } as never)
  await $.tool.call({ tool: 'Bash', command: 'pytest', description: 'run tests' })
  await $.tool.call({ tool: 'Bash', command: 'sleep 99', run_in_background: true })

  let ui = await $.ui.mount(PANE)
  expect((await ui.find({ type: 'Text', text: /find bugs/ }))?.text).toMatch(/running.*Explore: find bugs \(1 tools\)/)
  expect((await ui.find({ type: 'Text', text: /Grep TODO/ }))?.text).toMatch(/Grep TODO/)
  expect((await ui.find({ type: 'Text', text: /run tests/ }))?.text).toMatch(/done/)
  expect((await ui.find({ type: 'Text', text: /sleep 99/ }))?.text).toMatch(/background/)
  await ui.unmount()

  await $.turn.complete({ agentId: 'a1', answer: '', durationMs: 1, isAborted: false, turnId: 't', reason: 'answer' } as never)
  ui = await $.ui.mount(PANE)
  expect((await ui.find({ type: 'Text', text: /find bugs/ }))?.text).toMatch(/^done/)
  await ui.unmount()
})
