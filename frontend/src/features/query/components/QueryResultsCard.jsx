/**
 * Query results display card with DataTable
 */
import { Typography, Stack, useTheme } from '@mui/material'
import { GlassCard } from '@/styles'
import DataTable from '@/components/data-table/DataTable'
import SendToMenu from '@/components/common/SendToMenu'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'

export default function QueryResultsCard({
  results,
  columns,
  tableColumns,
  totalCount,
  executionTimeMs,
  currentQuestion,
}) {
  const theme = useTheme()

  if (!results) return null

  return (
    <GlassCard>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary }}>
            Results
          </Typography>
          <SendToMenu
            outputType={OutputType.TABLE}
            payload={{
              title: `Query: ${currentQuestion.substring(0, 60)}`,
              content: JSON.stringify({ columns, rows: results }),
              data: { columns, rows: results },
            }}
            sourceFeature={FeatureKey.QUERY}
          />
        </Stack>
        <Stack direction="row" spacing={2}>
          {totalCount !== null && (
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              {totalCount} total rows
            </Typography>
          )}
          {executionTimeMs !== null && (
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              {executionTimeMs}ms
            </Typography>
          )}
        </Stack>
      </Stack>

      <DataTable columns={tableColumns} data={results} pageSize={10} loading={false} />
    </GlassCard>
  )
}
