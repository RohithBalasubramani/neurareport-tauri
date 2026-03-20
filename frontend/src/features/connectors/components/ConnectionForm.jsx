/**
 * Connection Form Component
 * Dynamic form for database and cloud connector configuration.
 */
import { useState } from 'react'
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  IconButton,
  useTheme,
  alpha,
} from '@mui/material'
import {
  ExpandMore as ExpandIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material'
import OAuthButton, { isOAuthProvider } from './OAuthButton'
import { CONNECTOR_FIELDS, getConnectorConfig, validateConnectionForm } from './connectorFieldConfigs'
import ConnectionFormField from './ConnectionFormField'

export default function ConnectionForm({
  connectorType,
  values = {},
  onChange,
  errors = {},
  disabled = false,
  showAdvanced = false,
  onOAuthConnect,
  oauthConnected = false,
}) {
  const theme = useTheme()
  const [advancedOpen, setAdvancedOpen] = useState(showAdvanced)
  const [showPasswords, setShowPasswords] = useState({})

  const config = CONNECTOR_FIELDS[connectorType] || { name: connectorType, fields: [] }
  const fields = config.fields || []
  const advancedFields = config.advanced || []
  const isOAuth = config.oauth || false

  const handleChange = (fieldName, value) => {
    onChange?.({ ...values, [fieldName]: value })
  }

  const togglePassword = (fieldName) => {
    setShowPasswords((prev) => ({ ...prev, [fieldName]: !prev[fieldName] }))
  }

  return (
    <Box>
      {/* OAuth Section */}
      {isOAuth && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
            Authentication
          </Typography>
          <OAuthButton
            provider={connectorType}
            connected={oauthConnected}
            onConnect={onOAuthConnect}
            disabled={disabled}
          />
        </Box>
      )}

      {/* Main Fields */}
      {(!isOAuth || oauthConnected) && fields.length > 0 && (
        <Box>
          {isOAuth && (
            <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
              Configuration
            </Typography>
          )}
          {fields.map((field) => (
            <ConnectionFormField
              key={field.name}
              field={field}
              value={values[field.name] ?? field.default ?? ''}
              error={errors[field.name]}
              disabled={disabled}
              showPassword={showPasswords[field.name]}
              onChange={handleChange}
              onTogglePassword={togglePassword}
            />
          ))}
        </Box>
      )}

      {/* Advanced Fields */}
      {advancedFields.length > 0 && (
        <Accordion
          expanded={advancedOpen}
          onChange={() => setAdvancedOpen(!advancedOpen)}
          elevation={0}
          sx={{
            mt: 2,
            backgroundColor: alpha(theme.palette.background.default, 0.5),
            '&:before': { display: 'none' },
          }}
        >
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              Advanced Options
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {advancedFields.map((field) => (
              <ConnectionFormField
                key={field.name}
                field={field}
                value={values[field.name] ?? field.default ?? ''}
                error={errors[field.name]}
                disabled={disabled}
                showPassword={showPasswords[field.name]}
                onChange={handleChange}
                onTogglePassword={togglePassword}
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  )
}

export { getConnectorConfig, validateConnectionForm }
