import { useInteraction } from '@/components/ux/governance'
import IngestionPageContainer from '@/features/ingestion/containers/IngestionPageContainer'

export default function IngestionPage() {
  useInteraction()
  return <IngestionPageContainer />
}
