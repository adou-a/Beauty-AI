// Temporary submit-flow mock. No backend request is made.
const delayMs = 600

function mockError(status, code, message) {
  const error = new Error(message)
  error.status = status
  error.code = code
  return error
}

export async function sendMessage(sessionId, message) {
  await new Promise(resolve => setTimeout(resolve, delayMs))

  switch (message) {
    case '__MOCK_FAIL_422__':
      throw mockError(422, 'invalid_request', 'Invalid request')
    case '__MOCK_FAIL_503__':
      throw mockError(503, 'service_unavailable', 'Service temporarily unavailable')
    case '__MOCK_FAIL_500__':
      throw mockError(500, 'internal_error', 'Internal server error')
    case '__MOCK_NETWORK_ERROR__':
      throw mockError(null, 'network_error', 'Network request failed')
    case '__MOCK_INVALID_RESPONSE__':
      throw mockError(200, 'invalid_response', 'Invalid answer response')
    default:
      return `Mock answer (session ${sessionId}): ${message}`
  }
}
