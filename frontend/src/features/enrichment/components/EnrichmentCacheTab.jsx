/**
 * Cache admin tab for enrichment configuration.
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Grid,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

export default function EnrichmentCacheTab({
  cacheStats,
  fetchCacheStats,
  allSources,
  loading,
  setClearCacheConfirm,
}) {
  return (
    <Grid container spacing={3}>
      {/* Cache Stats */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Cache Statistics</Typography>
            <Tooltip title="Refresh cache stats">
              <IconButton onClick={fetchCacheStats} size="small" aria-label="Refresh cache stats">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {cacheStats ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Total Entries</Typography>
                <Typography variant="h4">{cacheStats.total_entries || 0}</Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Hit Rate</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(cacheStats.hit_rate || 0) * 100}
                    sx={{ flex: 1, height: 10, borderRadius: 1 }}
                  />
                  <Typography variant="body1">
                    {((cacheStats.hit_rate || 0) * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Cache Hits / Misses</Typography>
                <Typography variant="body1">
                  {cacheStats.hits || 0} hits / {cacheStats.misses || 0} misses
                </Typography>
              </Box>
              {cacheStats.size_bytes && (
                <Box>
                  <Typography variant="body2" color="text.secondary">Cache Size</Typography>
                  <Typography variant="body1">
                    {(cacheStats.size_bytes / 1024).toFixed(2)} KB
                  </Typography>
                </Box>
              )}
            </Box>
          ) : (
            <Typography color="text.secondary">No cache stats available</Typography>
          )}
        </Paper>
      </Grid>

      {/* Cache Actions */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Cache Management</Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            Clearing the cache will remove all cached enrichment results.
            New enrichment requests will fetch fresh data from sources.
          </Alert>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={loading ? <CircularProgress size={20} /> : <DeleteIcon />}
              onClick={() => setClearCacheConfirm({ open: true, sourceId: null, sourceName: 'all sources' })}
              disabled={loading}
              sx={{ color: 'text.secondary', borderColor: 'divider' }}
            >
              Clear All Cache
            </Button>

            <Divider sx={{ my: 1 }} />

            <Typography variant="subtitle2" color="text.secondary">
              Clear cache for specific source:
            </Typography>

            {allSources.map((source) => (
              <Box key={source.id} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2">{source.name}</Typography>
                <Button
                  size="small"
                  onClick={() => setClearCacheConfirm({ open: true, sourceId: source.id, sourceName: source.name })}
                  disabled={loading}
                >
                  Clear
                </Button>
              </Box>
            ))}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}
