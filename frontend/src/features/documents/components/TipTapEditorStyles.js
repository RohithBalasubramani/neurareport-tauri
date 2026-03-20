/**
 * Styled components for TipTapEditor
 */
import {
  Box,
  Divider,
  IconButton,
  FormControl,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'

export const EditorContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  overflow: 'hidden',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const Toolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexWrap: 'wrap',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  padding: theme.spacing(1, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

export const ToolbarDivider = styled(Divider)(({ theme }) => ({
  height: 24,
  margin: theme.spacing(0, 0.5),
}))

export const ToolbarButton = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,
  padding: 6,
  '&.active': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    color: theme.palette.text.secondary,
  },
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

export const EditorWrapper = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
  '& .ProseMirror': {
    minHeight: '500px',
    outline: 'none',
    fontFamily: theme.typography.fontFamily,
    fontSize: '1rem',
    lineHeight: 1.8,
    color: theme.palette.text.primary,
    '& p': {
      margin: '0.5em 0',
    },
    '& h1, & h2, & h3, & h4, & h5, & h6': {
      fontWeight: 600,
      marginTop: '1.5em',
      marginBottom: '0.5em',
    },
    '& h1': { fontSize: '2em' },
    '& h2': { fontSize: '1.5em' },
    '& h3': { fontSize: '1.25em' },
    '& ul, & ol': {
      paddingLeft: '1.5em',
    },
    '& blockquote': {
      borderLeft: `4px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}`,
      paddingLeft: '1em',
      marginLeft: 0,
      color: theme.palette.text.secondary,
      fontStyle: 'italic',
    },
    '& code': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      borderRadius: 4,
      padding: '0.2em 0.4em',
      fontFamily: 'monospace',
    },
    '& pre': {
      backgroundColor: alpha(theme.palette.common.black, 0.05),
      borderRadius: 8,
      padding: '1em',
      overflow: 'auto',
      '& code': {
        backgroundColor: 'transparent',
        padding: 0,
      },
    },
    '& hr': {
      border: 'none',
      borderTop: `2px solid ${alpha(theme.palette.divider, 0.2)}`,
      margin: '2em 0',
    },
    '& a': {
      color: theme.palette.text.secondary,
      textDecoration: 'underline',
      cursor: 'pointer',
    },
    '& img': {
      maxWidth: '100%',
      borderRadius: 8,
    },
    '& mark': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      borderRadius: 2,
      padding: '0.1em 0.2em',
    },
    '& ul[data-type="taskList"]': {
      listStyle: 'none',
      paddingLeft: 0,
      '& li': {
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.5em',
        '& input': {
          marginTop: '0.4em',
        },
      },
    },
    '& table': {
      borderCollapse: 'collapse',
      width: '100%',
      margin: '1em 0',
      '& th, & td': {
        border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
        padding: '0.5em',
        minWidth: 80,
      },
      '& th': {
        backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
        fontWeight: 600,
      },
    },
    '& p.is-empty::before': {
      content: 'attr(data-placeholder)',
      color: theme.palette.text.disabled,
      pointerEvents: 'none',
      float: 'left',
      height: 0,
    },
  },
}))

export const HeadingSelect = styled(FormControl)(({ theme }) => ({
  minWidth: 120,
  '& .MuiSelect-select': {
    padding: '4px 8px',
    fontSize: '0.875rem',
  },
}))
