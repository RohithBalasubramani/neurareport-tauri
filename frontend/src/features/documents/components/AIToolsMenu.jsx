/**
 * AI Tools dropdown menu for the Document Editor.
 */
import { Menu, MenuItem, ListItemIcon, ListItemText } from '@mui/material'
import {
  Spellcheck as GrammarIcon, Summarize as SummarizeIcon,
  Edit as RewriteIcon, Translate as TranslateIcon,
  Expand as ExpandIcon, FormatColorFill as ToneIcon,
} from '@mui/icons-material'

export default function AIToolsMenu({ anchorEl, onClose, onAIAction }) {
  return (
    <Menu
      anchorEl={anchorEl}
      open={Boolean(anchorEl)}
      onClose={onClose}
      PaperProps={{
        sx: {
          borderRadius: 1,  // Figma spec: 8px
          minWidth: 200,
        },
      }}
    >
      <MenuItem onClick={() => onAIAction('grammar')} data-testid="ai-grammar">
        <ListItemIcon><GrammarIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Check Grammar</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAIAction('summarize')} data-testid="ai-summarize">
        <ListItemIcon><SummarizeIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Summarize</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAIAction('rewrite')} data-testid="ai-rewrite">
        <ListItemIcon><RewriteIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Rewrite</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAIAction('expand')} data-testid="ai-expand">
        <ListItemIcon><ExpandIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Expand</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAIAction('translate')} data-testid="ai-translate">
        <ListItemIcon><TranslateIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Translate</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAIAction('tone')} data-testid="ai-tone">
        <ListItemIcon><ToneIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Adjust Tone</ListItemText>
      </MenuItem>
    </Menu>
  )
}
