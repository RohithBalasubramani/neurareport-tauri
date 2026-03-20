import {
  Typography,
  Stack,
  Grid,
  Avatar,
  alpha,
  useTheme,
} from '@mui/material'
import TableChartIcon from '@mui/icons-material/TableChart'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import TableAccordion from './TableAccordion'
import { EntitiesPanel, InvoicesPanel, ContractsPanel } from './DataPanels'

export default function DataTab({ analysisResult }) {
  const theme = useTheme()

  return (
    <Grid container spacing={3}>
      {/* Tables */}
      <Grid size={12}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <TableChartIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Extracted Tables ({analysisResult.tables?.length || 0})
            </Typography>
          </Stack>
          {analysisResult.tables?.map((table) => (
            <TableAccordion key={table.id} table={table} theme={theme} />
          ))}
        </GlassCard>
      </Grid>

      {/* Entities */}
      <Grid size={{ xs: 12, md: 6 }}>
        <EntitiesPanel entities={analysisResult.entities} theme={theme} />
      </Grid>

      {/* Invoices & Contracts */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Stack spacing={3}>
          {analysisResult.invoices?.length > 0 && (
            <InvoicesPanel invoices={analysisResult.invoices} theme={theme} />
          )}
          {analysisResult.contracts?.length > 0 && (
            <ContractsPanel contracts={analysisResult.contracts} theme={theme} />
          )}
        </Stack>
      </Grid>
    </Grid>
  )
}
