import { ApiError } from './errors'
import type {
  Activity,
  AnalyticsResponse,
  CareerOutput,
  CareerOutputType,
  Distraction,
  DistractionCategory,
  Prayer,
  PrayerLog,
  PrayerStatus,
  Session,
  SleepLog,
  Today,
} from './types'

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!response.ok) {
    let payload: unknown
    try {
      payload = await response.json()
    } catch {
      throw new Error(`Request failed with status ${response.status}`)
    }
    if (
      typeof payload === 'object' &&
      payload !== null &&
      'error' in payload &&
      typeof payload.error === 'object'
    ) {
      throw new ApiError(payload as { error: { code: string; message: string; details?: Record<string, unknown> | null; request_id: string } }, response.status)
    }
    throw new Error(`Request failed with status ${response.status}`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

const json = (body: unknown): RequestInit => ({
  method: 'POST',
  body: JSON.stringify(body),
})

export const api = {
  today: () => request<Today>('/today'),
  startSession: (activity: Activity) => request<Session>('/sessions/start', json({ activity })),
  stopSession: (id: number, focus_score: number, deep_work?: boolean) =>
    request<Session>(`/sessions/${id}/stop`, json({ focus_score, deep_work })),
  createSession: (
    activity: Activity,
    start_time: string,
    end_time: string,
    focus_score?: number,
  ) =>
    request<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify({ activity, start_time, end_time, focus_score }),
    }),
  deleteSession: (id: number) =>
    request<void>(`/sessions/${id}`, { method: 'DELETE' }),
  startDistraction: (category: DistractionCategory) =>
    request<Distraction>('/distractions/start', json({ category })),
  stopDistraction: (id: number) =>
    request<Distraction>(`/distractions/${id}/stop`, { method: 'POST' }),
  logDistraction: (category: DistractionCategory, minutes: number) =>
    request<Distraction>('/distractions', json({ category, minutes })),
  createDistraction: (category: DistractionCategory, start_time: string, end_time: string) =>
    request<Distraction>('/distractions', {
      method: 'POST',
      body: JSON.stringify({ category, start_time, end_time }),
    }),
  deleteDistraction: (id: number) =>
    request<void>(`/distractions/${id}`, { method: 'DELETE' }),
  updatePrayer: (date: string, prayer: Prayer, status: PrayerStatus) =>
    request<PrayerLog>(`/prayers/${date}/${prayer}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    }),
  deletePrayer: (date: string, prayer: Prayer) =>
    request<void>(`/prayers/${date}/${prayer}`, { method: 'DELETE' }),
  logCareerOutput: (type: CareerOutputType) =>
    request<CareerOutput>('/career-output', json({ type, count: 1 })),
  logSleep: (sleep_start: string, wake_time: string) =>
    request<SleepLog>('/sleep', json({ sleep_start, wake_time })),
  sessions: () => request<Session[]>('/sessions'),
  distractions: () => request<Distraction[]>('/distractions'),
  prayers: () => request<PrayerLog[]>('/prayers'),
  careerOutput: () => request<CareerOutput[]>('/career-output'),
  sleep: () => request<SleepLog[]>('/sleep'),
  analytics: (kind: string, range = '30d') =>
    request<AnalyticsResponse>(`/analytics/${kind}?range=${range}`),
  exportData: () => request<Record<string, unknown>>('/export'),
  deleteData: () => request<void>('/data?confirm=true', { method: 'DELETE' }),
}
