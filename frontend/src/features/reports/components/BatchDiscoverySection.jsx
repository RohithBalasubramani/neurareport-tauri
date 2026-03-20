import {
  Box,
  Typography,
  Stack,
  Collapse,
  Checkbox,
  List,
  ListItemText,
} from '@mui/material'
import FilterListIcon from '@mui/icons-material/FilterList'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import { GlassCard } from '@/styles'
import {
  SecondaryButton,
  TextButton,
  DiscoveryChip,
  BatchListContainer,
  BatchListItem,
  StyledLinearProgress,
  AdvancedToggle,
} from './ReportsStyledComponents'

export default function BatchDiscoverySection({
  batchDiscoveryOpen,
  onToggleOpen,
  discovering,
  discovery,
  selectedBatches,
  selectedTemplate,
  activeConnection,
  onDiscover,
  onToggleBatch,
  onSelectAll,
  onClear,
}) {
  return (
    <Box>
      <AdvancedToggle onClick={onToggleOpen}>
        <Stack direction="row" spacing={1} alignItems="center">
          <FilterListIcon sx={{ fontSize: 16 }} />
          <Typography variant="subtitle2" fontWeight={500}>
            Advanced: Find Data Batches
          </Typography>
        </Stack>
        {batchDiscoveryOpen ? (
          <ExpandLessIcon sx={{ fontSize: 20 }} />
        ) : (
          <ExpandMoreIcon sx={{ fontSize: 20 }} />
        )}
      </AdvancedToggle>

      <Collapse in={batchDiscoveryOpen}>
        <GlassCard sx={{ mt: 1 }}>
          <Stack spacing={2}>
            <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Discover available data batches for the selected design and date range.
              </Typography>
              <SecondaryButton
                variant="outlined"
                size="small"
                onClick={onDiscover}
                disabled={discovering || !selectedTemplate || !activeConnection}
              >
                {discovering ? 'Searching...' : 'Find Batches'}
              </SecondaryButton>
            </Stack>

            {discovering && <StyledLinearProgress />}

            {!discovering && discovery && (
              <Stack spacing={2}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <DiscoveryChip label={`${discovery.batches_count || discovery.batches?.length || 0} batches`} />
                  <DiscoveryChip label={`${discovery.rows_total || 0} rows`} />
                </Stack>
                <Stack direction="row" spacing={1}>
                  <TextButton size="small" onClick={onSelectAll}>Select all</TextButton>
                  <TextButton size="small" onClick={onClear}>Clear</TextButton>
                </Stack>
                <BatchListContainer>
                  <List dense disablePadding>
                    {(discovery.batches || []).map((batch) => (
                      <BatchListItem
                        key={batch.id}
                        disableGutters
                        onClick={() => onToggleBatch(batch.id)}
                        selected={selectedBatches.includes(batch.id)}
                      >
                        <Checkbox
                          checked={selectedBatches.includes(batch.id)}
                          sx={{ p: 0.5, mr: 1 }}
                        />
                        <ListItemText
                          primary={`${batch.id}`}
                          secondary={`${batch.rows || 0} rows`}
                          primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                          secondaryTypographyProps={{ variant: 'caption' }}
                        />
                      </BatchListItem>
                    ))}
                  </List>
                </BatchListContainer>
              </Stack>
            )}
          </Stack>
        </GlassCard>
      </Collapse>
    </Box>
  )
}
