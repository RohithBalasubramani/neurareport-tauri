import { useInteraction } from '@/components/ux/governance'
import DesignPageContainer from '@/features/design/containers/DesignPageContainer'

export default function DesignPage() {
  useInteraction()
  return <DesignPageContainer />
}
