const templatePickerInstances = new Set()
let activeTemplatePickerRoot = null

const hideTemplatePickerRoot = (node) => {
  if (!node) return
  node.setAttribute('aria-hidden', 'true')
  node.setAttribute('data-template-picker-hidden', 'true')
  node.setAttribute('hidden', 'true')
  node.inert = true
}

const showTemplatePickerRoot = (node) => {
  if (!node) return
  node.removeAttribute('aria-hidden')
  node.removeAttribute('data-template-picker-hidden')
  node.removeAttribute('hidden')
  node.inert = false
}

const activateTemplatePickerRoot = (node) => {
  if (!node || activeTemplatePickerRoot === node) return
  if (activeTemplatePickerRoot) {
    hideTemplatePickerRoot(activeTemplatePickerRoot)
  }
  showTemplatePickerRoot(node)
  activeTemplatePickerRoot = node
}

const activateFallbackTemplatePicker = () => {
  const iterator = templatePickerInstances.values().next()
  if (!iterator.done) {
    activateTemplatePickerRoot(iterator.value)
    return
  }
  activeTemplatePickerRoot = null
}

export const registerTemplatePickerRoot = (node) => {
  if (!node) return () => {}
  templatePickerInstances.add(node)
  activateTemplatePickerRoot(node)

  return () => {
    if (activeTemplatePickerRoot === node) {
      showTemplatePickerRoot(node)
      templatePickerInstances.delete(node)
      activeTemplatePickerRoot = null
      activateFallbackTemplatePicker()
      return
    }
    if (node) {
      templatePickerInstances.delete(node)
      showTemplatePickerRoot(node)
    }
  }
}
