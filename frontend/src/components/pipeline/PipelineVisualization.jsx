/**
 * PipelineVisualization - MUI Stepper-based pipeline progress view.
 *
 * Shows each stage of a multi-agent pipeline with status indicators,
 * agent roles, and collapsible output previews.
 */
import React from 'react';
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  LinearProgress,
  Typography,
  Box,
  Collapse,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import PlayCircleFilledIcon from '@mui/icons-material/PlayCircleFilled';
import { GlassCard } from '@/styles/components';
import { neutral } from '@/app/theme';

const STATUS_CONFIG = {
  completed: { color: 'success', label: 'Completed', icon: <CheckCircleIcon fontSize="small" /> },
  in_progress: { color: 'info', label: 'In Progress', icon: <PlayCircleFilledIcon fontSize="small" /> },
  pending: { color: 'default', label: 'Pending', icon: <RadioButtonUncheckedIcon fontSize="small" /> },
  failed: { color: 'error', label: 'Failed', icon: <ErrorIcon fontSize="small" /> },
};

function StageStepIcon({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  const isActive = status === 'in_progress';

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: status === 'completed'
          ? 'success.main'
          : status === 'in_progress'
            ? 'info.main'
            : status === 'failed'
              ? 'error.main'
              : 'text.disabled',
        ...(isActive && {
          animation: 'pulse 1.5s ease-in-out infinite',
          '@keyframes pulse': {
            '0%': { opacity: 1 },
            '50%': { opacity: 0.5 },
            '100%': { opacity: 1 },
          },
        }),
      }}
    >
      {config.icon}
    </Box>
  );
}

function OutputPreview({ output }) {
  const [expanded, setExpanded] = React.useState(false);

  if (!output) return null;

  const text = typeof output === 'string' ? output : JSON.stringify(output, null, 2);
  const isLong = text.length > 200;

  return (
    <Box sx={{ mt: 1 }}>
      <Typography
        variant="body2"
        sx={{
          color: 'text.secondary',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '0.8rem',
          maxHeight: expanded ? 'none' : 80,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {expanded ? text : text.slice(0, 200)}
        {!expanded && isLong && '...'}
      </Typography>
      {isLong && (
        <Typography
          variant="caption"
          sx={{ color: 'primary.main', cursor: 'pointer', mt: 0.5, display: 'inline-block' }}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Show less' : 'Show more'}
        </Typography>
      )}
    </Box>
  );
}

export default function PipelineVisualization({ pipelineId, stages = [], compact = false }) {
  if (!stages || stages.length === 0) {
    return (
      <GlassCard>
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
          No pipeline stages to display.
        </Typography>
      </GlassCard>
    );
  }

  const activeStep = stages.findIndex((s) => s.status === 'in_progress');
  const resolvedActiveStep = activeStep >= 0 ? activeStep : stages.filter((s) => s.status === 'completed').length;

  return (
    <GlassCard>
      <Typography
        variant="h6"
        sx={{
          color: neutral[900],
          fontWeight: 600,
          mb: 2,
        }}
      >
        Pipeline Progress
      </Typography>

      <Stepper
        activeStep={resolvedActiveStep}
        orientation="vertical"
        sx={{ '& .MuiStepConnector-line': { minHeight: compact ? 16 : 24 } }}
      >
        {stages.map((stage, index) => {
          const status = stage.status || 'pending';
          const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;

          return (
            <Step key={index} completed={status === 'completed'} active={status === 'in_progress'}>
              <StepLabel
                StepIconComponent={() => <StageStepIcon status={status} />}
                optional={
                  stage.agent && !compact ? (
                    <Typography variant="caption" color="text.secondary">
                      Agent: {stage.agent}
                    </Typography>
                  ) : null
                }
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: status === 'in_progress' ? 600 : 400 }}>
                    {stage.label}
                  </Typography>
                  <Chip
                    label={config.label}
                    color={config.color}
                    size="small"
                    variant={status === 'pending' ? 'outlined' : 'filled'}
                    sx={{ height: 22, fontSize: '0.7rem' }}
                  />
                </Box>
              </StepLabel>

              {!compact && (
                <StepContent>
                  {status === 'in_progress' && (
                    <LinearProgress
                      sx={{
                        borderRadius: 1,
                        height: 4,
                        mb: 1,
                      }}
                    />
                  )}
                  <OutputPreview output={stage.output} />
                </StepContent>
              )}
            </Step>
          );
        })}
      </Stepper>
    </GlassCard>
  );
}
