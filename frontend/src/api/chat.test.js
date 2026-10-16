import assert from 'node:assert/strict'
import test from 'node:test'
import { sendMessage } from './chat.js'

test('invalid answer contract returns invalid_response', async () => {
    const originalFetch = globalThis.fetch

    globalThis.fetch = async () => ({
        ok: true,
        status: 200,
        json: async () => ({
            result: 'This is not an answer field'
        })
    })

    try {
        await assert.rejects(
            sendMessage('test-session', 'hello'),
            error => {
                assert.equal(error.status, 200)
                assert.equal(error.code, 'invalid_response')
                assert.equal(error.message, 'Invalid answer response')
                return true
            }
        )
    } finally {
        globalThis.fetch = originalFetch
    }
})

test('invalid JSON returns invalid_response', async () => {
    const originalFetch = globalThis.fetch

    globalThis.fetch = async () => ({
        ok: true,
        status: 200,
        json: async () => {
            throw new SyntaxError('Invalid JSON')
        }
    })

    try {
        await assert.rejects(
            sendMessage('test-session', 'hello'),
            error => {
                assert.equal(error.status, 200)
                assert.equal(error.code, 'invalid_response')
                assert.equal(error.message, 'Invalid JSON response')
                return true
            }
        )
    } finally {
        globalThis.fetch = originalFetch
    }
})