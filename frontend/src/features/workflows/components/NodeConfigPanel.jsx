/**
 * Node Configuration Panel Component
 * Settings panel for configuring workflow nodes (actions, conditions, triggers).
 */
import {
  Box,
  Typography,
  IconButton,
  Chip,
  Stack,
  Button,
  AccordionSummary,
  AccordionDetails,
  alpha,
} from '@mui/material'
import {
  Close as CloseIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import {
  PanelContainer,
  PanelHeader,
  PanelContent,
  PanelFooter,
  NodeTypeChip,
  VariableChip,
  ConfigAccordion,
  AVAILABLE_VARIABLES,
} from './NodeConfigPanel.styles'
import { renderNodeConfigForm } from './NodeActionConfigs'
import NodeBasicSettings from './NodeBasicSettings'
import NodeErrorHandling from './NodeErrorHandling'
import { useNodeConfigPanel } from '../hooks/useNodeConfigPanel'

export default function NodeConfigPanel({
  node = null,
  onChange,
  onDelete,
  onTest,
  onClose,
}) {
  const {
    expandedSections,
    nodeTypeInfo,
    handleChange,
    handleConfigChange,
    toggleSection,
    insertVariable,
  } = useNodeConfigPanel({ node, onChange })

  if (!node) {
    return (
      <PanelContainer>
        <PanelHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Node Configuration
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </PanelHeader>
        <PanelContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <SettingsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              Select a node to configure
            </Typography>
          </Box>
        </PanelContent>
      </PanelContainer>
    )
  }

  const NodeIcon = nodeTypeInfo?.icon || SettingsIcon

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <NodeIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Configure Node
          </Typography>
        </Stack>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </PanelHeader>

      <PanelContent>
        <Stack direction="row" spacing={1} mb={2}>
          <NodeTypeChip
            label={nodeTypeInfo?.label || node.type}
            size="small"
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
          <Chip label={`ID: ${node.id}`} size="small" variant="outlined" />
        </Stack>

        <NodeBasicSettings
          node={node}
          expanded={expandedSections.includes('basic')}
          onToggle={() => toggleSection('basic')}
          handleChange={handleChange}
          handleConfigChange={handleConfigChange}
        />

        <ConfigAccordion
          expanded={expandedSections.includes('config')}
          onChange={() => toggleSection('config')}
          sx={{ mb: 1.5 }}
        >
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              Configuration
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {renderNodeConfigForm(node, handleConfigChange)}
          </AccordionDetails>
        </ConfigAccordion>

        <ConfigAccordion
          expanded={expandedSections.includes('variables')}
          onChange={() => toggleSection('variables')}
          sx={{ mb: 1.5 }}
        >
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              Available Variables
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Click to copy variable syntax
            </Typography>
            <Stack spacing={0.5}>
              {AVAILABLE_VARIABLES.map((v) => (
                <Stack
                  key={v.name}
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <VariableChip
                    label={`{{${v.name}}}`}
                    size="small"
                    onClick={() => insertVariable(v.name)}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {v.description}
                  </Typography>
                </Stack>
              ))}
            </Stack>
          </AccordionDetails>
        </ConfigAccordion>

        <NodeErrorHandling
          node={node}
          expanded={expandedSections.includes('errors')}
          onToggle={() => toggleSection('errors')}
          handleChange={handleChange}
        />
      </PanelContent>

      <PanelFooter>
        <Stack direction="row" spacing={1} justifyContent="space-between">
          <Button
            variant="outlined"
            size="small"
            startIcon={<DeleteIcon />}
            onClick={onDelete}
            sx={{ color: 'text.secondary' }}
          >
            Delete
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={<PlayIcon />}
            onClick={onTest}
          >
            Test Node
          </Button>
        </Stack>
      </PanelFooter>
    </PanelContainer>
  )
}
