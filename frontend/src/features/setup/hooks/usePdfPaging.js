import { useState } from 'react'

/**
 * Manages PDF page selection state: selectedPage, pageCount
 */
export default function usePdfPaging() {
  const [selectedPage, setSelectedPage] = useState(0)
  const [pageCount, setPageCount] = useState(1)

  return { selectedPage, setSelectedPage, pageCount, setPageCount }
}
