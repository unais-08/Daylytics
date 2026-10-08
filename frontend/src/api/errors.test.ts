import { describe, expect, it } from 'vitest'
import { ApiError, getErrorMessage, isApiError } from './errors'

describe('API errors', () => {
  it('preserves the backend code and request ID', () => {
    const error = new ApiError({
      error: {
        code: 'SESSION_ALREADY_ACTIVE',
        message: 'Stop the active session first.',
        details: { conflicting_id: 4 },
        request_id: 'request-4',
      },
    }, 409)

    expect(isApiError(error)).toBe(true)
    expect(error.code).toBe('SESSION_ALREADY_ACTIVE')
    expect(error.requestId).toBe('request-4')
    expect(getErrorMessage(error)).toBe('Stop the active session first.')
  })

  it('gives a useful message for network failures', () => {
    expect(getErrorMessage(new TypeError('Failed to fetch'))).toContain("Can't reach the server")
  })
})
