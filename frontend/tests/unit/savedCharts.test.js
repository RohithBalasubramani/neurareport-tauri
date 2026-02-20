import assert from 'node:assert/strict'
import { afterEach, mock, test } from 'node:test'

const loadClientModule = async (envOverrides) => {
  globalThis.__NEURA_TEST_ENVIRONMENT__ = envOverrides
  const mod = await import(
    `../../src/api/client.js?test=${Date.now()}_${Math.random().toString(16).slice(2)}`
  )
  return mod
}

afterEach(() => {
  delete globalThis.__NEURA_TEST_ENVIRONMENT__
})

const sampleSpec = {
  type: 'bar',
  xField: 'batch_index',
  yFields: ['rows'],
  chartTemplateId: 'time_series_basic',
}

test('saved chart helpers operate in mock mode', async () => {
  const clientModule = await loadClientModule({ VITE_USE_MOCK: 'true' })
  const templateId = 'tpl-mock'

  const initial = await clientModule.listSavedCharts({ templateId })
  assert.deepEqual(initial, [])

  const created = await clientModule.createSavedChart({
    templateId,
    name: 'Mock chart',
    spec: sampleSpec,
  })
  assert.equal(created.name, 'Mock chart')

  const listed = await clientModule.listSavedCharts({ templateId })
  assert.equal(listed.length, 1)

  await clientModule.deleteSavedChart({ templateId, chartId: created.id })
  const afterDelete = await clientModule.listSavedCharts({ templateId })
  assert.deepEqual(afterDelete, [])
})

test('saved chart helpers issue REST calls in real mode', async () => {
  const clientModule = await loadClientModule({ VITE_USE_MOCK: 'false' })
  const templateId = 'tpl-real'

  const getSpy = mock.method(clientModule.api, 'get', async () => ({
    data: {
      charts: [
        {
          id: 'c1',
          template_id: templateId,
          name: 'Server chart',
          spec: sampleSpec,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
    },
  }))
  const postSpy = mock.method(clientModule.api, 'post', async (_url, payload) => ({
    data: {
      id: 'new-chart',
      template_id: payload.template_id,
      name: payload.name,
      spec: payload.spec,
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
  }))
  const deleteSpy = mock.method(clientModule.api, 'delete', async () => ({ data: { status: 'ok' } }))

  const charts = await clientModule.listSavedCharts({ templateId })
  assert.equal(charts.length, 1)
  assert.equal(getSpy.mock.callCount(), 1)

  const created = await clientModule.createSavedChart({
    templateId,
    name: 'Server create',
    spec: sampleSpec,
  })
  assert.equal(created.name, 'Server create')
  assert.equal(postSpy.mock.callCount(), 1)

  await clientModule.deleteSavedChart({ templateId, chartId: 'new-chart' })
  assert.equal(deleteSpy.mock.callCount(), 1)

  getSpy.mock.restore()
  postSpy.mock.restore()
  deleteSpy.mock.restore()
})

test('updateSavedChart issues PUT in real mode', async () => {
  const clientModule = await loadClientModule({ VITE_USE_MOCK: 'false' })
  const templateId = 'tpl-update'
  const chartId = 'chart-1'

  const putSpy = mock.method(clientModule.api, 'put', async () => ({
    data: {
      id: chartId,
      template_id: templateId,
      name: 'Renamed chart',
      spec: sampleSpec,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-05T00:00:00Z',
    },
  }))

  const updated = await clientModule.updateSavedChart({
    templateId,
    chartId,
    name: 'Renamed chart',
    spec: sampleSpec,
  })
  assert.equal(updated.name, 'Renamed chart')
  assert.equal(putSpy.mock.callCount(), 1)

  putSpy.mock.restore()
})
