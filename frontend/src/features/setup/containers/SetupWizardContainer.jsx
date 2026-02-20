import { useState, useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Stack } from '@mui/material'
import { WizardLayout } from '@/layouts'
import { useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import StepConnection from '../components/steps/StepConnection'
import StepTemplate from '../components/steps/StepTemplate'
import StepMapping from '../components/steps/StepMapping'
import ReportGlossaryNotice from '@/components/ux/ReportGlossaryNotice.jsx'

const WIZARD_STORAGE_KEY = 'neurareport_wizard_state'

const saveWizardState = (state) => {
  try {
    sessionStorage.setItem(WIZARD_STORAGE_KEY, JSON.stringify(state))
  } catch (e) {
    // Ignore storage errors
  }
}

const loadWizardState = () => {
  try {
    const stored = sessionStorage.getItem(WIZARD_STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch (e) {
    return null
  }
}

const clearWizardState = () => {
  try {
    sessionStorage.removeItem(WIZARD_STORAGE_KEY)
  } catch (e) {
    // Ignore storage errors
  }
}

const WIZARD_STEPS = [
  {
    key: 'connection',
    label: 'Connect Data Source',
    description: 'Select or create a data source for reports',
  },
  {
    key: 'template',
    label: 'Upload Report Design',
    description: 'Upload a PDF or Excel design',
  },
  {
    key: 'mapping',
    label: 'Map Fields',
    description: 'Match design fields to data columns (no SQL required)',
  },
]

const STEP_MAP = { connection: 0, template: 1, mapping: 2 }
const STEP_KEYS = ['connection', 'template', 'mapping']

export default function SetupWizard() {
  const navigate = useNavigateInteraction()
  const [searchParams, setSearchParams] = useSearchParams()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'setup-wizard', ...intent } }),
    [navigate]
  )
  const toast = useToast()
  const [loading, setLoading] = useState(false)

  // Get step from URL or default to 0
  const stepParam = searchParams.get('step') || 'connection'
  const [currentStep, setCurrentStep] = useState(() => STEP_MAP[stepParam] ?? 0)

  // Load wizard state from sessionStorage on mount
  const [wizardState, setWizardState] = useState(() => {
    const stored = loadWizardState()
    return stored || {
      connectionId: null,
      templateId: null,
      templateKind: 'pdf',
      mapping: null,
      keys: [],
    }
  })

  const activeConnection = useAppStore((s) => s.activeConnection)
  const templateId = useAppStore((s) => s.templateId)

  // Persist wizard state to sessionStorage whenever it changes
  useEffect(() => {
    saveWizardState(wizardState)
  }, [wizardState])

  // Update URL when step changes
  useEffect(() => {
    setSearchParams((prev) => {
      const newParams = new URLSearchParams(prev)
      newParams.set('step', STEP_KEYS[currentStep])
      return newParams
    }, { replace: true })
  }, [currentStep, setSearchParams])

  const updateWizardState = useCallback((updates) => {
    setWizardState((prev) => ({ ...prev, ...updates }))
  }, [])

  const handleNext = useCallback(() => {
    if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1)
    }
  }, [currentStep])

  const handlePrev = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1)
    }
  }, [currentStep])

  const handleComplete = useCallback(() => {
    clearWizardState()
    toast.show('Report design ready. You can run it from Reports.', 'success')
    handleNavigate('/reports', 'Open reports')
  }, [handleNavigate, toast])

  const handleCancel = useCallback(() => {
    clearWizardState()
    handleNavigate('/', 'Exit wizard')
  }, [handleNavigate])

  const getStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <StepConnection
            wizardState={wizardState}
            updateWizardState={updateWizardState}
            onComplete={handleNext}
            setLoading={setLoading}
          />
        )
      case 1:
        return (
          <StepTemplate
            wizardState={wizardState}
            updateWizardState={updateWizardState}
            onComplete={handleNext}
            setLoading={setLoading}
          />
        )
      case 2:
        return (
          <StepMapping
            wizardState={wizardState}
            updateWizardState={updateWizardState}
            onComplete={handleComplete}
            setLoading={setLoading}
          />
        )
      default:
        return null
    }
  }

  const isNextDisabled = () => {
    switch (currentStep) {
      case 0:
        return !wizardState.connectionId && !activeConnection?.id
      case 1:
        return !wizardState.templateId && !templateId
      case 2:
        return false
      default:
        return false
    }
  }

  return (
    <WizardLayout
      title="Set Up Report Design"
      subtitle="Connect your data source and prepare a report design for runs"
      steps={WIZARD_STEPS}
      currentStep={currentStep}
      onNext={handleNext}
      onPrev={handlePrev}
      onComplete={handleComplete}
      onCancel={handleCancel}
      nextDisabled={isNextDisabled()}
      loading={loading}
    >
      <Stack spacing={2}>
        <ReportGlossaryNotice dense showChips={false} />
        {getStepContent()}
      </Stack>
    </WizardLayout>
  )
}
