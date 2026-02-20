import assert from 'node:assert/strict'
import { afterEach, test, mock } from 'node:test'

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

test('suggestCharts uses mock implementation when mock mode is enabled', async () => {
  const mockModule = await import('../../src/api/mock.js')
  const suggestionResult = {
    charts: [{ id: 'mock', type: 'LINE', xField: 'batch_index', yFields: ['rows'] }],
    sample_data: [{ batch_index: 1, batch_id: 'B1', rows: 10, parent: 2, rows_per_parent: 5 }],
  }
  const mockFn = mock.method(mockModule, 'suggestChartsMock', async () => suggestionResult)
  const clientModule = await loadClientModule({ VITE_USE_MOCK: 'true' })
  const apiSpy = mock.method(clientModule.api, 'post', async () => {
    throw new Error('real API should not be called in mock mode')
  })

  const result = await clientModule.suggestCharts({
    templateId: 'tpl_mock',
    startDate: '2024-01-01',
    endDate: '2024-01-31',
    keyValues: null,
    question: 'mock chart',
    kind: 'pdf',
  })

  assert.equal(mockFn.mock.callCount(), 1)
  assert.equal(apiSpy.mock.callCount(), 0)
  assert.equal(result.charts[0].type, 'line')
  assert.ok(Array.isArray(result.sampleData))

  mockFn.mock.restore()
  apiSpy.mock.restore()
})

test('suggestCharts posts include_sample_data flag in real mode and returns sample data', async () => {
  const clientModule = await loadClientModule({
    VITE_USE_MOCK: 'false',
    VITE_API_BASE_URL: 'http://localhost:9000',
  })

  const backendResponse = {
    data: {
      charts: [
        { id: 'server', type: 'BAR', xField: 'batch_index', yFields: ['rows'], chartTemplateId: null },
      ],
      sample_data: [{ batch_index: 1, batch_id: 'B1', rows: 40, parent: 5, rows_per_parent: 8 }],
    },
  }
  let capturedPayload = null
  const apiSpy = mock.method(clientModule.api, 'post', async (url, payload) => {
    capturedPayload = { url, payload }
    return backendResponse
  })

  const result = await clientModule.suggestCharts({
    templateId: 'tpl_real',
    startDate: '2024-02-01',
    endDate: '2024-02-28',
    keyValues: { region: 'North' },
    question: 'real chart',
    kind: 'pdf',
  })

  assert.equal(apiSpy.mock.callCount(), 1)
  assert.ok(capturedPayload)
  assert.match(capturedPayload.url, /charts\/suggest$/)
  assert.strictEqual(capturedPayload.payload.include_sample_data, true)
  assert.ok(Array.isArray(result.sampleData))
  assert.equal(result.charts[0].type, 'bar')

  apiSpy.mock.restore()
})
