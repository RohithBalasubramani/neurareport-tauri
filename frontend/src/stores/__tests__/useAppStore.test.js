/**
 * Comprehensive tests for the Zustand app store.
 *
 * Tests cover:
 * 1. Initial state
 * 2. State mutations
 * 3. Persistence behavior
 * 4. Discovery state management
 * 5. Edge cases
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { act } from '@testing-library/react'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = value
    }),
    removeItem: vi.fn((key) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(global, 'localStorage', { value: localStorageMock })

describe('useAppStore', () => {
  beforeEach(() => {
    vi.resetModules()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial setup state', async () => {
      const { useAppStore } = await import('../useAppStore.js')
      const state = useAppStore.getState()

      expect(state.setupNav).toBe('connect')
      expect(state.setupStep).toBe('connect')
      expect(state.templateKind).toBe('pdf')
      expect(state.hydrated).toBe(false)
    })

    it('should have correct initial connection state', async () => {
      const { useAppStore } = await import('../useAppStore.js')
      const state = useAppStore.getState()

      expect(state.connection).toEqual({
        status: 'disconnected',
        lastMessage: null,
        saved: false,
        name: '',
      })
      expect(state.savedConnections).toEqual([])
      expect(state.activeConnectionId).toBeNull()
      expect(state.activeConnection).toBeNull()
    })

    it('should have correct initial template state', async () => {
      const { useAppStore } = await import('../useAppStore.js')
      const state = useAppStore.getState()

      expect(state.templateId).toBeNull()
      expect(state.templates).toEqual([])
      expect(state.verifyArtifacts).toBeNull()
      expect(state.lastApprovedTemplate).toBeNull()
    })

    it('should have correct initial discovery state', async () => {
      const { useAppStore } = await import('../useAppStore.js')
      const state = useAppStore.getState()

      expect(state.discoveryResults).toEqual({})
      expect(state.discoveryMeta).toBeNull()
      expect(state.discoveryFinding).toBe(false)
    })

    it('should have correct initial cache state', async () => {
      const { useAppStore } = await import('../useAppStore.js')
      const state = useAppStore.getState()

      expect(state.cacheKey).toBe(0)
      expect(state.htmlUrls).toEqual({ final: null, template: null, llm2: null })
    })
  })

  describe('Setup Navigation', () => {
    it('should update setupNav', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSetupNav('generate')
      })

      expect(useAppStore.getState().setupNav).toBe('generate')
    })

    it('should update setupStep', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSetupStep('upload')
      })

      expect(useAppStore.getState().setupStep).toBe('upload')
    })

    it('should update templateKind', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplateKind('excel')
      })

      expect(useAppStore.getState().templateKind).toBe('excel')
    })

    it('should normalize invalid templateKind to pdf', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplateKind('invalid')
      })

      expect(useAppStore.getState().templateKind).toBe('pdf')
    })
  })

  describe('Connection Management', () => {
    it('should update connection status', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setConnection({
          status: 'connected',
          name: 'Test DB',
        })
      })

      const state = useAppStore.getState()
      expect(state.connection.status).toBe('connected')
      expect(state.connection.name).toBe('Test DB')
    })

    it('should add saved connection', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const conn = {
        id: 'conn-1',
        name: 'Connection 1',
        db_type: 'sqlite',
      }

      act(() => {
        useAppStore.getState().addSavedConnection(conn)
      })

      const state = useAppStore.getState()
      expect(state.savedConnections).toHaveLength(1)
      expect(state.savedConnections[0].id).toBe('conn-1')
    })

    it('should update existing connection when adding with same id', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().addSavedConnection({
          id: 'conn-1',
          name: 'Original',
        })
        useAppStore.getState().addSavedConnection({
          id: 'conn-1',
          name: 'Updated',
        })
      })

      const state = useAppStore.getState()
      expect(state.savedConnections).toHaveLength(1)
      expect(state.savedConnections[0].name).toBe('Updated')
    })

    it('should update saved connection', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSavedConnections([
          { id: 'conn-1', name: 'Original', status: 'unknown' },
        ])
        useAppStore.getState().updateSavedConnection('conn-1', {
          status: 'connected',
        })
      })

      const state = useAppStore.getState()
      expect(state.savedConnections[0].status).toBe('connected')
    })

    it('should remove saved connection', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSavedConnections([
          { id: 'conn-1', name: 'Connection 1' },
          { id: 'conn-2', name: 'Connection 2' },
        ])
        useAppStore.getState().removeSavedConnection('conn-1')
      })

      const state = useAppStore.getState()
      expect(state.savedConnections).toHaveLength(1)
      expect(state.savedConnections[0].id).toBe('conn-2')
    })

    it('should clear active connection when removing it', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSavedConnections([
          { id: 'conn-1', name: 'Connection 1' },
        ])
        useAppStore.getState().setActiveConnectionId('conn-1')
        useAppStore.getState().removeSavedConnection('conn-1')
      })

      const state = useAppStore.getState()
      expect(state.activeConnectionId).toBeNull()
      expect(state.activeConnection).toBeNull()
    })

    it('should set active connection from saved connections', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSavedConnections([
          { id: 'conn-1', name: 'Connection 1' },
        ])
        useAppStore.getState().setActiveConnectionId('conn-1')
      })

      const state = useAppStore.getState()
      expect(state.activeConnectionId).toBe('conn-1')
      expect(state.activeConnection?.id).toBe('conn-1')
    })
  })

  describe('Template Management', () => {
    it('should set templates', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const templates = [
        { id: 'tpl-1', name: 'Template 1' },
        { id: 'tpl-2', name: 'Template 2' },
      ]

      act(() => {
        useAppStore.getState().setTemplates(templates)
      })

      expect(useAppStore.getState().templates).toEqual(templates)
    })

    it('should add template', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplates([{ id: 'tpl-1', name: 'Template 1' }])
        useAppStore.getState().addTemplate({ id: 'tpl-2', name: 'Template 2' })
      })

      const state = useAppStore.getState()
      expect(state.templates).toHaveLength(2)
      // New template should be first
      expect(state.templates[0].id).toBe('tpl-2')
    })

    it('should remove template', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplates([
          { id: 'tpl-1', name: 'Template 1' },
          { id: 'tpl-2', name: 'Template 2' },
        ])
        useAppStore.getState().removeTemplate('tpl-1')
      })

      const state = useAppStore.getState()
      expect(state.templates).toHaveLength(1)
      expect(state.templates[0].id).toBe('tpl-2')
    })

    it('should clear lastUsed templateId when removing that template', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplates([{ id: 'tpl-1', name: 'Template 1' }])
        useAppStore.getState().setLastUsed({ templateId: 'tpl-1', connectionId: null })
        useAppStore.getState().removeTemplate('tpl-1')
      })

      const state = useAppStore.getState()
      expect(state.lastUsed.templateId).toBeNull()
    })

    it('should update template with updater function', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplates([
          { id: 'tpl-1', name: 'Original', status: 'pending' },
        ])
        useAppStore.getState().updateTemplate('tpl-1', (tpl) => ({
          ...tpl,
          status: 'approved',
        }))
      })

      const state = useAppStore.getState()
      expect(state.templates[0].status).toBe('approved')
    })

    it('should set templateId', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setTemplateId('tpl-1')
      })

      expect(useAppStore.getState().templateId).toBe('tpl-1')
    })

    it('should set verifyArtifacts', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const artifacts = {
        pdf_url: '/uploads/doc.pdf',
        png_url: '/uploads/preview.png',
      }

      act(() => {
        useAppStore.getState().setVerifyArtifacts(artifacts)
      })

      expect(useAppStore.getState().verifyArtifacts).toEqual(artifacts)
    })
  })

  describe('Discovery Management', () => {
    it('should set discovery results', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const results = {
        'tpl-1': {
          batches: [{ id: 'batch-1', rows: 100 }],
        },
      }

      act(() => {
        useAppStore.getState().setDiscoveryResults(results, { source: 'api' })
      })

      const state = useAppStore.getState()
      expect(state.discoveryResults).toEqual(results)
      expect(state.discoveryMeta).toEqual({ source: 'api' })
    })

    it('should persist discovery to localStorage', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const results = { 'tpl-1': { batches: [] } }

      act(() => {
        useAppStore.getState().setDiscoveryResults(results, null)
      })

      expect(localStorageMock.setItem).toHaveBeenCalled()
    })

    it('should update discovery batch selection', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setDiscoveryResults(
          {
            'tpl-1': {
              batches: [
                { id: 'batch-1', selected: false },
                { id: 'batch-2', selected: false },
              ],
            },
          },
          null
        )
        useAppStore.getState().updateDiscoveryBatchSelection('tpl-1', 0, true)
      })

      const state = useAppStore.getState()
      expect(state.discoveryResults['tpl-1'].batches[0].selected).toBe(true)
      expect(state.discoveryResults['tpl-1'].batches[1].selected).toBe(false)
    })

    it('should clear discovery results', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setDiscoveryResults({ 'tpl-1': { batches: [] } }, null)
        useAppStore.getState().clearDiscoveryResults()
      })

      const state = useAppStore.getState()
      expect(state.discoveryResults).toEqual({})
      expect(state.discoveryMeta).toBeNull()
      expect(localStorageMock.removeItem).toHaveBeenCalled()
    })

    it('should set discovery finding flag', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setDiscoveryFinding(true)
      })

      expect(useAppStore.getState().discoveryFinding).toBe(true)
    })
  })

  describe('Cache Management', () => {
    it('should bump cache key', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const originalKey = useAppStore.getState().cacheKey

      act(() => {
        useAppStore.getState().bumpCache()
      })

      expect(useAppStore.getState().cacheKey).toBeGreaterThan(originalKey)
    })

    it('should set cache key explicitly', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setCacheKey(12345)
      })

      expect(useAppStore.getState().cacheKey).toBe(12345)
    })

    it('should set HTML URLs', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setHtmlUrls({
          final: '/uploads/final.html',
          template: '/uploads/template.html',
        })
      })

      const state = useAppStore.getState()
      expect(state.htmlUrls.final).toBe('/uploads/final.html')
      expect(state.htmlUrls.template).toBe('/uploads/template.html')
    })

    it('should support updater function for HTML URLs', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setHtmlUrls({ final: '/old.html' })
        useAppStore.getState().setHtmlUrls((prev) => ({
          ...prev,
          final: '/new.html',
        }))
      })

      expect(useAppStore.getState().htmlUrls.final).toBe('/new.html')
    })
  })

  describe('Reset Setup', () => {
    it('should reset setup state', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      // Modify state
      act(() => {
        useAppStore.getState().setSetupNav('generate')
        useAppStore.getState().setSetupStep('approve')
        useAppStore.getState().setTemplateId('tpl-1')
        useAppStore.getState().setConnection({ status: 'connected' })
      })

      // Reset
      act(() => {
        useAppStore.getState().resetSetup()
      })

      const state = useAppStore.getState()
      expect(state.setupNav).toBe('connect')
      expect(state.setupStep).toBe('connect')
      expect(state.templateId).toBeNull()
      expect(state.connection.status).toBe('disconnected')
    })
  })

  describe('Last Used', () => {
    it('should set last used', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSavedConnections([{ id: 'conn-1', name: 'Conn 1' }])
        useAppStore.getState().setLastUsed({
          connectionId: 'conn-1',
          templateId: 'tpl-1',
        })
      })

      const state = useAppStore.getState()
      expect(state.lastUsed.connectionId).toBe('conn-1')
      expect(state.lastUsed.templateId).toBe('tpl-1')
      expect(state.activeConnectionId).toBe('conn-1')
    })

    it('should update activeConnection when setting lastUsed', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        useAppStore.getState().setSavedConnections([
          { id: 'conn-1', name: 'Connection 1' },
        ])
        useAppStore.getState().setLastUsed({ connectionId: 'conn-1' })
      })

      const state = useAppStore.getState()
      expect(state.activeConnection?.id).toBe('conn-1')
    })
  })

  describe('Downloads', () => {
    it('should add download', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      const download = { url: '/uploads/doc.pdf', name: 'doc.pdf' }

      act(() => {
        useAppStore.getState().addDownload(download)
      })

      const state = useAppStore.getState()
      expect(state.downloads).toHaveLength(1)
      expect(state.downloads[0]).toEqual(download)
    })

    it('should limit downloads to 20', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      act(() => {
        // Add 25 downloads
        for (let i = 0; i < 25; i++) {
          useAppStore.getState().addDownload({ url: `/doc-${i}.pdf` })
        }
      })

      const state = useAppStore.getState()
      expect(state.downloads).toHaveLength(20)
      // Most recent should be first
      expect(state.downloads[0].url).toBe('/doc-24.pdf')
    })
  })

  describe('Hydration', () => {
    it('should set hydrated flag', async () => {
      const { useAppStore } = await import('../useAppStore.js')

      expect(useAppStore.getState().hydrated).toBe(false)

      act(() => {
        useAppStore.getState().setHydrated(true)
      })

      expect(useAppStore.getState().hydrated).toBe(true)
    })
  })
})
