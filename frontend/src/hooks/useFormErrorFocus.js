import { useEffect, useMemo, useRef } from 'react'

const collectErrorPaths = (errorMap, prefix = '') => {
  if (!errorMap || typeof errorMap !== 'object') return []
  return Object.entries(errorMap).flatMap(([key, value]) => {
    if (!value) return []
    const path = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'object' && 'message' in value && value.message) {
      return [path]
    }
    if (typeof value === 'object') {
      return collectErrorPaths(value, path)
    }
    return []
  })
}

const pickFirstPath = (paths, priority) => {
  if (!priority?.length) return paths[0]
  const prioritySet = new Set(priority)
  const prioritized = paths.find((path) => prioritySet.has(path))
  return prioritized ?? paths[0]
}

export function useFormErrorFocus(formState, setFocus, priority = []) {
  const { errors, isSubmitted, submitCount } = formState || {}
  const errorsKey = useMemo(() => {
    const paths = collectErrorPaths(errors)
    return {
      paths,
      signature: paths.join('|'),
    }
  }, [errors])
  const priorityKey = Array.isArray(priority) ? priority.join('|') : ''
  const lastSignatureRef = useRef(null)

  useEffect(() => {
    if (!setFocus || typeof setFocus !== 'function') return
    if (!isSubmitted && !submitCount) return
    if (!errorsKey.paths.length) return
    const target = pickFirstPath(errorsKey.paths, priority)
    if (!target) return
    const signature = `${errorsKey.signature}:${submitCount}:${priorityKey}`
    if (lastSignatureRef.current === signature) return
    try {
      setFocus(target, { shouldSelect: true })
      lastSignatureRef.current = signature
    } catch {
      // ignore if field cannot be focused (e.g., unmounted between submit and effect)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsKey, isSubmitted, submitCount, priorityKey, setFocus])
}

export default useFormErrorFocus

