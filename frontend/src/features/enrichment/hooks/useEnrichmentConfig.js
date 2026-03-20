/**
 * Custom hook for enrichment configuration state and actions.
 */
import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import useEnrichmentStore from '@/stores/enrichmentStore';
import useSharedData from '@/hooks/useSharedData';
import useCrossPageActions from '@/hooks/useCrossPageActions';
import useIncomingTransfer from '@/hooks/useIncomingTransfer';
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance';
import { OutputType, TransferAction, FeatureKey } from '@/utils/crossPageTypes';

// Fallback sources in case API is unavailable
const FALLBACK_SOURCES = [
  { id: 'company', name: 'Company Information', description: 'Enrich with company details (industry, size, revenue)' },
  { id: 'address', name: 'Address Standardization', description: 'Standardize and validate addresses' },
  { id: 'exchange', name: 'Currency Exchange', description: 'Convert currencies to target currency' },
];

const SOURCE_TYPES = [
  { value: 'company_info', label: 'Company Information' },
  { value: 'address', label: 'Address Standardization' },
  { value: 'exchange_rate', label: 'Currency Exchange' },
];

export { SOURCE_TYPES };

export function useEnrichmentConfig() {
  const {
    sources,
    customSources,
    cacheStats,
    previewResult,
    enrichmentResult,
    loading,
    error,
    fetchSources,
    createSource,
    deleteSource,
    fetchCacheStats,
    clearCache,
    previewEnrichment,
    enrichData,
    reset,
  } = useEnrichmentStore();
  const { execute } = useInteraction();
  const { registerOutput } = useCrossPageActions(FeatureKey.ENRICHMENT);

  const { connections, activeConnectionId } = useSharedData();
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId || '');

  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const activeTab = tabParam === 'cache' ? 1 : 0;

  const [initialLoading, setInitialLoading] = useState(true);
  const [inputData, setInputData] = useState('');
  const [selectedSources, setSelectedSources] = useState([]);
  const [parsedData, setParsedData] = useState(null);

  // Create Source Dialog
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSourceName, setNewSourceName] = useState('');
  const [newSourceType, setNewSourceType] = useState('company_info');
  const [newSourceDescription, setNewSourceDescription] = useState('');
  const [newSourceCacheTtl, setNewSourceCacheTtl] = useState(24);

  // Confirmation dialogs
  const [deleteSourceConfirm, setDeleteSourceConfirm] = useState({ open: false, sourceId: null, sourceName: '' });
  const [clearCacheConfirm, setClearCacheConfirm] = useState({ open: false, sourceId: null, sourceName: '' });

  // Cross-page: accept table/dataset for enrichment
  useIncomingTransfer(FeatureKey.ENRICHMENT, {
    [TransferAction.ENRICH]: async (payload) => {
      const rows = payload.data?.rows || payload.data;
      if (Array.isArray(rows)) {
        setParsedData(rows);
        setInputData(JSON.stringify(rows, null, 2));
      }
    },
  });

  const handleTabChange = useCallback((e, newValue) => {
    setSearchParams(newValue === 1 ? { tab: 'cache' } : {}, { replace: true });
  }, [setSearchParams]);

  useEffect(() => {
    const init = async () => {
      setInitialLoading(true);
      await Promise.all([fetchSources(), fetchCacheStats()]);
      setInitialLoading(false);
    };
    init();
    return () => reset();
  }, [fetchSources, fetchCacheStats, reset]);

  const handleParseData = useCallback(() => {
    try {
      const data = JSON.parse(inputData);
      if (Array.isArray(data)) {
        setParsedData(data);
      } else {
        setParsedData([data]);
      }
    } catch (err) {
      const lines = inputData.trim().split('\n');
      if (lines.length > 1) {
        const headers = lines[0].split(',').map(h => h.trim());
        const data = lines.slice(1).map(line => {
          const values = line.split(',');
          const obj = {};
          headers.forEach((h, i) => {
            obj[h] = values[i]?.trim() || '';
          });
          return obj;
        });
        setParsedData(data);
      }
    }
  }, [inputData]);

  const handlePreview = async () => {
    if (!parsedData || selectedSources.length === 0) return;
    await execute({
      type: InteractionType.ANALYZE,
      label: 'Preview enrichment',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        sourceIds: selectedSources,
        action: 'preview_enrichment',
      },
      action: async () => {
        const result = await previewEnrichment(parsedData, selectedSources, 3);
        if (!result) {
          throw new Error('Preview enrichment failed');
        }
        return result;
      },
    });
  };

  const handleEnrich = async () => {
    if (!parsedData || selectedSources.length === 0) return;
    await execute({
      type: InteractionType.GENERATE,
      label: 'Enrich data',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        sourceIds: selectedSources,
        action: 'enrich_data',
      },
      action: async () => {
        const result = await enrichData(parsedData, selectedSources);
        if (!result) {
          throw new Error('Enrichment failed');
        }
        const rows = result.enriched_data || [];
        const columns = rows.length > 0 ? Object.keys(rows[0]).map((k) => ({ name: k })) : [];
        registerOutput({
          type: OutputType.TABLE,
          title: `Enriched Data (${rows.length} rows)`,
          summary: `Enriched with ${selectedSources.length} source(s)`,
          data: { columns, rows },
          format: 'table',
        });
        return result;
      },
    });
  };

  const toggleSource = (sourceId) => {
    setSelectedSources(prev =>
      prev.includes(sourceId)
        ? prev.filter(s => s !== sourceId)
        : [...prev, sourceId]
    );
  };

  const handleCreateSource = async () => {
    if (!newSourceName.trim()) return;
    await execute({
      type: InteractionType.CREATE,
      label: 'Create enrichment source',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        sourceType: newSourceType,
        action: 'create_enrichment_source',
      },
      action: async () => {
        const result = await createSource({
          name: newSourceName,
          type: newSourceType,
          description: newSourceDescription,
          config: {},
          cacheTtlHours: newSourceCacheTtl,
        });
        if (result) {
          setCreateDialogOpen(false);
          setNewSourceName('');
          setNewSourceType('company_info');
          setNewSourceDescription('');
          setNewSourceCacheTtl(24);
        }
        if (!result) {
          throw new Error('Create source failed');
        }
        return result;
      },
    });
  };

  const handleClearCache = async () => {
    await execute({
      type: InteractionType.DELETE,
      label: 'Clear enrichment cache',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        action: 'clear_enrichment_cache',
      },
      action: async () => {
        const result = await clearCache();
        if (result == null) {
          throw new Error('Clear cache failed');
        }
        return result;
      },
    });
  };

  const handleDeleteSourceConfirm = async () => {
    const sourceId = deleteSourceConfirm.sourceId;
    const sourceName = deleteSourceConfirm.sourceName;
    setDeleteSourceConfirm({ open: false, sourceId: null, sourceName: '' });
    if (!sourceId) return;
    await execute({
      type: InteractionType.DELETE,
      label: 'Delete enrichment source',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        sourceId,
        sourceName,
        action: 'delete_enrichment_source',
      },
      action: async () => {
        const result = await deleteSource(sourceId);
        if (!result) {
          throw new Error('Delete source failed');
        }
        return result;
      },
    });
  };

  const handleClearCacheConfirm = async () => {
    const sourceId = clearCacheConfirm.sourceId || null;
    const sourceName = clearCacheConfirm.sourceName;
    setClearCacheConfirm({ open: false, sourceId: null, sourceName: '' });
    await execute({
      type: InteractionType.DELETE,
      label: 'Clear enrichment cache',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        sourceId,
        sourceName,
        action: 'clear_enrichment_cache',
      },
      action: async () => {
        const result = await clearCache(sourceId);
        if (result == null) {
          throw new Error('Clear cache failed');
        }
        return result;
      },
    });
  };

  const handleImport = useCallback((output) => {
    const rows = output.data?.rows || output.data;
    if (Array.isArray(rows)) {
      setParsedData(rows);
      setInputData(JSON.stringify(rows, null, 2));
    }
  }, []);

  // Use API sources if available, fallback to static list
  const usingFallbackSources = sources.length === 0 && !initialLoading;
  const availableSources = sources.length > 0 ? sources : FALLBACK_SOURCES;
  const allSources = [...availableSources, ...customSources];

  return {
    // Store state
    cacheStats,
    previewResult,
    enrichmentResult,
    loading,
    error,
    reset,
    fetchCacheStats,

    // Local state
    selectedConnectionId,
    setSelectedConnectionId,
    activeTab,
    handleTabChange,
    initialLoading,
    inputData,
    setInputData,
    selectedSources,
    parsedData,
    createDialogOpen,
    setCreateDialogOpen,
    newSourceName,
    setNewSourceName,
    newSourceType,
    setNewSourceType,
    newSourceDescription,
    setNewSourceDescription,
    newSourceCacheTtl,
    setNewSourceCacheTtl,
    deleteSourceConfirm,
    setDeleteSourceConfirm,
    clearCacheConfirm,
    setClearCacheConfirm,

    // Derived
    usingFallbackSources,
    allSources,
    customSources,

    // Handlers
    handleParseData,
    handlePreview,
    handleEnrich,
    toggleSource,
    handleCreateSource,
    handleDeleteSourceConfirm,
    handleClearCacheConfirm,
    handleImport,
  };
}
