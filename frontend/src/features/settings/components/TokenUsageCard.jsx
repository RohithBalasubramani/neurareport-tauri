/**
 * Token usage statistics card
 */
import { Stack, Typography, Divider, useTheme, alpha } from '@mui/material'
import TokenIcon from '@mui/icons-material/Toll'
import SettingCard from './SettingCard'
import ConfigRow from './ConfigRow'

export default function TokenUsageCard({ tokenUsage }) {
  const theme = useTheme()

  return (
    <SettingCard icon={TokenIcon} title="Token Usage">
      {tokenUsage ? (
        <Stack spacing={1}>
          <ConfigRow
            label="Total Tokens"
            value={(tokenUsage.total_tokens || 0).toLocaleString()}
          />
          <ConfigRow
            label="Input Tokens"
            value={(tokenUsage.total_input_tokens || 0).toLocaleString()}
          />
          <ConfigRow
            label="Output Tokens"
            value={(tokenUsage.total_output_tokens || 0).toLocaleString()}
          />
          <Divider sx={{ my: 1, borderColor: alpha(theme.palette.divider, 0.08) }} />
          <ConfigRow
            label="Estimated Cost"
            value={`$${(tokenUsage.estimated_cost_usd || 0).toFixed(4)}`}
            mono
          />
          <ConfigRow
            label="API Requests"
            value={(tokenUsage.request_count || 0).toLocaleString()}
          />
          <Typography variant="caption" sx={{ color: theme.palette.text.disabled, mt: 1 }}>
            Usage statistics are tracked since server start.
          </Typography>
        </Stack>
      ) : (
        <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
          Token usage data unavailable
        </Typography>
      )}
    </SettingCard>
  )
}
