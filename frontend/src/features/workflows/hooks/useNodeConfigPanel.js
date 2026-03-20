import { useState, useCallback, useMemo } from 'react'
import { NODE_TYPES } from '../components/NodeConfigPanel.styles'

/**
 * Custom hook for NodeConfigPanel state and callbacks.
 */
export function useNodeConfigPanel({ node, onChange }) {
  const [expandedSections, setExpandedSections] = useState(['basic', 'config'])

  const nodeTypeInfo = useMemo(() =>
    node ? NODE_TYPES[node.type] || NODE_TYPES.action : null,
    [node]
  )

  const handleChange = useCallback((key, value) => {
    onChange?.({ ...node, [key]: value })
  }, [node, onChange])

  const handleConfigChange = useCallback((config) => {
    onChange?.({ ...node, config })
  }, [node, onChange])

  const toggleSection = useCallback((section) => {
    setExpandedSections((prev) =>
      prev.includes(section)
        ? prev.filter((s) => s !== section)
        : [...prev, section]
    )
  }, [])

  const insertVariable = useCallback((varName) => {
    navigator.clipboard.writeText(`{{${varName}}}`)
  }, [])

  return {
    expandedSections,
    nodeTypeInfo,
    handleChange,
    handleConfigChange,
    toggleSection,
    insertVariable,
  }
}
