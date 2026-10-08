import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { ReactNode } from 'react'
import { Card, EmptyState } from '../../components/Ui'
import { label } from '../../lib/format'

type Result = Record<string, unknown>
type Point = Record<string, string | number>

const colors = ['#4f46e5', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff', '#eef2ff']

function chartData(value: unknown, key: string): Point[] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return []
  return Object.entries(value).map(([name, amount]) => ({
    name: label(name),
    [key]: typeof amount === 'number' ? amount : 0,
  }))
}

function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return <Card><h2 className="font-bold">{title}</h2><div className="mt-4 h-64">{children}</div></Card>
}

function NoChart({ message = 'Not enough data to show this chart yet.' }: { message?: string }) {
  return <EmptyState title={message} />
}

export function DashboardCharts({ analysis, result }: { analysis: string; result: Result }) {
  if (analysis === 'overview') {
    return <div className="grid gap-5 sm:grid-cols-2"><MetricCard label="Deep work" value={`${result.deep_work_minutes ?? 0} min`} /><MetricCard label="Distraction" value={`${result.distraction_minutes ?? 0} min`} /><MetricCard label="Career output" value={`${result.career_units ?? 0} units`} /><MetricCard label="Prayer completion" value={`${result.prayer_completion_percent ?? 0}%`} /></div>
  }
  if (analysis === 'time-leaks') {
    const data = chartData(result.by_category, 'minutes')
    return <ChartCard title="Which distractions took the most time?">{data.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data} layout="vertical" margin={{ left: 20, right: 12 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} /><XAxis type="number" /><YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 12 }} /><Tooltip /><Bar dataKey="minutes" fill="#f59e0b" radius={[0, 5, 5, 0]} /></BarChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'best-worst-days') {
    const data = Array.isArray(result.days) ? result.days as Point[] : []
    return <ChartCard title="How did your daily scores change?">{data.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={data} margin={{ left: 4, right: 12 }}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(value: string) => value.slice(5)} /><YAxis domain={[0, 100]} /><Tooltip /><Line type="monotone" dataKey="score" stroke="#4f46e5" strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'focus-by-time') {
    const data = chartData(result.by_hour, 'focus')
    return <ChartCard title="When was focus strongest?">{data.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 5]} /><Tooltip /><Bar dataKey="focus" fill="#4f46e5" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'prayers') {
    const data = chartData(result.by_prayer, 'completion')
    return <ChartCard title="What was the completion rate by prayer?">{data.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 100]} /><Tooltip formatter={(value) => `${value}%`} /><Bar dataKey="completion" fill="#64748b" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'career-output') {
    const data = chartData(result.by_type, 'units')
    return <ChartCard title="Where did your output go?">{data.length ? <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="units" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>{data.map((entry, index) => <Cell key={entry.name} fill={colors[index % colors.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'weekday-weekend') {
    const weekday = result.weekday as Record<string, unknown> | undefined
    const weekend = result.weekend as Record<string, unknown> | undefined
    const data = weekday && weekend ? [{ name: 'Weekday', minutes: Number(weekday.deep_work_minutes ?? 0) }, { name: 'Weekend', minutes: Number(weekend.deep_work_minutes ?? 0) }] : []
    return <ChartCard title="How did deep work compare by day type?">{data.some((item) => item.minutes > 0) ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="minutes" fill="#4f46e5" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'trends') {
    const data = Array.isArray(result.daily_deep_work) ? result.daily_deep_work as Point[] : []
    return <ChartCard title="How did daily deep work trend?">{data.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(value: string) => value.slice(5)} /><YAxis /><Tooltip /><Line type="monotone" dataKey="minutes" stroke="#4f46e5" strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer> : <NoChart />}</ChartCard>
  }
  if (analysis === 'sleep-focus') {
    return <ChartCard title="How does sleep relate to focus?"><div className="flex h-full flex-col items-center justify-center text-center"><ScatterChart width={280} height={180}><XAxis type="number" dataKey="sleep_minutes" name="Sleep" hide /><YAxis type="number" dataKey="focus" name="Focus" hide /><Scatter data={Array.isArray(result.points) ? result.points : []} fill="#4f46e5" /></ScatterChart><p className="text-sm text-slate-500">{String(result.label ?? 'correlation, not causation')}</p><p className="mt-1 font-semibold">Correlation: {result.correlation === null ? 'Not enough data' : String(result.correlation)}</p></div></ChartCard>
  }
  if (analysis === 'deep-work') {
    return <div className="grid gap-5 sm:grid-cols-2"><MetricCard label="Total deep work" value={`${result.total_minutes ?? 0} min`} /><MetricCard label="Average session" value={`${result.average_session_minutes ?? 0} min`} /><MetricCard label="Longest session" value={`${result.longest_session_minutes ?? 0} min`} /><MetricCard label="Average focus" value={`${result.average_focus ?? '—'} / 5`} /></div>
  }
  return <NoChart />
}

function MetricCard({ label: name, value }: { label: string; value: string }) {
  return <Card><p className="text-sm text-slate-500">{name}</p><p className="mt-2 text-2xl font-bold">{value}</p></Card>
}
