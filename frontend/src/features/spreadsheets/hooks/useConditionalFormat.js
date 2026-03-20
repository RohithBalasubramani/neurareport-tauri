/**
 * Hook for managing conditional formatting state and actions.
 */
import { useState, useCallback } from 'react'
import { secondary, primary } from '@/app/theme'

// Rule types and conditions (shared constants)
export const RULE_TYPES = [
  { value: 'cell_value', label: 'Cell Value' },
  { value: 'text_contains', label: 'Text Contains' },
  { value: 'date', label: 'Date' },
  { value: 'top_bottom', label: 'Top/Bottom Values' },
  { value: 'above_below_avg', label: 'Above/Below Average' },
  { value: 'duplicate', label: 'Duplicate Values' },
  { value: 'unique', label: 'Unique Values' },
  { value: 'blank', label: 'Blank/Non-Blank' },
  { value: 'formula', label: 'Custom Formula' },
  { value: 'color_scale', label: 'Color Scale' },
  { value: 'data_bar', label: 'Data Bar' },
  { value: 'icon_set', label: 'Icon Set' },
]

export const CONDITIONS = {
  cell_value: [
    { value: 'greater_than', label: 'Greater than' },
    { value: 'less_than', label: 'Less than' },
    { value: 'equal_to', label: 'Equal to' },
    { value: 'not_equal', label: 'Not equal to' },
    { value: 'between', label: 'Between' },
    { value: 'not_between', label: 'Not between' },
  ],
  text_contains: [
    { value: 'contains', label: 'Contains' },
    { value: 'not_contains', label: 'Does not contain' },
    { value: 'begins_with', label: 'Begins with' },
    { value: 'ends_with', label: 'Ends with' },
  ],
  date: [
    { value: 'yesterday', label: 'Yesterday' },
    { value: 'today', label: 'Today' },
    { value: 'tomorrow', label: 'Tomorrow' },
    { value: 'last_7_days', label: 'Last 7 days' },
    { value: 'this_week', label: 'This week' },
    { value: 'this_month', label: 'This month' },
  ],
  top_bottom: [
    { value: 'top_n', label: 'Top N values' },
    { value: 'bottom_n', label: 'Bottom N values' },
    { value: 'top_percent', label: 'Top N%' },
    { value: 'bottom_percent', label: 'Bottom N%' },
  ],
  blank: [
    { value: 'is_blank', label: 'Is blank' },
    { value: 'not_blank', label: 'Is not blank' },
  ],
}

export const PRESET_STYLES = [
  { label: 'Red Fill', fill: secondary.rose[100], text: secondary.rose[700] },
  { label: 'Green Fill', fill: secondary.emerald[100], text: secondary.emerald[700] },
  { label: 'Yellow Fill', fill: secondary.stone[100], text: secondary.stone[700] },
  { label: 'Blue Fill', fill: secondary.cyan[100], text: secondary.cyan[700] },
  { label: 'Orange Fill', fill: primary[100], text: secondary.stone[600] },
  { label: 'Purple Fill', fill: secondary.violet[100], text: secondary.violet[700] },
]

export function getRuleDescription(rule) {
  const typeLabel = RULE_TYPES.find((t) => t.value === rule.type)?.label || rule.type
  const conditions = CONDITIONS[rule.type] || []
  const condLabel = conditions.find((c) => c.value === rule.condition)?.label || rule.condition

  if (['duplicate', 'unique'].includes(rule.type)) return typeLabel
  if (['color_scale', 'data_bar', 'icon_set'].includes(rule.type)) return typeLabel
  if (rule.condition === 'between') return `${condLabel} ${rule.value1} and ${rule.value2}`
  return `${condLabel} ${rule.value1 || ''}`
}

export function useConditionalFormat({ rules, onRulesChange }) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState(null)
  const [expandedRules, setExpandedRules] = useState([])

  const handleAddRule = useCallback(() => {
    setEditingRule(null)
    setDialogOpen(true)
  }, [])

  const handleEditRule = useCallback((rule) => {
    setEditingRule(rule)
    setDialogOpen(true)
  }, [])

  const handleSaveRule = useCallback((rule) => {
    if (rule.id) {
      onRulesChange?.(rules.map((r) => (r.id === rule.id ? rule : r)))
    } else {
      onRulesChange?.([...rules, { ...rule, id: `rule_${Date.now()}` }])
    }
    setDialogOpen(false)
  }, [rules, onRulesChange])

  const handleDeleteRule = useCallback((ruleId) => {
    onRulesChange?.(rules.filter((r) => r.id !== ruleId))
  }, [rules, onRulesChange])

  const handleToggleRule = useCallback((ruleId) => {
    onRulesChange?.(
      rules.map((r) => (r.id === ruleId ? { ...r, enabled: !r.enabled } : r))
    )
  }, [rules, onRulesChange])

  const toggleRuleExpansion = useCallback((ruleId) => {
    setExpandedRules((prev) =>
      prev.includes(ruleId)
        ? prev.filter((id) => id !== ruleId)
        : [...prev, ruleId]
    )
  }, [])

  return {
    dialogOpen,
    editingRule,
    expandedRules,
    setDialogOpen,
    handleAddRule,
    handleEditRule,
    handleSaveRule,
    handleDeleteRule,
    handleToggleRule,
    toggleRuleExpansion,
  }
}
