import { useState, useCallback, useRef } from 'react'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'

function detectFormat(file) {
  if (!file?.name) return null
  const name = file.name.toLowerCase()
  if (name.endsWith('.pdf')) return 'PDF'
  if (name.endsWith('.xlsx') || name.endsWith('.xls')) return 'Excel'
  return 'Unknown'
}

const ACCEPTED_FORMATS = new Set(['PDF', 'Excel'])

const isSupportedTemplateFile = (file) => {
  if (!file) return false
  return ACCEPTED_FORMATS.has(detectFormat(file))
}

/**
 * Manages file upload state: file, pendingFileAction, uploadProgress, preview
 * Also provides file-handling callbacks.
 */
export default function useFileUpload({ resetVerification, resetPaging, inputRef }) {
  const setSetupStep = useAppStore((state) => state.setSetupStep)
  const setTemplateKind = useAppStore((state) => state.setTemplateKind)
  const toast = useToast()

  const [file, setFile] = useState(null)
  const [pendingFileAction, setPendingFileAction] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [preview, setPreview] = useState(null)

  const hasInProgressSetupRef = useRef(false)

  const resetFileState = useCallback(
    () => {
      setFile(null)
      setPreview(null)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    },
    [inputRef],
  )

  const resetVerificationState = useCallback(
    (options = {}) => {
      resetVerification()
      setPreview(null)
      if (options.clearFile) {
        setFile(null)
        if (resetPaging) resetPaging()
        if (inputRef.current) {
          inputRef.current.value = ''
        }
      }
    },
    [resetVerification, resetPaging, inputRef],
  )

  const applySelectedFile = useCallback(
    (selectedFile) => {
      if (!selectedFile) return
      if (!isSupportedTemplateFile(selectedFile)) {
        toast.show('Unsupported file type. Please upload a PDF or Excel design.', 'warning')
        return
      }
      resetVerificationState({ clearFile: true })
      const detected = detectFormat(selectedFile)
      const nextKind = detected === 'Excel' ? 'excel' : 'pdf'
      setTemplateKind(nextKind)
      setFile(selectedFile)
      setSetupStep('upload')
    },
    [resetVerificationState, setSetupStep, setTemplateKind, toast],
  )

  const clearFile = useCallback(() => {
    if (hasInProgressSetupRef.current) {
      setPendingFileAction({ action: 'remove', file: null })
      return
    }
    resetVerificationState({ clearFile: true })
  }, [resetVerificationState])

  return {
    file,
    setFile,
    pendingFileAction,
    setPendingFileAction,
    uploadProgress,
    setUploadProgress,
    preview,
    setPreview,
    hasInProgressSetupRef,
    resetFileState,
    resetVerificationState,
    applySelectedFile,
    clearFile,
  }
}
