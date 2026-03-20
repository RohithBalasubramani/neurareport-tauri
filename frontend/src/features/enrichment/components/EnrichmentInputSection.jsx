/**
 * Input data section for enrichment configuration.
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
} from '@mui/material';
import ConnectionSelector from '@/components/common/ConnectionSelector';
import ImportFromMenu from '@/components/common/ImportFromMenu';
import { FeatureKey } from '@/utils/crossPageTypes';

export default function EnrichmentInputSection({
  selectedConnectionId,
  setSelectedConnectionId,
  inputData,
  setInputData,
  parsedData,
  handleParseData,
  handleImport,
}) {
  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="h6">
          Input Data
        </Typography>
        <ImportFromMenu
          currentFeature={FeatureKey.ENRICHMENT}
          onImport={handleImport}
          size="small"
        />
      </Box>
      <ConnectionSelector
        value={selectedConnectionId}
        onChange={setSelectedConnectionId}
        label="Data Source (Optional)"
        size="small"
        showStatus
        sx={{ mb: 2 }}
      />
      {selectedConnectionId && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Data will be pulled from the selected database connection
        </Alert>
      )}
      <TextField
        fullWidth
        multiline
        rows={10}
        placeholder={'Paste JSON array or CSV data:\n\n[\n  {"name": "Acme Corp", "address": "123 Main St"},\n  {"name": "Tech Inc", "address": "456 Oak Ave"}\n]\n\nOr CSV:\nname,address\nAcme Corp,123 Main St\nTech Inc,456 Oak Ave'}
        value={inputData}
        onChange={(e) => setInputData(e.target.value)}
        sx={{ mb: 2, fontFamily: 'monospace' }}
      />
      <Button
        variant="outlined"
        onClick={handleParseData}
        disabled={!inputData.trim()}
      >
        Parse Data
      </Button>

      {parsedData && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Parsed {parsedData.length} records with columns: {Object.keys(parsedData[0] || {}).join(', ')}
        </Alert>
      )}
    </Paper>
  );
}
