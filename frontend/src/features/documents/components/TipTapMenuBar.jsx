/**
 * TipTap Editor Menu Bar
 * Toolbar with undo/redo, heading selector, links, images, and formatting controls.
 */
import { useState } from 'react'
import {
  Box,
  Tooltip,
  Select,
  MenuItem,
  Popover,
  Button,
  TextField,
} from '@mui/material'
import {
  Link as LinkIcon,
  Image as ImageIcon,
  Undo,
  Redo,
} from '@mui/icons-material'
import {
  Toolbar,
  ToolbarDivider,
  ToolbarButton,
  HeadingSelect,
} from './TipTapEditorStyles'
import TipTapFormattingButtons from './TipTapFormattingButtons'

export default function MenuBar({ editor }) {
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

  const handleLinkClose = () => { setLinkAnchor(null); setLinkUrl('') }

  const handleLinkSubmit = () => {
    if (linkUrl) {
      editor.chain().focus().extendMarkRange('link').setLink({ href: linkUrl }).run()
    } else {
      editor.chain().focus().extendMarkRange('link').unsetLink().run()
    }
    handleLinkClose()
  }

  const handleImageOpen = (event) => { setImageAnchor(event.currentTarget) }
  const handleImageClose = () => { setImageAnchor(null); setImageUrl('') }

  const handleImageSubmit = () => {
    if (imageUrl) {
      editor.chain().focus().setImage({ src: imageUrl }).run()
    }
    handleImageClose()
  }

  return (
    <Toolbar>
      <Tooltip title="Undo (Ctrl+Z)">
        <ToolbarButton onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()}>
          <Undo fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Redo (Ctrl+Y)">
        <ToolbarButton onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()}>
          <Redo fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <ToolbarDivider orientation="vertical" />

      <HeadingSelect size="small" variant="outlined">
        <Select value={getCurrentHeading()} onChange={handleHeadingChange} displayEmpty>
          <MenuItem value="paragraph">Paragraph</MenuItem>
          <MenuItem value="1">Heading 1</MenuItem>
          <MenuItem value="2">Heading 2</MenuItem>
          <MenuItem value="3">Heading 3</MenuItem>
          <MenuItem value="4">Heading 4</MenuItem>
        </Select>
      </HeadingSelect>

      <ToolbarDivider orientation="vertical" />

      <TipTapFormattingButtons editor={editor} />

      <ToolbarDivider orientation="vertical" />

      <Tooltip title="Insert Link">
        <ToolbarButton onClick={handleLinkOpen} className={editor.isActive('link') ? 'active' : ''}>
          <LinkIcon fontSize="small" />
        </ToolbarButton>
      </Tooltip>
      <Tooltip title="Insert Image">
        <ToolbarButton onClick={handleImageOpen}>
          <ImageIcon fontSize="small" />
        </ToolbarButton>
      </Tooltip>

      <Popover open={Boolean(linkAnchor)} anchorEl={linkAnchor} onClose={handleLinkClose} anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}>
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <TextField size="small" placeholder="Enter URL" value={linkUrl} onChange={(e) => setLinkUrl(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleLinkSubmit()} />
          <Button variant="contained" size="small" onClick={handleLinkSubmit}>{linkUrl ? 'Update' : 'Remove'}</Button>
        </Box>
      </Popover>

      <Popover open={Boolean(imageAnchor)} anchorEl={imageAnchor} onClose={handleImageClose} anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}>
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <TextField size="small" placeholder="Enter image URL" value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleImageSubmit()} />
          <Button variant="contained" size="small" onClick={handleImageSubmit} disabled={!imageUrl}>Insert</Button>
        </Box>
      </Popover>
    </Toolbar>
  )
}
