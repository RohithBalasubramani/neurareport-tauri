/**
 * TipTap Formatting Buttons
 * Text formatting, alignment, and list controls for the editor toolbar.
 */
import { Tooltip } from '@mui/material'
import {
  FormatBold,
  FormatItalic,
  FormatUnderlined,
  FormatStrikethrough,
  FormatListBulleted,
  FormatListNumbered,
  FormatQuote,
  Code,
  FormatAlignLeft,
  FormatAlignCenter,
  FormatAlignRight,
  FormatAlignJustify,
  Highlight as HighlightIcon,
  CheckBox,
  TableChart,
  FormatClear,
  HorizontalRule,
} from '@mui/icons-material'
import { ToolbarDivider, ToolbarButton } from './TipTapEditorStyles'

export default function TipTapFormattingButtons({ editor }) {
  if (!editor) return null

  const addTable = () => {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
  }

  return (
    <>
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

      <Tooltip title="Clear Formatting">
        <ToolbarButton
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
        >
          <FormatClear fontSize="small" />
        </ToolbarButton>
      </Tooltip>
    </>
  )
}
