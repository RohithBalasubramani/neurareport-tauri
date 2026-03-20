/**
 * Summary History Panel — collapsible list of recent summaries.
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Collapse,
} from '@mui/material';

export default function SummaryHistoryPanel({
  showHistory,
  history,
  onLoadFromHistory,
  onOpenClearHistory,
}) {
  return (
    <Collapse in={showHistory}>
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Recent Summaries</Typography>
          <Button size="small" onClick={onOpenClearHistory} sx={{ color: 'text.secondary' }}>
            Clear All
          </Button>
        </Box>
        <Grid container spacing={2}>
          {history.map((item) => (
            <Grid size={{ xs: 12, md: 6 }} key={item.id}>
              <Card variant="outlined" sx={{ cursor: 'pointer' }} onClick={() => onLoadFromHistory(item)}>
                <CardContent sx={{ py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(item.createdAt).toLocaleString()} - {item.tone}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }} noWrap>
                    {item.summary?.substring(0, 150)}...
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Collapse>
  );
}
