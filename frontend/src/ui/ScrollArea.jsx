import { forwardRef, useRef, useEffect, useImperativeHandle, useCallback } from 'react'
import { Box } from '@mui/material'

const ScrollArea = forwardRef(function ScrollArea(
  {
    children,
    autoScroll = false,
    onScroll,
    maxHeight,
    sx,
    ...props
  },
  ref
) {
  const containerRef = useRef(null)
  const isAtBottomRef = useRef(true)

  useImperativeHandle(ref, () => ({
    scrollToBottom: (behavior = 'smooth') => {
      if (containerRef.current) {
        containerRef.current.scrollTo({
          top: containerRef.current.scrollHeight,
          behavior,
        })
      }
    },
    scrollToTop: (behavior = 'smooth') => {
      if (containerRef.current) {
        containerRef.current.scrollTo({ top: 0, behavior })
      }
    },
    getScrollContainer: () => containerRef.current,
  }))

  const handleScroll = useCallback(
    (e) => {
      const el = e.target
      const threshold = 100
      isAtBottomRef.current =
        el.scrollHeight - el.scrollTop - el.clientHeight < threshold
      onScroll?.(e)
    },
    [onScroll]
  )

  // Auto-scroll on content changes when user is at bottom
  useEffect(() => {
    if (!autoScroll || !containerRef.current) return

    const observer = new MutationObserver(() => {
      if (isAtBottomRef.current && containerRef.current) {
        containerRef.current.scrollTo({
          top: containerRef.current.scrollHeight,
          behavior: 'smooth',
        })
      }
    })

    observer.observe(containerRef.current, {
      childList: true,
      subtree: true,
      characterData: true,
    })

    return () => observer.disconnect()
  }, [autoScroll])

  return (
    <Box
      ref={containerRef}
      onScroll={handleScroll}
      sx={{
        flex: 1,
        overflow: 'auto',
        maxHeight,
        scrollBehavior: 'smooth',
        '&::-webkit-scrollbar': {
          width: 8,
          height: 8,
        },
        '&::-webkit-scrollbar-track': {
          bgcolor: 'transparent',
        },
        '&::-webkit-scrollbar-thumb': {
          bgcolor: 'divider',
          borderRadius: 4,
          '&:hover': {
            bgcolor: 'action.disabled',
          },
        },
        ...(sx || {}),
      }}
      {...props}
    >
      {children}
    </Box>
  )
})

export default ScrollArea
