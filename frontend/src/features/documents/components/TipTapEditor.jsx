/**
 * TipTap Rich Text Editor Component
 * Full-featured WYSIWYG editor with toolbar, formatting, and collaboration support.
 */
import { useCallback, useEffect, useRef } from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import Highlight from '@tiptap/extension-highlight'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TextStyle from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import {
  Box,
  IconButton,
  Tooltip,
  Divider,
  Select,
  MenuItem,
  FormControl,
  ToggleButton,
  ToggleButtonGroup,
  Popover,
  Button,
  TextField,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  FormatBold,
  FormatItalic,
  FormatUnderlined,
  FormatStrikethrough,
  FormatListBulleted,
  FormatListNumbered,
  FormatQuote,
  Code,
  Link as LinkIcon,
  Image as ImageIcon,
  FormatAlignLeft,
  FormatAlignCenter,
  FormatAlignRight,
  FormatAlignJustify,
  Undo,
  Redo,
  Highlight as HighlightIcon,
  CheckBox,
  TableChart,
  FormatClear,
  HorizontalRule,
} from '@mui/icons-material'
import { useState } from 'react'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const EditorContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,  // Figma spec: 8px
  overflow: 'hidden',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const Toolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexWrap: 'wrap',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  padding: theme.spacing(1, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

const ToolbarDivider = styled(Divider)(({ theme }) => ({
  height: 24,
  margin: theme.spacing(0, 0.5),
}))

const ToolbarButton = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  padding: 6,
  '&.active': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    color: theme.palette.text.secondary,
  },
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

const EditorWrapper = styled(Box)(({ theme }) => ({
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

const HeadingSelect = styled(FormControl)(({ theme }) => ({
  minWidth: 120,
  '& .MuiSelect-select': {
    padding: '4px 8px',
    fontSize: '0.875rem',
  },
}))

// =============================================================================
// MENU BAR COMPONENT
// =============================================================================

function MenuBar({ editor }) {
  const theme = useTheme()
  const [linkAnchor, setLinkAnchor] = useState(null)
  const [linkUrl, setLinkUrl] = useState('')
  const [imageAnchor, setImageAnchor] = useState(null)
  const [imageUrl, setImageUrl] = useState('')

  if (!editor) return null

  const handleHeadingChange = (event) => {
    const value = event.target.value
    if (value === 'paragraph') {
      editor.chain().focus().setParagraph().run()
    } else {
      editor.chain().focus().toggleHeading({ level: parseInt(value) }).run()
    }
  }

  const getCurrentHeading = () => {
    for (let i = 1; i <= 6; i++) {
      if (editor.isActive('heading', { level: i })) return String(i)
    }
    return 'paragraph'
  }

  const handleLinkOpen = (event) => {
    const previousUrl = editor.getAttributes('link').href || ''
    setLinkUrl(previousUrl)
    setLinkAnchor(event.currentTarget)
  }

  const handleLinkClose = () => {
    setLinkAnchor(null)
    setLinkUrl('')
  }

  const handleLinkSubmit = () => {
    if (linkUrl) {
      editor.chain().focus().extendMarkRange('link').setLink({ href: linkUrl }).run()
    } else {
      editor.chain().focus().extendMarkRange('link').unsetLink().run()
    }
    handleLinkClose()
  }

  const handleImageOpen = (event) => {
    setImageAnchor(event.currentTarget)
  }

  const handleImageClose = () => {
    setImageAnchor(null)
    setImageUrl('')
  }

  const handleImageSubmit = () => {
    if (imageUrl) {
      editor.chain().focus().setImage({ src: imageUrl }).run()
    }
    handleImageClose()
  }

  const addTable = () => {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
  }

  return (
    <Toolbar>
      {/* Undo/Redo */}
      <Tooltip title="Undo (Ctrl+Z)">
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
        >
          <Undo fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Redo (Ctrl+Y)">
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
        >
          <Redo fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      {/* Heading Selector */}
      <HeadingSelect size="small" variant="outlined">
        <Select
          value={getCurrentHeading()}
          onChange={handleHeadingChange}
          displayEmpty
        >
          <MenuItem value="paragraph">Paragraph</MenuItem>
          <MenuItem value="1">Heading 1</MenuItem>
          <MenuItem value="2">Heading 2</MenuItem>
          <MenuItem value="3">Heading 3</MenuItem>
          <MenuItem value="4">Heading 4</MenuItem>
        </Select>
      </HeadingSelect>

      <ToolbarDivider orientation="vertical" />

      {/* Text Formatting */}
      <Tooltip title="Bold (Ctrl+B)">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'active' : ''}
        >
          <FormatBold fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Italic (Ctrl+I)">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'active' : ''}
        >
          <FormatItalic fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Underline (Ctrl+U)">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          className={editor.isActive('underline') ? 'active' : ''}
        >
          <FormatUnderlined fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Strikethrough">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={editor.isActive('strike') ? 'active' : ''}
        >
          <FormatStrikethrough fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Highlight">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHighlight().run()}
          className={editor.isActive('highlight') ? 'active' : ''}
        >
          <HighlightIcon fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Code">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCode().run()}
          className={editor.isActive('code') ? 'active' : ''}
        >
          <Code fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      {/* Text Alignment */}
      <Tooltip title="Align Left">
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          className={editor.isActive({ textAlign: 'left' }) ? 'active' : ''}
        >
          <FormatAlignLeft fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Align Center">
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          className={editor.isActive({ textAlign: 'center' }) ? 'active' : ''}
        >
          <FormatAlignCenter fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Align Right">
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          className={editor.isActive({ textAlign: 'right' }) ? 'active' : ''}
        >
          <FormatAlignRight fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Justify">
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('justify').run()}
          className={editor.isActive({ textAlign: 'justify' }) ? 'active' : ''}
        >
          <FormatAlignJustify fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      {/* Lists */}
      <Tooltip title="Bullet List">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'active' : ''}
        >
          <FormatListBulleted fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Numbered List">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'active' : ''}
        >
          <FormatListNumbered fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Task List">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleTaskList().run()}
          className={editor.isActive('taskList') ? 'active' : ''}
        >
          <CheckBox fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      {/* Block Elements */}
      <Tooltip title="Quote">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          className={editor.isActive('blockquote') ? 'active' : ''}
        >
          <FormatQuote fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Horizontal Rule">
        <ToolbarButton onClick={() => editor.chain().focus().setHorizontalRule().run()}>
          <HorizontalRule fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Insert Table">
        <ToolbarButton onClick={addTable}>
          <TableChart fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      {/* Links & Images */}
      <Tooltip title="Insert Link">
        <ToolbarButton
          onClick={handleLinkOpen}
          className={editor.isActive('link') ? 'active' : ''}
        >
          <LinkIcon fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Insert Image">
        <ToolbarButton onClick={handleImageOpen}>
          <ImageIcon fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      {/* Clear Formatting */}
      <Tooltip title="Clear Formatting">
        <ToolbarButton
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
        >
          <FormatClear fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      {/* Link Popover */}
      <Popover
        open={Boolean(linkAnchor)}
        anchorEl={linkAnchor}
        onClose={handleLinkClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <TextField
            size="small"
            placeholder="Enter URL"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLinkSubmit()}
          />
          <Button variant="contained" size="small" onClick={handleLinkSubmit}>
            {linkUrl ? 'Update' : 'Remove'}
          </Button>
        </Box>
      </Popover>

      {/* Image Popover */}
      <Popover
        open={Boolean(imageAnchor)}
        anchorEl={imageAnchor}
        onClose={handleImageClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <TextField
            size="small"
            placeholder="Enter image URL"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleImageSubmit()}
          />
          <Button
            variant="contained"
            size="small"
            onClick={handleImageSubmit}
            disabled={!imageUrl}
          >
            Insert
          </Button>
        </Box>
      </Popover>
    </Toolbar>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function TipTapEditor({
  content,
  onUpdate,
  onSelectionChange,
  placeholder = 'Start writing your document...',
  editable = true,
}) {
  const isInternalUpdate = useRef(false)

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3, 4] },
      }),
      Underline,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          target: '_blank',
          rel: 'noopener noreferrer',
        },
      }),
      Image.configure({
        inline: false,
        allowBase64: true,
      }),
      Placeholder.configure({
        placeholder,
      }),
      Highlight.configure({
        multicolor: false,
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,
      TextStyle,
      Color,
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      isInternalUpdate.current = true
      onUpdate?.(editor.getJSON())
      isInternalUpdate.current = false
    },
    onSelectionUpdate: ({ editor }) => {
      const { from, to } = editor.state.selection
      const selectedText = editor.state.doc.textBetween(from, to, ' ')
      onSelectionChange?.(selectedText)
    },
  })

  // Update content when it changes externally
  useEffect(() => {
    if (isInternalUpdate.current) {
      isInternalUpdate.current = false
      return
    }
    if (editor && content && JSON.stringify(editor.getJSON()) !== JSON.stringify(content)) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  // Update editable state
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable)
    }
  }, [editable, editor])

  return (
    <EditorContainer>
      <MenuBar editor={editor} />
      <EditorWrapper>
        <EditorContent editor={editor} />
      </EditorWrapper>
    </EditorContainer>
  )
}

// Export editor hook for external access
export function useTipTapEditor() {
  return useEditor
}
