/**
 * Sidebar state and interaction hooks
 */
import { useCallback, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '../../stores'

export function useSidebarNavigation(onClose) {
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()

  const handleNavigate = useCallback((path, label) => {
    const resolvedLabel = label || `Open ${path}`
    navigate(path, {
      label: resolvedLabel,
      intent: { source: 'sidebar', path },
    })
    onClose?.()
  }, [navigate, onClose])

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'sidebar', ...intent },
      action,
    })
  }, [execute])

  return { handleNavigate, executeUI }
}

export function useSidebarSections(executeUI) {
  const [expandedSections, setExpandedSections] = useState({
    Data: true,
    'AI Assistant': true,
    Create: true,
    Admin: false,
  })

  const handleToggleSection = useCallback((section) => {
    const isExpanded = expandedSections[section] !== false
    const nextLabel = isExpanded ? 'Collapse' : 'Expand'
    return executeUI(
      `${nextLabel} ${section} section`,
      () => setExpandedSections(prev => ({
        ...prev,
        [section]: !prev[section],
      })),
      { section, expanded: !isExpanded }
    )
  }, [executeUI, expandedSections])

  return { expandedSections, handleToggleSection }
}

export function useSidebarControls(executeUI, collapsed, onToggle, onClose) {
  const handleToggleSidebar = useCallback(() => {
    return executeUI(
      collapsed ? 'Expand sidebar' : 'Collapse sidebar',
      () => onToggle?.(),
      { collapsed: !collapsed }
    )
  }, [executeUI, collapsed, onToggle])

  const handleCloseSidebar = useCallback(() => {
    return executeUI('Close sidebar', () => onClose?.())
  }, [executeUI, onClose])

  return { handleToggleSidebar, handleCloseSidebar }
}

export function useSidebarActiveState() {
  const location = useLocation()

  const activeJobs = useAppStore((s) => {
    const jobs = s.jobs || []
    return jobs.filter((j) => j.status === 'running' || j.status === 'pending').length
  })

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/dashboard'
    }
    return location.pathname.startsWith(path)
  }

  return { isActive, activeJobs }
}
