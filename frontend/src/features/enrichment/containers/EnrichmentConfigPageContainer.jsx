/**
 * Data Enrichment Configuration Page
 */
import React from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  AutoFixHigh as EnrichIcon,
  Cached as CacheIcon,
} from '@mui/icons-material';
import AiUsageNotice from '@/components/ai/AiUsageNotice';
import ConfirmModal from '@/components/modal/ConfirmModal';
import { FeatureKey } from '@/utils/crossPageTypes';
import { useEnrichmentConfig } from '../hooks/useEnrichmentConfig';
import EnrichmentInputSection from '../components/EnrichmentInputSection';
import EnrichmentSourcesSection from '../components/EnrichmentSourcesSection';
import EnrichmentResultsSection from '../components/EnrichmentResultsSection';
import EnrichmentCacheTab from '../components/EnrichmentCacheTab';
import CreateSourceDialog from '../components/CreateSourceDialog';

export default function EnrichmentConfigPage() {
  const config = useEnrichmentConfig();

  // Show loading during initial fetch
  if (config.initialLoading) {
    return (
      <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <EnrichIcon />
          <Typography variant="h5">Data Enrichment</Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <CircularProgress />
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <EnrichIcon /> Data Enrichment
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Enrich your data with external information sources using AI
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={() => config.setCreateDialogOpen(true)}
        >
          Add Custom Source
        </Button>
      </Box>

      {config.error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => config.reset()}>
          {config.error}
        </Alert>
      )}

      <AiUsageNotice
        title="AI enrichment"
        description="Enrichment adds fields to a new output based on the sources you select. Preview before running."
        chips={[
          { label: 'Source: Input data', color: 'info', variant: 'outlined' },
          { label: 'Confidence: Review results', color: 'warning', variant: 'outlined' },
          { label: 'Original data unchanged', color: 'success', variant: 'outlined' },
        ]}
        dense
        sx={{ mb: 2 }}
      />

      {config.usingFallbackSources && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Using default enrichment sources. Create custom sources below to configure specific enrichment behavior.
        </Alert>
      )}

      <Tabs value={config.activeTab} onChange={config.handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Enrich Data" />
        <Tab label="Cache Admin" icon={<CacheIcon />} iconPosition="start" />
      </Tabs>

      {config.activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <EnrichmentInputSection
              selectedConnectionId={config.selectedConnectionId}
              setSelectedConnectionId={config.setSelectedConnectionId}
              inputData={config.inputData}
              setInputData={config.setInputData}
              parsedData={config.parsedData}
              handleParseData={config.handleParseData}
              handleImport={config.handleImport}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <EnrichmentSourcesSection
              allSources={config.allSources}
              customSources={config.customSources}
              selectedSources={config.selectedSources}
              toggleSource={config.toggleSource}
              setDeleteSourceConfirm={config.setDeleteSourceConfirm}
              parsedData={config.parsedData}
              loading={config.loading}
              handlePreview={config.handlePreview}
              handleEnrich={config.handleEnrich}
            />
          </Grid>
          {(config.previewResult || config.enrichmentResult) && (
            <Grid size={12}>
              <EnrichmentResultsSection
                previewResult={config.previewResult}
                enrichmentResult={config.enrichmentResult}
              />
            </Grid>
          )}
        </Grid>
      )}

      {config.activeTab === 1 && (
        <EnrichmentCacheTab
          cacheStats={config.cacheStats}
          fetchCacheStats={config.fetchCacheStats}
          allSources={config.allSources}
          loading={config.loading}
          setClearCacheConfirm={config.setClearCacheConfirm}
        />
      )}

      <CreateSourceDialog
        open={config.createDialogOpen}
        onClose={() => config.setCreateDialogOpen(false)}
        newSourceName={config.newSourceName}
        setNewSourceName={config.setNewSourceName}
        newSourceType={config.newSourceType}
        setNewSourceType={config.setNewSourceType}
        newSourceDescription={config.newSourceDescription}
        setNewSourceDescription={config.setNewSourceDescription}
        newSourceCacheTtl={config.newSourceCacheTtl}
        setNewSourceCacheTtl={config.setNewSourceCacheTtl}
        onCreateSource={config.handleCreateSource}
        loading={config.loading}
      />

      <ConfirmModal
        open={config.deleteSourceConfirm.open}
        onClose={() => config.setDeleteSourceConfirm({ open: false, sourceId: null, sourceName: '' })}
        onConfirm={config.handleDeleteSourceConfirm}
        title="Delete Source"
        message={`Are you sure you want to delete "${config.deleteSourceConfirm.sourceName}"? This will remove the source configuration and all associated cache data.`}
        confirmLabel="Delete"
        severity="error"
      />

      <ConfirmModal
        open={config.clearCacheConfirm.open}
        onClose={() => config.setClearCacheConfirm({ open: false, sourceId: null, sourceName: '' })}
        onConfirm={config.handleClearCacheConfirm}
        title="Clear Cache"
        message={`Are you sure you want to clear cache for ${config.clearCacheConfirm.sourceName}? New enrichment requests will fetch fresh data from the source.`}
        confirmLabel="Clear Cache"
        severity="warning"
      />
    </Box>
  );
}
