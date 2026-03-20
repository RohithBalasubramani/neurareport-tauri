/**
 * Shared styled components for the Document Q&A feature.
 */
import {
  Box,
  Chip,
  TextField,
  IconButton,
  Button,
  Avatar,
  Dialog,
  styled,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { slideInLeft, slideInRight, typing, pulse, float } from '@/styles'

export const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: 'calc(100vh - 64px)',
  backgroundColor: 'transparent',
  position: 'relative',
  overflow: 'hidden',
}))

export const Sidebar = styled(Box)(({ theme }) => ({
  width: 300,
  flexShrink: 0,
  display: 'flex',
  flexDirection: 'column',
  background: alpha(theme.palette.background.paper, 0.6),
  backdropFilter: 'blur(20px)',
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 200,
    background: `linear-gradient(180deg, ${alpha(theme.palette.text.primary, 0.03)} 0%, transparent 100%)`,
    pointerEvents: 'none',
  },
}))

export const SidebarHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  position: 'relative',
  zIndex: 1,
}))

export const SessionList = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(0, 2, 2),
  '&::-webkit-scrollbar': {
    width: 6,
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    borderRadius: 1,
    '&:hover': {
      backgroundColor: alpha(theme.palette.text.primary, 0.2),
    },
  },
}))

export const SessionCard = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'selected',
})(({ theme, selected }) => ({
  padding: theme.spacing(1.5),
  borderRadius: 8,
  cursor: 'pointer',
  marginBottom: theme.spacing(1),
  backgroundColor: selected
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100])
    : alpha(theme.palette.background.paper, 0.4),
  border: `1px solid ${selected ? alpha(theme.palette.divider, 0.3) : 'transparent'}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  position: 'relative',
  overflow: 'hidden',
  '&:hover': {
    backgroundColor: selected
      ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200])
      : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]),
    transform: 'translateX(4px)',
  },
  '&::before': selected
    ? {
        content: '""',
        position: 'absolute',
        left: 0,
        top: '50%',
        transform: 'translateY(-50%)',
        width: 3,
        height: '60%',
        background: theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
        borderRadius: '0 4px 4px 0',
      }
    : {},
}))

export const DocumentChip = styled(Chip)(({ theme }) => ({
  height: 24,
  fontSize: 12,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  color: theme.palette.text.secondary,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '& .MuiChip-icon': {
    fontSize: 14,
  },
}))

export const ChatArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: 'transparent',
  position: 'relative',
}))

export const ChatHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  background: alpha(theme.palette.background.paper, 0.4),
  backdropFilter: 'blur(10px)',
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const MessagesContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
  '&::-webkit-scrollbar': {
    width: 8,
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    borderRadius: 4,
    '&:hover': {
      backgroundColor: alpha(theme.palette.text.primary, 0.2),
    },
  },
}))

export const MessageBubble = styled(Box, {
  shouldForwardProp: (prop) => !['isUser', 'index'].includes(prop),
})(({ theme, isUser, index }) => ({
  maxWidth: '75%',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  animation: `${isUser ? slideInRight : slideInLeft} 0.4s ease-out`,
  animationDelay: `${index * 0.05}s`,
  animationFillMode: 'both',
}))

export const BubbleContent = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'isUser',
})(({ theme, isUser }) => ({
  padding: theme.spacing(2, 2.5),
  borderRadius: isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
  backgroundColor: isUser
    ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
    : alpha(theme.palette.background.paper, 0.8),
  color: isUser ? theme.palette.common.white : theme.palette.text.primary,
  backdropFilter: isUser ? 'none' : 'blur(10px)',
  border: isUser ? 'none' : `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  position: 'relative',
  boxShadow: isUser
    ? `0 4px 20px ${alpha(theme.palette.common.black, 0.2)}`
    : `0 4px 20px ${alpha(theme.palette.common.black, 0.05)}`,
}))

export const AvatarStyled = styled(Avatar, {
  shouldForwardProp: (prop) => prop !== 'isUser',
})(({ theme, isUser }) => ({
  width: 36,
  height: 36,
  background: isUser
    ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
    : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]),
  border: `2px solid ${alpha(theme.palette.background.paper, 0.8)}`,
  boxShadow: `0 2px 10px ${alpha(theme.palette.common.black, 0.1)}`,
  '& svg': {
    fontSize: 18,
    color: isUser ? theme.palette.common.white : theme.palette.text.secondary,
  },
}))

export const CitationBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(2),
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const CitationItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'flex-start',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
  borderRadius: 8,
  backgroundColor: alpha(theme.palette.background.paper, 0.5),
  marginTop: theme.spacing(1),
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

export const FollowUpChip = styled(Chip)(({ theme }) => ({
  borderRadius: 20,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  color: theme.palette.text.primary,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
    transform: 'translateY(-2px)',
    boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

export const InputArea = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3, 3),
  background: `linear-gradient(180deg, transparent 0%, ${alpha(theme.palette.background.paper, 0.6)} 30%)`,
  backdropFilter: 'blur(10px)',
}))

export const InputContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'flex-end',
  gap: theme.spacing(1.5),
  padding: theme.spacing(1.5),
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  borderRadius: 24,
  border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.05)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:focus-within': {
    borderColor: alpha(theme.palette.divider, 0.4),
    boxShadow: `0 4px 30px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

export const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: 'transparent',
    fontSize: 16,
    '& fieldset': {
      border: 'none',
    },
  },
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 0),
    '&::placeholder': {
      color: alpha(theme.palette.text.secondary, 0.6),
    },
  },
}))

export const SendButton = styled(IconButton)(({ theme }) => ({
  width: 44,
  height: 44,
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    transform: 'scale(1.05)',
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.2)}`,
  },
  '&:disabled': {
    background: alpha(theme.palette.text.primary, 0.1),
    color: alpha(theme.palette.text.primary, 0.3),
  },
}))

export const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: 6,
  padding: theme.spacing(2),
  '& span': {
    width: 8,
    height: 8,
    borderRadius: '50%',
    backgroundColor: theme.palette.text.secondary,
    animation: `${typing} 1.4s infinite ease-in-out`,
    '&:nth-of-type(1)': { animationDelay: '0s' },
    '&:nth-of-type(2)': { animationDelay: '0.2s' },
    '&:nth-of-type(3)': { animationDelay: '0.4s' },
  },
}))

export const ThinkingBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
  padding: theme.spacing(1.5, 2),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  borderRadius: 8,
  marginBottom: theme.spacing(1),
  animation: `${pulse} 2s infinite ease-in-out`,
}))

export const EmptyState = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  textAlign: 'center',
}))

export const EmptyIcon = styled(Box)(({ theme }) => ({
  width: 120,
  height: 120,
  borderRadius: '50%',
  background: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(3),
  animation: `${float} 3s infinite ease-in-out`,
  '& svg': {
    fontSize: 56,
    color: theme.palette.text.secondary,
  },
}))

export const SuggestionCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: 8,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
    borderColor: alpha(theme.palette.divider, 0.2),
    transform: 'translateY(-2px)',
  },
}))

export const ActionButton = styled(IconButton)(({ theme }) => ({
  width: 28,
  height: 28,
  color: alpha(theme.palette.text.secondary, 0.6),
  '&:hover': {
    color: theme.palette.text.primary,
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

export const NewSessionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  padding: theme.spacing(1.5, 2),
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  fontWeight: 600,
  textTransform: 'none',
  boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.15)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    transform: 'translateY(-2px)',
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 6px 28px ${alpha(theme.palette.common.black, 0.2)}`,
  },
}))

export const DocumentsSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
}))

export const LoadingOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: alpha(theme.palette.background.default, 0.8),
  backdropFilter: 'blur(8px)',
  zIndex: 10,
}))

export const LoadingSpinner = styled(Box)(({ theme }) => ({
  width: 48,
  height: 48,
  borderRadius: '50%',
  background: `conic-gradient(from 0deg, transparent, ${theme.palette.text.secondary})`,
  animation: 'spin 1s linear infinite',
  '@keyframes spin': {
    to: { transform: 'rotate(360deg)' },
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    inset: 4,
    borderRadius: '50%',
    backgroundColor: theme.palette.background.paper,
  },
}))

export const GlassDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    backgroundColor: alpha(theme.palette.background.paper, 0.9),
    backdropFilter: 'blur(20px)',
    borderRadius: 8,
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  },
}))

// Constants
export const MAX_DOC_SIZE = 5 * 1024 * 1024
export const MIN_DOC_LENGTH = 10
export const MAX_NAME_LENGTH = 200
export const MIN_QUESTION_LENGTH = 3
export const MAX_QUESTION_LENGTH = 2000
