import {
  Box,
  Typography,
  Stack,
  Chip,
  Avatar,
  alpha,
} from '@mui/material'
import DataObjectIcon from '@mui/icons-material/DataObject'
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong'
import GavelIcon from '@mui/icons-material/Gavel'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'

export function EntitiesPanel({ entities, theme }) {
  return (
    <GlassCard>
      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
          <DataObjectIcon />
        </Avatar>
        <Typography variant="h6" fontWeight={600}>
          Entities ({entities?.length || 0})
        </Typography>
      </Stack>
      <Stack spacing={1.5}>
        {entities?.slice(0, 20).map((entity) => (
          <Stack
            key={entity.id}
            direction="row"
            alignItems="center"
            spacing={1.5}
            sx={{
              p: 1.5,
              borderRadius: 1,
              bgcolor: alpha(theme.palette.background.default, 0.5),
              transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
              '&:hover': {
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
              },
            }}
          >
            <Chip
              label={entity.type}
              size="small"
              sx={{
                minWidth: 80,
                fontWeight: 600,
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                color: 'text.secondary',
              }}
            />
            <Typography variant="body2" fontWeight={500}>
              {entity.value}
            </Typography>
            {entity.normalized_value && entity.normalized_value !== entity.value && (
              <Typography variant="caption" color="text.secondary">
                → {entity.normalized_value}
              </Typography>
            )}
          </Stack>
        ))}
      </Stack>
    </GlassCard>
  )
}

export function InvoicesPanel({ invoices, theme }) {
  return (
    <GlassCard>
      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
          <ReceiptLongIcon />
        </Avatar>
        <Typography variant="h6" fontWeight={600}>
          Invoices Detected
        </Typography>
      </Stack>
      {invoices.map((invoice) => (
        <Box
          key={invoice.id}
          sx={{
            p: 2,
            mb: 2,
            borderRadius: 1,
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
            border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
          }}
        >
          <Typography variant="subtitle2" fontWeight={600}>
            {invoice.vendor_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Invoice #{invoice.invoice_number} • {invoice.invoice_date}
          </Typography>
          <Typography variant="h5" fontWeight={600} color="text.primary" sx={{ mt: 1 }}>
            {invoice.currency} {invoice.grand_total}
          </Typography>
        </Box>
      ))}
    </GlassCard>
  )
}

export function ContractsPanel({ contracts, theme }) {
  return (
    <GlassCard>
      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
          <GavelIcon />
        </Avatar>
        <Typography variant="h6" fontWeight={600}>
          Contracts Detected
        </Typography>
      </Stack>
      {contracts.map((contract) => (
        <Box
          key={contract.id}
          sx={{
            p: 2,
            borderRadius: 1,
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
            border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
          }}
        >
          <Typography variant="subtitle2" fontWeight={600}>
            {contract.contract_type}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {contract.effective_date} → {contract.expiration_date}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Parties: {contract.parties?.map((p) => p.name).join(', ')}
          </Typography>
        </Box>
      ))}
    </GlassCard>
  )
}
