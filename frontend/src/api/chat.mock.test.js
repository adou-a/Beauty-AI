import assert from 'node:assert/strict'
import test from 'node:test'
import { sendMessage } from './chat.mock.js'

test('success returns the passed session and message without a backend request', async () => {
  const originalFetch = globalThis.fetch
  let fetchCount = 0
  globalThis.fetch = () => { fetchCount += 1; throw new Error('unexpected fetch') }
  try {
    const start = performance.now()
    const answer = await sendMessage('session-test-123', 'hello')
    assert.equal(answer, 'Mock answer (session session-test-123): hello')
    assert.ok(performance.now() - start >= 500)
    assert.equal(fetchCount, 0)
  } finally {
    globalThis.fetch = originalFetch
  }
})

for (const [input, status, code, message] of [
  ['__MOCK_FAIL_422__', 422, 'invalid_request', 'Invalid request'],
  ['__MOCK_FAIL_503__', 503, 'service_unavailable', 'Service temporarily unavailable'],
  ['__MOCK_FAIL_500__', 500, 'internal_error', 'Internal server error'],
  ['__MOCK_NETWORK_ERROR__', null, 'network_error', 'Network request failed'],
  ['__MOCK_INVALID_RESPONSE__', 200, 'invalid_response', 'Invalid answer response'],
]) {
  test(`${input} rejects with the API-layer error shape`, async () => {
    await assert.rejects(sendMessage('session-test-123', input), error => {
      assert.ok(error instanceof Error)
      assert.equal(error.status, status)
      assert.equal(error.code, code)
      assert.equal(error.message, message)
      return true
    })
  })
}
