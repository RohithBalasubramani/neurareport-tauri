import { useInteraction } from '@/components/ux/governance'
import TemplateChatCreateContainer from '@/features/templates/containers/TemplateChatCreateContainer'

export default function TemplateChatCreatePage() {
  useInteraction()
  return <TemplateChatCreateContainer />
}
