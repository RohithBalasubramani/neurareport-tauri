/**
 * TeamActivity - Multi-agent chat-style activity view.
 *
 * Shows agent messages as chat bubbles with colored avatars,
 * timestamps, and support for different message types.
 */
import React, { useEffect, useRef } from 'react';
import { Avatar, Box, Typography, Paper } from '@mui/material';
import { GlassCard } from '@/styles/components';
import { neutral } from '@/app/theme';

const AGENT_COLORS = {
  template_analyst: '#8B5CF6',
  data_engineer: '#3B82F6',
  report_writer: '#10B981',
  qa_reviewer: '#F59E0B',
  researcher: '#6366F1',
  analyst: '#EC4899',
  writer: '#14B8A6',
  schema_analyst: '#8B5CF6',
  mapping_specialist: '#3B82F6',
  content_reviewer: '#10B981',
  fact_checker: '#F59E0B',
  editor: '#6366F1',
};

const DEFAULT_COLOR = '#6B7280';

function getAgentColor(agent) {
  if (!agent) return DEFAULT_COLOR;
  const key = agent.toLowerCase().replace(/\s+/g, '_');
  return AGENT_COLORS[key] || DEFAULT_COLOR;
}

function getInitials(agent) {
  if (!agent) return '?';
  return agent
    .split(/[\s_]+/)
    .map((w) => w[0]?.toUpperCase() || '')
    .slice(0, 2)
    .join('');
}

function formatTimestamp(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function MessageBubble({ message }) {
  const { agent, content, timestamp, type = 'output' } = message;
  const color = getAgentColor(agent);
  const isThinking = type === 'thinking';
  const isDelegation = type === 'delegation';

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1.5,
        mb: 2,
        alignItems: 'flex-start',
      }}
    >
      <Avatar
        sx={{
          bgcolor: color,
          width: 36,
          height: 36,
          fontSize: '0.8rem',
          fontWeight: 600,
          flexShrink: 0,
        }}
      >
        {getInitials(agent)}
      </Avatar>

      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 0.5 }}>
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: 600,
              color: color,
              textTransform: 'capitalize',
            }}
          >
            {agent ? agent.replace(/_/g, ' ') : 'Unknown Agent'}
          </Typography>
          {timestamp && (
            <Typography variant="caption" sx={{ color: 'text.disabled' }}>
              {formatTimestamp(timestamp)}
            </Typography>
          )}
        </Box>

        <Paper
          elevation={0}
          sx={{
            px: 2,
            py: 1.5,
            borderRadius: 2,
            bgcolor: isDelegation
              ? 'rgba(99, 102, 241, 0.08)'
              : isThinking
                ? 'rgba(0, 0, 0, 0.03)'
                : 'rgba(0, 0, 0, 0.02)',
            borderLeft: `3px solid ${isDelegation ? '#6366F1' : color}`,
          }}
        >
          <Typography
            variant="body2"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              ...(isThinking && {
                fontStyle: 'italic',
                color: 'text.secondary',
              }),
            }}
          >
            {content}
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}

export default function TeamActivity({ messages = [], maxHeight = 500 }) {
  const scrollRef = useRef(null);
  const bottomRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]);

  if (!messages || messages.length === 0) {
    return (
      <GlassCard>
        <Typography
          variant="h6"
          sx={{ color: neutral[900], fontWeight: 600, mb: 2 }}
        >
          Team Activity
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
          No agent activity yet. Start a pipeline to see agent collaboration.
        </Typography>
      </GlassCard>
    );
  }

  return (
    <GlassCard>
      <Typography
        variant="h6"
        sx={{ color: neutral[900], fontWeight: 600, mb: 2 }}
      >
        Team Activity
      </Typography>

      <Box
        ref={scrollRef}
        sx={{
          maxHeight,
          overflowY: 'auto',
          overflowX: 'hidden',
          pr: 1,
          '&::-webkit-scrollbar': {
            width: 6,
          },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: 'rgba(0,0,0,0.15)',
            borderRadius: 3,
          },
        }}
      >
        {messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}
        <div ref={bottomRef} />
      </Box>
    </GlassCard>
  );
}
