/**
 * File Upload with Progress Tracking
 *
 * This hook provides XMLHttpRequest-based file upload with progress tracking,
 * which is not natively supported by fetch().
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { fetchWithIntent } from '../api/client'

/**
 * Upload state object
 * @typedef {Object} UploadState
 * @property {boolean} uploading - Whether upload is in progress
 * @property {number} progress - Upload progress percentage (0-100)
 * @property {string|null} stage - Current stage description
 * @property {Error|null} error - Upload error if any
 * @property {boolean} cancelled - Whether upload was cancelled
 */

/**
 * Hook for uploading files with progress tracking
 *
 * @param {Object} options - Configuration options
 * @param {Function} options.onProgress - Callback for progress updates
 * @param {Function} options.onComplete - Callback when upload completes
 * @param {Function} options.onError - Callback for errors
 * @returns {Object} Upload functions and state
 *
 * @example
 * const { upload, cancel, state } = useUploadProgress({
 *   onProgress: (percent) => console.log(`${percent}% uploaded`),
 *   onComplete: (response) => console.log('Done:', response),
 *   onError: (err) => console.error('Failed:', err),
 * })
 *
 * // Start upload
 * upload('/api/upload', file, { connectionId: '123' })
 *
 * // Cancel if needed
 * cancel()
 */
export function useUploadProgress({ onProgress, onComplete, onError } = {}) {
  const [state, setState] = useState({
    uploading: false,
    progress: 0,
    stage: null,
    error: null,
    cancelled: false,
  })

  const xhrRef = useRef(null)
  const abortControllerRef = useRef(null)

  // Abort any in-flight upload when the component unmounts
  useEffect(() => {
    return () => {
      xhrRef.current?.abort()
      abortControllerRef.current?.abort()
    }
  }, [])

  const reset = useCallback(() => {
    setState({
      uploading: false,
      progress: 0,
      stage: null,
      error: null,
      cancelled: false,
    })
  }, [])

  const cancel = useCallback(() => {
    if (xhrRef.current) {
      xhrRef.current.abort()
      xhrRef.current = null
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setState(prev => ({ ...prev, uploading: false, cancelled: true, stage: 'Cancelled' }))
  }, [])

  /**
   * Upload a file with progress tracking
   *
   * @param {string} url - Upload endpoint URL
   * @param {File} file - File to upload
   * @param {Object} formFields - Additional form fields to include
   * @param {Object} options - Upload options
   * @param {Object} options.headers - Additional headers
   * @param {boolean} options.streaming - Whether to expect streaming response
   * @returns {Promise<Object>} Response data
   */
  const upload = useCallback(async (url, file, formFields = {}, options = {}) => {
    const { headers = {}, streaming = false } = options

    // Reset state
    setState({
      uploading: true,
      progress: 0,
      stage: 'Preparing upload...',
      error: null,
      cancelled: false,
    })

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhrRef.current = xhr

      // Build FormData
      const formData = new FormData()
      formData.append('file', file)
      Object.entries(formFields).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          formData.append(key, String(value))
        }
      })

      // Track upload progress
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100)
          setState(prev => ({
            ...prev,
            progress: percent,
            stage: percent < 100 ? `Uploading... ${percent}%` : 'Processing...',
          }))
          onProgress?.(percent, event.loaded, event.total)
        }
      })

      xhr.upload.addEventListener('load', () => {
        setState(prev => ({
          ...prev,
          progress: 100,
          stage: 'Processing server response...',
        }))
      })

      xhr.addEventListener('load', () => {
        xhrRef.current = null
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            setState(prev => ({
              ...prev,
              uploading: false,
              stage: 'Complete',
            }))
            onComplete?.(response)
            resolve(response)
          } catch (parseError) {
            // Response might be NDJSON - return raw text for streaming handler
            if (streaming) {
              setState(prev => ({
                ...prev,
                uploading: false,
                stage: 'Complete',
              }))
              onComplete?.(xhr.responseText)
              resolve(xhr.responseText)
            } else {
              const error = new Error('Failed to parse response')
              setState(prev => ({ ...prev, uploading: false, error, stage: 'Error' }))
              onError?.(error)
              reject(error)
            }
          }
        } else {
          let errorMessage = `Upload failed with status ${xhr.status}`
          try {
            const errorData = JSON.parse(xhr.responseText)
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch {
            // Use default error message
          }
          const error = new Error(errorMessage)
          setState(prev => ({ ...prev, uploading: false, error, stage: 'Error' }))
          onError?.(error)
          reject(error)
        }
      })

      xhr.addEventListener('error', () => {
        xhrRef.current = null
        const error = new Error('Network error during upload')
        setState(prev => ({ ...prev, uploading: false, error, stage: 'Error' }))
        onError?.(error)
        reject(error)
      })

      xhr.addEventListener('abort', () => {
        xhrRef.current = null
        const error = new Error('Upload cancelled')
        error.cancelled = true
        setState(prev => ({ ...prev, uploading: false, cancelled: true, stage: 'Cancelled' }))
        reject(error)
      })

      // Open and send request
      xhr.open('POST', url)

      // Set custom headers
      Object.entries(headers).forEach(([key, value]) => {
        xhr.setRequestHeader(key, value)
      })

      xhr.send(formData)
    })
  }, [onProgress, onComplete, onError])

  /**
   * Upload with streaming response handling (for NDJSON)
   * Uses fetch for response streaming after XMLHttpRequest upload
   *
   * @param {string} url - Upload endpoint URL
   * @param {File} file - File to upload
   * @param {Object} formFields - Additional form fields
   * @param {Object} options - Options
   * @param {Function} options.onEvent - Callback for each streamed event
   * @param {Object} options.headers - Additional headers
   * @returns {Promise<Object>} Final result event
   */
  const uploadWithStreaming = useCallback(async (url, file, formFields = {}, options = {}) => {
    const { onEvent, headers = {} } = options

    setState({
      uploading: true,
      progress: 0,
      stage: 'Preparing upload...',
      error: null,
      cancelled: false,
    })

    // Build FormData
    const formData = new FormData()
    formData.append('file', file)
    Object.entries(formFields).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, String(value))
      }
    })

    // Create abort controller
    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      // Use XMLHttpRequest-style progress tracking via fetch ReadableStream
      const response = await fetchWithIntent(url, {
        method: 'POST',
        body: formData,
        headers,
        signal: controller.signal,
      })

      if (!response.ok) {
        let errorMessage = `Upload failed with status ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // Use default error message
        }
        throw new Error(errorMessage)
      }

      setState(prev => ({
        ...prev,
        progress: 100,
        stage: 'Processing...',
      }))

      // Handle streaming response
      if (!response.body) {
        throw new Error('Response body not available')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let finalEvent = null

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        let newlineIndex
        while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
          const line = buffer.slice(0, newlineIndex).trim()
          buffer = buffer.slice(newlineIndex + 1)
          if (!line) continue

          let payload
          try {
            payload = JSON.parse(line)
          } catch {
            continue
          }

          // Update stage from event
          if (payload.stage || payload.label) {
            setState(prev => ({
              ...prev,
              stage: payload.label || payload.stage,
              progress: payload.progress ?? prev.progress,
            }))
          }

          onEvent?.(payload)

          if (payload.event === 'result') {
            finalEvent = payload
          } else if (payload.event === 'error') {
            throw new Error(payload.detail || 'Processing error')
          }
        }
      }

      setState(prev => ({
        ...prev,
        uploading: false,
        stage: 'Complete',
      }))

      abortControllerRef.current = null
      onComplete?.(finalEvent)
      return finalEvent
    } catch (err) {
      abortControllerRef.current = null
      if (err.name === 'AbortError') {
        setState(prev => ({ ...prev, uploading: false, cancelled: true, stage: 'Cancelled' }))
        const cancelError = new Error('Upload cancelled')
        cancelError.cancelled = true
        throw cancelError
      }
      setState(prev => ({ ...prev, uploading: false, error: err, stage: 'Error' }))
      onError?.(err)
      throw err
    }
  }, [onComplete, onError])

  return {
    upload,
    uploadWithStreaming,
    cancel,
    reset,
    state,
    uploading: state.uploading,
    progress: state.progress,
    stage: state.stage,
    error: state.error,
    cancelled: state.cancelled,
  }
}

export default useUploadProgress
