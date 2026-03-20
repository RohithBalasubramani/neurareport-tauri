/**
 * Column definitions for HistoryPage DataTable
 */
import React from 'react'
import {
  Box,
  Typography,
  Stack,
  Tooltip,
} from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import VisibilityIcon from '@mui/icons-material/Visibility'
import ArticleIcon from '@mui/icons-material/Article'
import TableChartIcon from '@mui/icons-material/TableChart'
import { getStatusConfig, getKindConfig } from './historyHelpers'
import { KindIconContainer, StatusChip, ArtifactButton } from './HistoryStyledComponents'

export function getHistoryColumns(theme, handleDownloadClick) {
  return [
    {
      field: 'templateName',
      headerName: 'Design',
      renderCell: (value, row) => {
        const kind = row.templateKind || 'pdf'
        const cfg = getKindConfig(theme, kind)
        const Icon = cfg.icon
        return (
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <KindIconContainer>
              <Icon sx={{ fontSize: 18, color: 'text.secondary' }} />
            </KindIconContainer>
            <Box>
              <Typography sx={{ fontSize: '14px', fontWeight: 500, color: 'text.primary' }}>
                {value || 'Unknown'}
              </Typography>
              <Typography sx={{ fontSize: '12px', color: 'text.secondary' }}>
                {kind.toUpperCase()}
              </Typography>
            </Box>
          </Stack>
        )
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (value) => {
        const cfg = getStatusConfig(theme, value)
        const Icon = cfg.icon
        return (
          <StatusChip
            icon={<Icon sx={{ fontSize: 14 }} />}
            label={cfg.label}
            size="small"
            statusColor={cfg.color}
            statusBg={cfg.bgColor}
          />
        )
      },
    },
    {
      field: 'createdAt',
      headerName: 'Started',
      width: 160,
      renderCell: (value) => (
        <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
          {value ? new Date(value).toLocaleString() : '-'}
        </Typography>
      ),
    },
    {
      field: 'completedAt',
      headerName: 'Completed',
      width: 160,
      renderCell: (value) => (
        <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
          {value ? new Date(value).toLocaleString() : '-'}
        </Typography>
      ),
    },
    {
      field: 'artifacts',
      headerName: 'Downloads',
      width: 150,
      renderCell: (value, row) => {
        const artifacts = value || {}
        const hasAny = artifacts.pdf_url || artifacts.html_url || artifacts.docx_url || artifacts.xlsx_url
        if (!hasAny) {
          return (
            <Typography sx={{ fontSize: '0.75rem', color: 'text.disabled' }}>
              {(row.status === 'completed' || row.status === 'succeeded') ? 'No files' : '-'}
            </Typography>
          )
        }
        return (
          <Stack direction="row" spacing={0.5}>
            {artifacts.pdf_url && (
              <Tooltip title="Download PDF">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'pdf')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="Download PDF"
                >
                  <PictureAsPdfIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
            {artifacts.html_url && (
              <Tooltip title="View HTML">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'html')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="View HTML"
                >
                  <VisibilityIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
            {artifacts.docx_url && (
              <Tooltip title="Download DOCX">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'docx')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="Download DOCX"
                >
                  <ArticleIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
            {artifacts.xlsx_url && (
              <Tooltip title="Download XLSX">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'xlsx')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="Download XLSX"
                >
                  <TableChartIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
          </Stack>
        )
      },
    },
  ]
}
