import { describe, expect, it } from 'vitest'
import { duration, label } from './format'

describe('format helpers', () => {
  it('formats enum labels for readable UI text', () => {
    expect(label('JOB_APPLICATION')).toBe('Job Application')
    expect(label('PROJECT')).toBe('Project')
  })

  it('formats durations without unnecessary zero units', () => {
    expect(duration(0)).toBe('0m')
    expect(duration(45)).toBe('45m')
    expect(duration(135)).toBe('2h 15m')
    expect(duration(null)).toBe('—')
  })
})
