import assert from 'node:assert/strict'
import { describe, test } from 'node:test'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const designSrc = fs.readFileSync(
  path.resolve(__dirname, '../../src/api/design.js'),
  'utf-8'
)

describe('design API route alignment', () => {
  test('setActiveTheme calls POST /design/themes/{id}/activate', () => {
    // Verify the route path is /activate, NOT /set-active
    assert.ok(
      designSrc.includes('/activate'),
      'design.js must use /activate path for setActiveTheme'
    )
    assert.ok(
      !designSrc.includes('/set-active'),
      'design.js must NOT use /set-active (old incorrect path)'
    )
  })

  test('generateColorPalette calls POST /design/color-palette with correct body', () => {
    // Verify route path is /color-palette, NOT /colors/generate
    assert.ok(
      designSrc.includes("'/design/color-palette'"),
      'design.js must use /design/color-palette path'
    )
    assert.ok(
      !designSrc.includes('/colors/generate'),
      'design.js must NOT use /colors/generate (old incorrect path)'
    )

    // Verify body uses harmony_type, NOT scheme
    assert.ok(
      designSrc.includes('harmony_type'),
      'design.js must send harmony_type in color palette request body'
    )

    // Verify count parameter is sent
    assert.ok(
      designSrc.includes('count'),
      'design.js must send count in color palette request body'
    )
  })

  test('generateColorPalette function signature has harmonyType and count params', () => {
    // Verify function signature includes harmonyType and count
    const fnMatch = designSrc.match(
      /export async function generateColorPalette\(([^)]+)\)/
    )
    assert.ok(fnMatch, 'generateColorPalette function must exist')

    const params = fnMatch[1]
    assert.ok(
      params.includes('harmonyType'),
      `generateColorPalette params must include harmonyType, got: ${params}`
    )
    assert.ok(
      params.includes('count'),
      `generateColorPalette params must include count, got: ${params}`
    )
  })
})
