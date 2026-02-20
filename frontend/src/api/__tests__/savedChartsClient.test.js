import { afterEach, describe, expect, it, vi } from 'vitest'

const loadClientModule = async (envOverrides) => {
  globalThis.__NEURA_TEST_ENVIRONMENT__ = envOverrides
  const mod = await import('../client.js')
  return mod
}

afterEach(() => {
  delete globalThis.__NEURA_TEST_ENVIRONMENT__
  vi.resetModules()
  vi.restoreAllMocks()
})

const sampleSpec = {
  type: 'line',
  xField: 'batch_index',
  yFields: ['rows'],
}

describe('saved chart client helpers', () => {
  it('persist and list saved charts via mock API', async () => {
    const clientModule = await loadClientModule({ VITE_USE_MOCK: 'true' })
    const templateId = `tpl-${Date.now()}`

    const initial = await clientModule.listSavedCharts({ templateId })
    expect(initial).toEqual([])

    const created = await clientModule.createSavedChart({
      templateId,
      name: 'Vitest mock chart',
      spec: sampleSpec,
    })
    expect(created?.name).toBe('Vitest mock chart')

    const listed = await clientModule.listSavedCharts({ templateId })
    expect(listed).toHaveLength(1)
    expect(listed[0].name).toBe('Vitest mock chart')
  })

  it('updates saved charts via REST when mock mode is disabled', async () => {
    const clientModule = await loadClientModule({ VITE_USE_MOCK: 'false' })
    const templateId = 'tpl-vitest'
    const chartId = 'chart-123'

    const putSpy = vi.spyOn(clientModule.api, 'put').mockResolvedValue({
      data: {
        id: chartId,
        template_id: templateId,
        name: 'Renamed via REST',
        spec: sampleSpec,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      },
    })

    const updated = await clientModule.updateSavedChart({
      templateId,
      chartId,
      name: 'Renamed via REST',
      spec: sampleSpec,
    })

    expect(updated?.name).toBe('Renamed via REST')
    expect(putSpy).toHaveBeenCalledTimes(1)
    expect(putSpy.mock.calls[0][0]).toContain(`/templates/${templateId}/charts/saved/${chartId}`)
  })
})
