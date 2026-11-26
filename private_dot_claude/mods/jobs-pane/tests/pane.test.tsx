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

test('a host with more rows than fit pages through them', async ($, on) => {
  on('state.get', () => ({ value: { version: 1, value: { shape: 'snapshot-1', value: {
        at: 0,
        hosts: [{ host: 'cluster', jobs: Array.from({ length: 8 }, (_, i) =>
          ({ id: String(i), name: `job${i}`, state: 'PENDING', elapsed: '0:00', note: 'Priority' })) }],
      } } } }))

  // 8 body rows: header + host title leave 6 job rows.
  const ui = await $.ui.mount({ ...PANE, props: { ...PANE.props, scroll: { offset: 0, bodyRows: 8 } } })
  expect(await ui.find({ type: 'Text', text: /1–6 of 8/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /job5/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /job7/ })).toBeUndefined()
  await ui.unmount()
})

test('a taller pane shows more jobs per page', async ($, on) => {
  on('state.get', () => ({ value: { version: 1, value: { shape: 'snapshot-1', value: {
        at: 0,
        hosts: [{ host: 'cluster', jobs: Array.from({ length: 8 }, (_, i) =>
          ({ id: String(i), name: `job${i}`, state: 'PENDING', elapsed: '0:00', note: 'Priority' })) }],
      } } } }))

  const ui = await $.ui.mount({ ...PANE, props: { ...PANE.props, scroll: { offset: 0, bodyRows: 40 } } })
  expect(await ui.find({ type: 'Text', text: /job7/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /of 8/ })).toBeUndefined()
  await ui.unmount()
})
