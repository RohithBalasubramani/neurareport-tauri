export const getSourceMeta = (source) => {
  const normalized = String(source || '').toLowerCase()
  if (normalized === 'starter') {
    return {
      label: 'Starter',
      color: 'secondary',
      variant: 'outlined',
      isStarter: true,
    }
  }
  return {
    label: 'Company',
    color: 'default',
    variant: 'outlined',
    isStarter: false,
  }
}

export default getSourceMeta
