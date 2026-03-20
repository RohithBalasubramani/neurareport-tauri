import { useState } from 'react'

/**
 * Manages template metadata form fields: tplName, tplDesc, tplTags
 */
export default function useTemplateFormFields() {
  const [tplName, setTplName] = useState('New Template')
  const [tplDesc, setTplDesc] = useState('')
  const [tplTags, setTplTags] = useState('')

  return { tplName, setTplName, tplDesc, setTplDesc, tplTags, setTplTags }
}
