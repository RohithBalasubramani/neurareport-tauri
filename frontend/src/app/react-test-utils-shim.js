// React 19 compatibility shim for react-dom/test-utils
// React 19 moved `act` from react-dom/test-utils to react directly
// This shim provides backwards compatibility for libraries that still import from react-dom/test-utils

import { act } from 'react'

// Re-export act from react (React 19 location)
export { act }

// Simulate object stub for compatibility (deprecated in React 19)
export const Simulate = new Proxy(
  {},
  {
    get: (target, prop) => {
      return (element, eventData) => {
        const eventName = prop.toLowerCase()
        const event = new Event(eventName, { bubbles: true, cancelable: true })
        Object.assign(event, eventData)
        element.dispatchEvent(event)
      }
    },
  }
)

// Default export for CommonJS compatibility
export default { act, Simulate }
