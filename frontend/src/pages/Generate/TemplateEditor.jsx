import { useInteraction } from '@/components/ux/governance'
import TemplateEditorContainer from '@/features/generate/containers/TemplateEditor'

export default function TemplateEditor() {
  useInteraction()
  return <TemplateEditorContainer />
}
