import type { ApiErrorPayload } from './types'

export class ApiError extends Error {
  readonly code: string
  readonly details: Record<string, unknown> | null
  readonly requestId: string
  readonly status: number

  constructor(payload: ApiErrorPayload, status: number) {
    super(payload.error.message)
    this.name = 'ApiError'
    this.code = payload.error.code
    this.details = payload.error.details ?? null
    this.requestId = payload.error.request_id
    this.status = status
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) return error.message
  if (error instanceof TypeError) return "Can't reach the server. Check that the backend is running."
  return 'Something went wrong. Please try again.'
}
