export type Activity =
  | 'DSA'
  | 'PROJECT'
  | 'JOB_APPLICATION'
  | 'INTERVIEW_PREP'
  | 'LEARNING'
  | 'OTHER'

export type DistractionCategory =
  | 'YOUTUBE'
  | 'INSTAGRAM'
  | 'GAMING'
  | 'RANDOM_BROWSING'
  | 'PHONE'
  | 'OTHER'

export type Prayer = 'FAJR' | 'DHUHR' | 'ASR' | 'MAGHRIB' | 'ISHA'
export type PrayerStatus = 'completed' | 'missed'
export type CareerOutputType =
  | 'DSA_PROBLEMS'
  | 'PROJECT_WORK'
  | 'APPLICATIONS'
  | 'INTERVIEW'
  | 'MOCK_INTERVIEW'

export interface Session {
  id: number
  activity: Activity
  start_time: string
  end_time: string | null
  deep_work: boolean | null
  focus_score: number | null
  duration_minutes: number | null
}

export interface Distraction {
  id: number
  category: DistractionCategory
  start_time: string
  end_time: string | null
  duration_minutes: number | null
}

export interface Today {
  date: string
  active_session: Session | null
  active_distraction: Distraction | null
  prayers: Record<Prayer, PrayerStatus | null>
  totals: Record<string, number>
}

export interface PrayerLog {
  id: number
  date: string
  prayer: Prayer
  status: PrayerStatus
}

export interface CareerOutput {
  id: number
  logged_at: string
  type: CareerOutputType
  count: number
  note: string | null
}

export interface SleepLog {
  id: number
  sleep_start: string
  wake_time: string
}

export interface ApiErrorPayload {
  error: {
    code: string
    message: string
    details?: Record<string, unknown> | null
    request_id: string
  }
}

export interface AnalyticsResponse {
  analysis: string
  range: { name: string; start_date: string; end_date: string }
  data_sufficiency: {
    days_with_data: number
    level: string
    message: string
  }
  result: Record<string, unknown>
}
