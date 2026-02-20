import { useInteraction } from '@/components/ux/governance'
import KnowledgePageContainer from '@/features/knowledge/containers/KnowledgePageContainer'

export default function KnowledgePage() {
  useInteraction()
  return <KnowledgePageContainer />
}
