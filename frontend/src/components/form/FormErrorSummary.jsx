import { useMemo } from 'react'
import {
  Alert,
  AlertTitle,
  Collapse,
  List,
  ListItemButton,
  ListItemText,
  Typography,
} from '@mui/material'


const flattenErrors = (errorMap, prefix = '') => {
  if (!errorMap || typeof errorMap !== 'object') return []
  return Object.entries(errorMap).flatMap(([key, value]) => {
    if (!value) return []
    const path = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'object' && 'message' in value && value.message) {
      return [{ name: path, message: value.message }]
    }
    if (typeof value === 'object') {
      return flattenErrors(value, path)
    }
    return []
  })
}

const orderByField = (items, fieldOrder) => {
  if (!fieldOrder?.length) return items
  const orderMap = new Map(fieldOrder.map((field, index) => [field, index]))
  return [...items].sort((a, b) => {
    const aIndex = orderMap.has(a.name) ? orderMap.get(a.name) : Number.MAX_SAFE_INTEGER
    const bIndex = orderMap.has(b.name) ? orderMap.get(b.name) : Number.MAX_SAFE_INTEGER
    if (aIndex !== bIndex) return aIndex - bIndex
    return a.name.localeCompare(b.name)
  })
}

export default function FormErrorSummary({
  errors,
  visible = true,
  title = 'Please fix the highlighted fields',
  description = 'Select an item below to jump to the field.',
  fieldOrder = [],
  fieldLabels = {},
  onFocusField,
  sx = [],
}) {
  const items = useMemo(() => {
    const flattened = flattenErrors(errors)
    const unique = []
    const seen = new Set()
    flattened.forEach((item) => {
      const key = `${item.name}-${item.message}`
      if (seen.has(key)) return
      seen.add(key)
      unique.push(item)
    })
    return orderByField(unique, fieldOrder)
  }, [errors, fieldOrder])

  if (!visible || !items.length) return null

  const sxArray = Array.isArray(sx) ? sx : [sx]

  return (
    <Collapse in={visible} timeout={180}>
      <Alert
        severity="error"
        role="alert"
        tabIndex={-1}
        sx={[
          {
            borderRadius: 1,  // Figma spec: 8px
            alignItems: 'stretch',
          },
          ...sxArray,
        ]}
      >
        <AlertTitle sx={{ fontWeight: 600 }}>{title}</AlertTitle>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          {description}
        </Typography>
        <List disablePadding dense>
          {items.map((item) => {
            const itemLabel = fieldLabels[item.name] || item.name
            const button = typeof onFocusField === 'function'
            return (
              <ListItemButton
                key={`${item.name}-${item.message}`}
                onClick={button ? () => onFocusField(item.name) : undefined}
                disabled={!button}
                tabIndex={button ? 0 : -1}
                sx={{
                  borderRadius: 1,
                  px: 1,
                  mb: 0.5,
                  alignItems: 'flex-start',
                  '&:last-of-type': { mb: 0 },
                }}
              >
                <ListItemText
                  primaryTypographyProps={{ variant: 'body2', fontWeight: 600 }}
                  secondaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                  primary={item.message}
                  secondary={itemLabel}
                />
              </ListItemButton>
            )
          })}
        </List>
      </Alert>
    </Collapse>
  )
}
