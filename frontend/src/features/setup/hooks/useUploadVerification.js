import { useState, useCallback } from 'react'
import { useAppStore } from '@/stores'

/**
 * Manages verification-related state:
 * verified, verifying, queueingVerify, queuedJobId,
 * verifyModalOpen, verifyProgress, verifyStage, verifyLog
 */
export default function useUploadVerification() {
  const setVerifyArtifacts = useAppStore((state) => state.setVerifyArtifacts)
  const setHtmlUrls = useAppStore((state) => state.setHtmlUrls)
  const setTemplateId = useAppStore((state) => state.setTemplateId)
  const setCacheKey = useAppStore((state) => state.setCacheKey)

  const [verified, setVerified] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [queueingVerify, setQueueingVerify] = useState(false)
  const [queuedJobId, setQueuedJobId] = useState(null)
  const [verifyModalOpen, setVerifyModalOpen] = useState(false)
  const [verifyProgress, setVerifyProgress] = useState(0)
  const [verifyStage, setVerifyStage] = useState('Idle')
  const [verifyLog, setVerifyLog] = useState([])

  const resetVerification = useCallback(
    () => {
      setVerified(false)
      setVerifyStage('Idle')
      setVerifyProgress(0)
      setVerifyLog([])
      setVerifyArtifacts(null)
      setHtmlUrls({ template: null, final: null, llm2: null })
      setTemplateId(null)
      setCacheKey(Date.now())
      setQueuedJobId(null)
      setQueueingVerify(false)
    },
    [setCacheKey, setHtmlUrls, setTemplateId, setVerifyArtifacts],
  )

  return {
    verified,
    setVerified,
    verifying,
    setVerifying,
    queueingVerify,
    setQueueingVerify,
    queuedJobId,
    setQueuedJobId,
    verifyModalOpen,
    setVerifyModalOpen,
    verifyProgress,
    setVerifyProgress,
    verifyStage,
    setVerifyStage,
    verifyLog,
    setVerifyLog,
    resetVerification,
  }
}
