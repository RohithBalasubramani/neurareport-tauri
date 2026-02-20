const MAX_INTENT_STACK = 100
let intentStack = []

export const pushActiveIntent = (intent) => {
  if (!intent) return
  intentStack = [...intentStack, intent].slice(-MAX_INTENT_STACK)
}

export const popActiveIntent = (intentId) => {
  if (!intentStack.length) return
  if (!intentId) {
    intentStack = []
    return
  }
  intentStack = intentStack.filter((item) => item?.id !== intentId)
}

export const getActiveIntent = () => (
  intentStack.length ? intentStack[intentStack.length - 1] : null
)
