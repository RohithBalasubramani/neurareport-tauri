import { describe, it, expect, vi, afterEach } from 'vitest'

async function loadClient(envOverrides) {
  vi.resetModules()
  if (envOverrides) {
    globalThis.__NEURA_TEST_ENVIRONMENT__ = envOverrides
  } else {
    delete globalThis.__NEURA_TEST_ENVIRONMENT__
  }
  return import('../client.js')
}

describe('jobs API client', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    delete globalThis.__NEURA_TEST_ENVIRONMENT__
  })

  it('posts payloads to the run-report job endpoint', async () => {
    const client = await loadClient({ VITE_USE_MOCK: 'false' })
    const postSpy = vi.spyOn(client.api, 'post').mockResolvedValue({ data: { job_id: 'job-123' } })
    const payload = {
      templateId: 'tpl-123',
      templateName: 'Quarterly Revenue',
      connectionId: 'conn-1',
      startDate: '2024-01-01 00:00:00',
      endDate: '2024-01-31 23:59:59',
      batchIds: ['a'],
      keyValues: { foo: 'bar' },
      docx: true,
      xlsx: false,
      kind: 'excel',
    }

    const result = await client.runReportAsJob(payload)

    expect(postSpy).toHaveBeenCalledWith(
      '/excel/jobs/run-report',
      expect.objectContaining({
        template_id: 'tpl-123',
        template_name: 'Quarterly Revenue',
        start_date: '2024-01-01 00:00:00',
        end_date: '2024-01-31 23:59:59',
        batch_ids: ['a'],
        key_values: { foo: 'bar' },
        docx: true,
      }),
    )
    expect(result).toEqual({ job_id: 'job-123' })
  })

  it('builds query params for listJobs and getJob requests', async () => {
    const client = await loadClient({ VITE_USE_MOCK: 'false' })
    const getSpy = vi.spyOn(client.api, 'get').mockResolvedValue({
      data: { jobs: [{ id: 'j1', status: 'running' }] },
    })

    const { jobs } = await client.listJobs({
      statuses: ['running'],
      types: ['run_report'],
      limit: 5,
      activeOnly: true,
    })
    expect(getSpy).toHaveBeenCalledWith('/jobs?status=running&type=run_report&limit=5&active_only=true')
    expect(jobs).toHaveLength(1)

    getSpy.mockResolvedValue({ data: { job: { id: 'job-7' } } })
    const job = await client.getJob('job-7')
    expect(getSpy).toHaveBeenLastCalledWith('/jobs/job-7')
    expect(job).toEqual({ id: 'job-7' })
  })

  it('routes through mock APIs when mock mode is enabled', async () => {
    const client = await loadClient({ VITE_USE_MOCK: 'true' })
    const mockApi = await import('../mock.js')
    const runSpy = vi.spyOn(mockApi, 'runReportAsJobMock').mockResolvedValue({ job_id: 'mock-job' })
    const listSpy = vi
      .spyOn(mockApi, 'listJobsMock')
      .mockResolvedValue({ jobs: [{ id: 'mock-job', status: 'queued' }] })
    const getSpy = vi.spyOn(mockApi, 'getJobMock').mockResolvedValue({ id: 'mock-job' })

    const payload = { templateId: 'tpl', startDate: '2024-01-01 00:00:00', endDate: '2024-01-02 00:00:00' }
    const runResult = await client.runReportAsJob(payload)
    expect(runSpy).toHaveBeenCalled()
    expect(runResult).toEqual({ job_id: 'mock-job' })

    const mockJobs = await client.listJobs({ statuses: ['queued'] })
    expect(listSpy).toHaveBeenCalledWith({ statuses: ['queued'], types: undefined, limit: 25, activeOnly: false })
    expect(mockJobs.jobs[0].id).toBe('mock-job')

    const jobDetail = await client.getJob('mock-job')
    expect(getSpy).toHaveBeenCalledWith('mock-job')
    expect(jobDetail).toEqual({ id: 'mock-job' })
  })
})
