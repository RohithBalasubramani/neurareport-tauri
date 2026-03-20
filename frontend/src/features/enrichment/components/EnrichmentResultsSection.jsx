/**
 * Results table for enrichment preview/results.
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import SendToMenu from '@/components/common/SendToMenu';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';

export default function EnrichmentResultsSection({ previewResult, enrichmentResult }) {
  if (!previewResult && !enrichmentResult) return null;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="h6">
          {enrichmentResult ? 'Enrichment Results' : 'Preview Results'}
        </Typography>
        {enrichmentResult && (
          <SendToMenu
            outputType={OutputType.TABLE}
            payload={{
              title: `Enriched Data (${enrichmentResult.enriched_data?.length || 0} rows)`,
              content: JSON.stringify(enrichmentResult.enriched_data),
              data: {
                columns: Object.keys(enrichmentResult.enriched_data?.[0] || {}).map((k) => ({ name: k })),
                rows: enrichmentResult.enriched_data || [],
              },
            }}
            sourceFeature={FeatureKey.ENRICHMENT}
          />
        )}
      </Box>
      <TableContainer sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {Object.keys((enrichmentResult?.enriched_data || previewResult?.preview)?.[0] || {}).map((col) => (
                <TableCell key={col}>{col}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(enrichmentResult?.enriched_data || previewResult?.preview || []).map((row, idx) => (
              <TableRow key={idx}>
                {Object.values(row).map((val, cidx) => (
                  <TableCell key={cidx}>
                    {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
