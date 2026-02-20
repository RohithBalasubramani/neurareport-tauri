import { useInteraction } from '@/components/ux/governance'
import SearchPageContainer from '@/features/search/containers/SearchPageContainer'

export default function SearchPage() {
  useInteraction()
  return <SearchPageContainer />
}
