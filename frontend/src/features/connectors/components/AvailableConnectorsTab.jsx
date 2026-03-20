/**
 * Available connectors tab showing connector categories.
 */
import React from 'react'
import {
  Box,
  Typography,
  Grid,
  CardContent,
  CardActions,
  alpha,
} from '@mui/material'
import {
  Storage as DatabaseIcon,
  Cloud as CloudIcon,
} from '@mui/icons-material'
import { secondary } from '@/app/theme'

const CONNECTOR_CATEGORIES = {
  database: {
    label: 'Databases',
    icon: DatabaseIcon,
    connectors: [
      { id: 'postgresql', name: 'PostgreSQL', color: secondary.slate[600] },
      { id: 'mysql', name: 'MySQL', color: secondary.cyan[700] },
      { id: 'mongodb', name: 'MongoDB', color: secondary.emerald[500] },
      { id: 'sqlserver', name: 'SQL Server', color: secondary.rose[600] },
      { id: 'bigquery', name: 'BigQuery', color: secondary.cyan[500] },
      { id: 'snowflake', name: 'Snowflake', color: secondary.cyan[400] },
    ],
  },
  cloud_storage: {
    label: 'Cloud Storage',
    icon: CloudIcon,
    connectors: [
      { id: 'google_drive', name: 'Google Drive', color: secondary.cyan[500] },
      { id: 'dropbox', name: 'Dropbox', color: secondary.violet[500] },
      { id: 's3', name: 'Amazon S3', color: secondary.fuchsia[500] },
      { id: 'azure_blob', name: 'Azure Blob', color: secondary.teal[500] },
      { id: 'onedrive', name: 'OneDrive', color: secondary.slate[500] },
    ],
  },
}

export default function AvailableConnectorsTab({
  handleOpenConnect,
  ConnectorCard,
  ConnectorIcon,
  ActionButton,
}) {
  const categoryKeys = Object.keys(CONNECTOR_CATEGORIES)

  return (
    <Box>
      {categoryKeys.map((catKey) => {
        const category = CONNECTOR_CATEGORIES[catKey]
        const CategoryIcon = category.icon
        return (
          <Box key={catKey} sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CategoryIcon color="inherit" sx={{ color: 'text.secondary' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {category.label}
              </Typography>
            </Box>
            <Grid container spacing={2}>
              {category.connectors.map((connector) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={connector.id}>
                  <ConnectorCard variant="outlined">
                    <CardContent>
                      <ConnectorIcon
                        sx={{ bgcolor: alpha(connector.color, 0.1) }}
                      >
                        {catKey === 'database' ? (
                          <DatabaseIcon sx={{ color: connector.color }} />
                        ) : (
                          <CloudIcon sx={{ color: connector.color }} />
                        )}
                      </ConnectorIcon>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {connector.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {catKey === 'database' ? 'Database' : 'Cloud Storage'}
                      </Typography>
                    </CardContent>
                    <CardActions sx={{ mt: 'auto', p: 2, pt: 0 }}>
                      <ActionButton
                        fullWidth
                        variant="outlined"
                        size="small"
                        onClick={() => handleOpenConnect(connector)}
                        data-testid="connector-connect-button"
                      >
                        Connect
                      </ActionButton>
                    </CardActions>
                  </ConnectorCard>
                </Grid>
              ))}
            </Grid>
          </Box>
        )
      })}
    </Box>
  )
}
