import { useInteraction } from '@/components/ux/governance'
import AgentsPageContainer from '@/features/agents/containers/AgentsPageContainer'

export default function AgentsPage() {
  useInteraction()
  return <AgentsPageContainer />
}
