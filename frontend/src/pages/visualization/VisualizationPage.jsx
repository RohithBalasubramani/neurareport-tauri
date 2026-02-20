import { useInteraction } from '@/components/ux/governance'
import VisualizationPageContainer from '@/features/visualization/containers/VisualizationPageContainer'

export default function VisualizationPage() {
  useInteraction()
  return <VisualizationPageContainer />
}
