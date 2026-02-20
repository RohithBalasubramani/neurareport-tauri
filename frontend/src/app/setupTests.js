// Set act environment flag for React 19
globalThis.IS_REACT_ACT_ENVIRONMENT = true

import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

const createMemoryStorage = () => {
  const store = new Map()
  return {
    getItem: (key) => (store.has(String(key)) ? store.get(String(key)) : null),
    setItem: (key, value) => {
      store.set(String(key), String(value))
    },
    removeItem: (key) => {
      store.delete(String(key))
    },
    clear: () => {
      store.clear()
    },
    key: (index) => Array.from(store.keys())[index] ?? null,
    get length() {
      return store.size
    },
  }
}

if (
  typeof globalThis.localStorage === 'undefined'
  || typeof globalThis.localStorage?.getItem !== 'function'
  || typeof globalThis.localStorage?.setItem !== 'function'
) {
  globalThis.localStorage = createMemoryStorage()
}

afterEach(cleanup)
