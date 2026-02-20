import { useInteraction } from '@/components/ux/governance'
import WidgetsPageContainer from '@/features/widgets/containers/WidgetsPageContainer'

export default function WidgetsPage() {
  useInteraction()
  return <WidgetsPageContainer />
}
