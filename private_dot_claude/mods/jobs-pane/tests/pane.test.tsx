import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'jobs-pane',
  component: 'Pane',
  requestId: 'jobs-pane',
  surface: 'terminal',
  props: { title: 'Cluster jobs', isFocused: false, bodyColumns: 80, placement: 'dock', scroll: { offset: 0, bodyRows: 20 }, view: {} },
} as const

test('the pane draws hosts, grouped array tasks and errors', async ($, on) => {
  on('state.get', () => ({
    value: {
      version: 1,
      value: { shape: 'snapshot-1', value: {
        at: 0,
        hosts: [
          { host: 'cluster', jobs: [
            { id: '7_1', name: 'sweep', state: 'RUNNING', elapsed: '1:00', note: 'None' },
            { id: '7_2', name: 'sweep', state: 'RUNNING', elapsed: '2:00', note: 'None' },
            { id: '8', name: 'chain', state: 'PENDING', elapsed: '0:00', note: 'Dependency' },
          ] },
          { host: 'gpu-box', jobs: [], error: 'Connection refused' },
        ],
      } },
    },
  }))

  const ui = await $.ui.mount(PANE)
  expect((await ui.find({ type: 'Text', text: /sweep ×2/ }))).toBeDefined()
  expect((await ui.find({ type: 'Text', text: /Dependency/ }))).toBeDefined()
  expect((await ui.find({ type: 'Text', text: /Connection refused/ }))?.text).toBe('Connection refused')
  await ui.unmount()
})
