/**
 * Widget Palette Component
 * Draggable widget options with variant sub-menus for AI widgets.
 */
import { useState, useCallback } from 'react'
import { Typography, CardContent, Collapse, IconButton } from '@mui/material'
import { ExpandMore as ExpandIcon, ExpandLess as CollapseIcon } from '@mui/icons-material'
import { SCENARIO_VARIANTS, DEFAULT_VARIANTS } from '../constants/widgetVariants'
import { WIDGET_CATEGORIES, parseWidgetType, getWidgetDefinition, ALL_WIDGET_TYPES } from './widgetCategories'
import VariantPickerPopover from './VariantPickerPopover'
import { PaletteContainer, CategoryHeader, WidgetCard, WidgetGrid, VariantBadge } from './widgetPaletteStyles'

export default function WidgetPalette({ onAddWidget }) {
  const [expandedCategories, setExpandedCategories] = useState(
    WIDGET_CATEGORIES.reduce((acc, cat) => ({ ...acc, [cat.id]: !cat.defaultCollapsed }), {})
  )
  const [variantAnchor, setVariantAnchor] = useState(null)
  const [variantWidget, setVariantWidget] = useState(null)

  const toggleCategory = useCallback((categoryId) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [categoryId]: !prev[categoryId],
    }))
  }, [])

  const handleDragStart = useCallback((e, widget, variant) => {
    e.dataTransfer.setData('widget-type', widget.type)
    e.dataTransfer.setData('widget-label', widget.label)
    if (variant) {
      e.dataTransfer.setData('widget-variant', variant)
    }
    e.dataTransfer.effectAllowed = 'copy'
  }, [])

  const handleWidgetClick = useCallback((widget, e) => {
    const variants = SCENARIO_VARIANTS[widget.type]
    if (widget.hasVariants && variants && variants.length > 1) {
      setVariantAnchor(e.currentTarget)
      setVariantWidget(widget)
      return
    }
    const defaultVariant = DEFAULT_VARIANTS[widget.type]
    onAddWidget?.(widget.type, widget.label, defaultVariant)
  }, [onAddWidget])

  const handleVariantSelect = useCallback((scenario, variant) => {
    const vConfig = VARIANT_CONFIG[variant]
    const label = vConfig?.label || variant
    onAddWidget?.(scenario, label, variant)
    setVariantAnchor(null)
    setVariantWidget(null)
  }, [onAddWidget])

  const handleCloseVariantPicker = useCallback(() => {
    setVariantAnchor(null)
    setVariantWidget(null)
  }, [])

  return (
    <PaletteContainer>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        Add Widget
      </Typography>

      {WIDGET_CATEGORIES.map((category) => (
        <Box key={category.id}>
          <CategoryHeader onClick={() => toggleCategory(category.id)}>
            <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
              {category.label}
            </Typography>
            <IconButton size="small">
              {expandedCategories[category.id] ? (
                <CollapseIcon fontSize="small" />
              ) : (
                <ExpandIcon fontSize="small" />
              )}
            </IconButton>
          </CategoryHeader>

          <Collapse in={expandedCategories[category.id]}>
            <WidgetGrid>
              {category.widgets.map((widget) => {
                const variantCount = SCENARIO_VARIANTS[widget.type]?.length || 0
                return (
                  <WidgetCard
                    key={widget.type}
                    variant="outlined"
                    draggable
                    onDragStart={(e) => handleDragStart(e, widget)}
                    onClick={(e) => handleWidgetClick(widget, e)}
                  >
                    <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                      <Box
                        sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: 0.5,
                        }}
                      >
                        <widget.icon
                          sx={{
                            fontSize: 20,
                            color: 'text.secondary',
                          }}
                        />
                        <Typography
                          variant="caption"
                          sx={{ fontSize: '12px', textAlign: 'center' }}
                        >
                          {widget.label}
                        </Typography>
                      </Box>
                    </CardContent>
                    {widget.hasVariants && variantCount > 1 && (
                      <VariantBadge>{variantCount}</VariantBadge>
                    )}
                  </WidgetCard>
                )
              })}
            </WidgetGrid>
          </Collapse>
        </Box>
      ))}

      <VariantPickerPopover
        anchorEl={variantAnchor}
        widget={variantWidget}
        onClose={handleCloseVariantPicker}
        onSelect={handleVariantSelect}
      />
    </PaletteContainer>
  )
}

export { parseWidgetType, getWidgetDefinition, ALL_WIDGET_TYPES }
