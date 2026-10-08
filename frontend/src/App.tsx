import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { BrowserRouter, NavLink, Route, Routes, useSearchParams } from 'react-router-dom'
import { BarChart3, Check, Clock3, Download, Home, Menu, Moon, Play, Settings, Square, Trash2, X } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Toaster, toast } from 'sonner'
import { api } from './api/client'
import { getErrorMessage } from './api/errors'
import type { Activity, DistractionCategory, Prayer, PrayerStatus } from './api/types'
import { Button, Card, EmptyState, ErrorState } from './components/Ui'
import { DashboardCharts } from './features/analytics/DashboardCharts'
import { duration, friendlyDate, label, localTime } from './lib/format'

const activities: Activity[] = ['DSA', 'PROJECT', 'JOB_APPLICATION', 'INTERVIEW_PREP', 'LEARNING', 'OTHER']
const distractions: DistractionCategory[] = ['YOUTUBE', 'INSTAGRAM', 'GAMING', 'RANDOM_BROWSING', 'PHONE', 'OTHER']
const prayers: Prayer[] = ['FAJR', 'DHUHR', 'ASR', 'MAGHRIB', 'ISHA']
const careerTypes = [
  ['DSA_PROBLEMS', 'DSA problem'],
  ['APPLICATIONS', 'Application'],
  ['PROJECT_WORK', 'Project work'],
  ['INTERVIEW', 'Interview'],
  ['MOCK_INTERVIEW', 'Mock interview'],
] as const

function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false)
  const links = [
    { to: '/', label: 'Today', icon: Home },
    { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { to: '/history', label: 'History', icon: Clock3 },
    { to: '/settings', label: 'Settings', icon: Settings },
  ]
  return (
    <div className="min-h-screen bg-[#f7f8fc] text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <NavLink to="/" className="text-lg font-bold tracking-tight">steady<span className="text-indigo-600">.</span></NavLink>
          <button className="rounded-lg p-2 md:hidden" aria-label="Open navigation" onClick={() => setMenuOpen(!menuOpen)}><Menu size={22} /></button>
          <nav className="hidden gap-1 md:flex">{links.map(({ to, label: name, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-500 hover:bg-slate-50'}`}><Icon size={17} />{name}</NavLink>)}</nav>
        </div>
        {menuOpen && <nav className="grid gap-1 border-t border-slate-100 px-4 py-3 md:hidden">{links.map(({ to, label: name, icon: Icon }) => <NavLink onClick={() => setMenuOpen(false)} key={to} to={to} className="flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium text-slate-600"><Icon size={18} />{name}</NavLink>)}</nav>}
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6 pb-24"><Routes><Route path="/" element={<TodayPage />} /><Route path="/dashboard" element={<DashboardPage />} /><Route path="/history" element={<HistoryPage />} /><Route path="/settings" element={<SettingsPage />} /></Routes></main>
      <Toaster position="top-center" richColors />
    </div>
  )
}

function TodayPage() {
  const queryClient = useQueryClient()
  const today = useQuery({ queryKey: ['today'], queryFn: api.today, refetchInterval: 30_000 })
  const [focusOpen, setFocusOpen] = useState(false)
  const [focus, setFocus] = useState(4)
  const mutation = useMutation({
    mutationFn: async (action: () => Promise<unknown>) => action(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['today'] }),
    onError: (error) => toast.error(getErrorMessage(error)),
  })
  if (today.isLoading) return <Loading />
  if (today.isError || !today.data) return <ErrorState message={getErrorMessage(today.error)} onRetry={() => today.refetch()} />
  const data = today.data
  const stop = () => {
    if (!data.active_session) return
    mutation.mutate(() => api.stopSession(data.active_session!.id, focus))
    setFocusOpen(false)
  }
  return (
    <div className="space-y-6">
      <div><p className="text-sm font-medium text-indigo-600">Your day, at a glance</p><h1 className="mt-1 text-3xl font-bold tracking-tight">Today</h1><p className="mt-1 text-slate-500">{friendlyDate(data.date)}</p></div>
      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <SectionTitle title="Work session" subtitle={data.active_session ? 'In progress' : 'What are you working on?'} />
          {data.active_session ? <div className="mt-5 rounded-xl bg-indigo-50 p-4"><div className="flex items-center justify-between"><div><p className="font-semibold text-indigo-950">{label(data.active_session.activity)}</p><LiveTimer start={data.active_session.start_time} /></div><Button variant="danger" onClick={() => setFocusOpen(true)}><span className="flex items-center gap-2"><Square size={16} fill="currentColor" />Stop</span></Button></div></div> : <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3">{activities.map((activity) => <QuickButton key={activity} label={label(activity)} icon={<Play size={14} />} onClick={() => mutation.mutate(() => api.startSession(activity))} />)}</div>}
          {focusOpen && <div className="mt-4 rounded-xl border border-indigo-200 bg-white p-4"><div className="flex items-center justify-between"><p className="font-semibold">How focused was it?</p><button aria-label="Close focus rating" onClick={() => setFocusOpen(false)}><X size={18} /></button></div><div className="mt-3 grid grid-cols-5 gap-2">{[1, 2, 3, 4, 5].map((score) => <button key={score} onClick={() => setFocus(score)} className={`min-h-12 rounded-xl font-bold ${focus === score ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'}`}>{score}</button>)}</div><Button className="mt-3 w-full" loading={mutation.isPending} onClick={stop}>Save session</Button></div>}
        </Card>
        <DistractionCard active={data.active_distraction} mutate={mutation.mutate} pending={mutation.isPending} />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <Card><SectionTitle title="Prayers" subtitle="Log each one with one tap" /><div className="mt-4 grid grid-cols-5 gap-2">{prayers.map((prayer) => <PrayerButton key={prayer} prayer={prayer} status={data.prayers[prayer]} date={data.date} mutate={mutation.mutate} />)}</div></Card>
        <Card><SectionTitle title="Today's totals" subtitle="Small steps add up" /><div className="mt-5 grid grid-cols-3 gap-3 text-center"><Metric label="Work" value={duration(data.totals.work_minutes)} /><Metric label="Distraction" value={duration(data.totals.distraction_minutes)} /><Metric label="Outputs" value="Add below" /></div><div className="mt-5 flex flex-wrap gap-2">{careerTypes.map(([type, name]) => <button key={type} className="rounded-full bg-slate-100 px-3 py-2 text-sm font-medium hover:bg-indigo-50" onClick={() => mutation.mutate(() => api.logCareerOutput(type))}>+1 {name}</button>)}</div></Card>
      </div>
      <SleepCard mutate={mutation.mutate} pending={mutation.isPending} />
    </div>
  )
}

function DistractionCard({ active, mutate, pending }: { active: import('./api/types').Distraction | null; mutate: (action: () => Promise<unknown>) => void; pending: boolean }) {
  const [category, setCategory] = useState<DistractionCategory>('YOUTUBE')
  const [minutes, setMinutes] = useState(15)
  return <Card><SectionTitle title="Distraction" subtitle={active ? `Started at ${localTime(active.start_time)}` : 'Log it without friction'} />{active ? <div className="mt-5 flex items-center justify-between rounded-xl bg-amber-50 p-4"><div><p className="font-semibold">{label(active.category)}</p><LiveTimer start={active.start_time} /></div><Button variant="danger" loading={pending} onClick={() => mutate(() => api.stopDistraction(active.id))}>Stop</Button></div> : <><div className="mt-4 flex flex-wrap gap-2">{distractions.map((item) => <button key={item} onClick={() => setCategory(item)} className={`rounded-full px-3 py-2 text-sm font-medium ${category === item ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-600'}`}>{label(item)}</button>)}</div><div className="mt-4 flex items-center gap-2"><select aria-label="Past distraction minutes" className="min-h-11 rounded-xl border border-slate-200 bg-white px-3" value={minutes} onChange={(event) => setMinutes(Number(event.target.value))}>{[10, 15, 30, 60].map((value) => <option key={value} value={value}>{value} minutes</option>)}</select><Button loading={pending} onClick={() => mutate(() => api.logDistraction(category, minutes))}>Log past</Button></div></>}</Card>
}

function PrayerButton({ prayer, status, date, mutate }: { prayer: Prayer; status: PrayerStatus | null; date: string; mutate: (action: () => Promise<unknown>) => void }) {
  const next: PrayerStatus | null = status === null ? 'completed' : status === 'completed' ? 'missed' : null
  return <button aria-label={`${label(prayer)}: ${status ?? 'not logged'}`} onClick={() => { if (status === 'missed') mutate(() => api.deletePrayer(date, prayer)); else mutate(() => api.updatePrayer(date, prayer, next ?? 'completed')) }} className={`min-h-16 rounded-xl border text-xs font-semibold ${status === 'completed' ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : status === 'missed' ? 'border-amber-200 bg-amber-50 text-amber-800' : 'border-slate-200 bg-slate-50 text-slate-500'}`}><span className="mb-1 block text-lg">{status === 'completed' ? <Check className="mx-auto" size={18} /> : status === 'missed' ? '—' : '·'}</span>{label(prayer)}</button>
}

function SleepCard({ mutate, pending }: { mutate: (action: () => Promise<unknown>) => void; pending: boolean }) {
  const [start, setStart] = useState('22:30')
  const [wake, setWake] = useState('06:30')
  const submit = () => { const today = new Date(); const [sh, sm] = start.split(':').map(Number); const [wh, wm] = wake.split(':').map(Number); const wakeDate = new Date(today); wakeDate.setHours(wh, wm, 0, 0); const startDate = new Date(wakeDate); startDate.setDate(startDate.getDate() - (wh > sh ? 1 : 0)); startDate.setHours(sh, sm, 0, 0); mutate(() => api.logSleep(startDate.toISOString(), wakeDate.toISOString())) }
  return <Card><SectionTitle title="Sleep" subtitle="Log last night's rest" /><div className="mt-4 flex flex-wrap items-end gap-3"><label className="text-sm font-medium text-slate-600">Sleep time<input type="time" className="mt-1 block min-h-11 rounded-xl border border-slate-200 px-3" value={start} onChange={(e) => setStart(e.target.value)} /></label><label className="text-sm font-medium text-slate-600">Wake time<input type="time" className="mt-1 block min-h-11 rounded-xl border border-slate-200 px-3" value={wake} onChange={(e) => setWake(e.target.value)} /></label><Button loading={pending} onClick={submit}><span className="flex items-center gap-2"><Moon size={16} />Save sleep</span></Button></div></Card>
}

function DashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [analysis, setAnalysis] = useState(searchParams.get('analysis') ?? 'overview')
  const [range, setRange] = useState(searchParams.get('range') ?? '30d')
  const query = useQuery({ queryKey: ['analytics', analysis, range], queryFn: () => api.analytics(analysis, range) })
  const updateFilter = (nextAnalysis: string, nextRange: string) => {
    setAnalysis(nextAnalysis)
    setRange(nextRange)
    setSearchParams({ analysis: nextAnalysis, range: nextRange })
  }
  return <div className="space-y-6"><div><p className="text-sm font-medium text-indigo-600">Patterns, not pressure</p><h1 className="mt-1 text-3xl font-bold">Dashboard</h1></div><Card><div className="grid gap-3 sm:grid-cols-2"><label className="text-sm font-semibold text-slate-600">What do you want to analyze?<select className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={analysis} onChange={(e) => updateFilter(e.target.value, range)}>{['overview', 'time-leaks', 'deep-work', 'best-worst-days', 'focus-by-time', 'prayers', 'career-output', 'weekday-weekend', 'sleep-focus', 'trends'].map((item) => <option key={item} value={item}>{label(item)}</option>)}</select></label><label className="text-sm font-semibold text-slate-600">Range<select className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={range} onChange={(e) => updateFilter(analysis, e.target.value)}><option value="today">Today</option><option value="7d">7 days</option><option value="30d">30 days</option></select></label></div></Card>{query.isLoading && <Loading />}{query.isError && <ErrorState message={getErrorMessage(query.error)} onRetry={() => query.refetch()} />}{query.data && <><div className="rounded-2xl border border-indigo-100 bg-indigo-50 px-5 py-4"><p className="font-semibold text-indigo-950">{query.data.data_sufficiency.message}</p><p className="mt-1 text-sm text-indigo-800">{query.data.data_sufficiency.days_with_data} days with data in this range.</p></div><DashboardCharts analysis={analysis} result={query.data.result} /></>}</div>
}

function HistoryPage() {
  const queryClient = useQueryClient()
  const sessions = useQuery({ queryKey: ['sessions'], queryFn: api.sessions })
  const distractionsQuery = useQuery({ queryKey: ['distractions'], queryFn: api.distractions })
  const [showForm, setShowForm] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)
  const deleteMutation = useMutation({
    mutationFn: async (entry: { kind: 'session' | 'distraction'; id: number }) =>
      entry.kind === 'session' ? api.deleteSession(entry.id) : api.deleteDistraction(entry.id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['sessions'] })
      void queryClient.invalidateQueries({ queryKey: ['distractions'] })
      toast.success('Entry deleted.')
      setDeleting(null)
    },
    onError: (error) => {
      toast.error(getErrorMessage(error))
      setDeleting(null)
    },
  })
  if (sessions.isLoading || distractionsQuery.isLoading) return <Loading />
  if (sessions.isError || distractionsQuery.isError) return <ErrorState message={getErrorMessage(sessions.error ?? distractionsQuery.error)} onRetry={() => { void sessions.refetch(); void distractionsQuery.refetch() }} />
  const entries = [
    ...(sessions.data ?? []).map((item) => ({
      key: `session-${item.id}`,
      kind: 'session' as const,
      id: item.id,
      date: item.start_time,
      title: label(item.activity),
      meta: `${duration(item.duration_minutes)} · work session`,
    })),
    ...(distractionsQuery.data ?? []).map((item) => ({
      key: `distraction-${item.id}`,
      kind: 'distraction' as const,
      id: item.id,
      date: item.start_time,
      title: label(item.category),
      meta: `${duration(item.duration_minutes)} · distraction`,
    })),
  ].sort((a, b) => b.date.localeCompare(a.date))
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div><h1 className="text-3xl font-bold">History</h1><p className="mt-1 text-slate-500">Review or correct recent entries.</p></div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? 'Close form' : '+ Add missed entry'}</Button>
      </div>
      {showForm && <ManualEntryForm onSaved={() => { setShowForm(false); void queryClient.invalidateQueries({ queryKey: ['sessions'] }); void queryClient.invalidateQueries({ queryKey: ['distractions'] }) }} />}
      <Card>
        {entries.length === 0 ? <EmptyState title="No entries yet. Start logging from Today." /> : <div className="divide-y divide-slate-100">{entries.slice(0, 50).map((entry) => <div key={entry.key} className="flex items-center justify-between gap-3 py-4"><div><p className="font-semibold">{entry.title}</p><p className="text-sm text-slate-500">{new Date(entry.date).toLocaleDateString()} · {entry.meta}</p></div><div className="flex items-center gap-3"><Clock3 size={18} className="text-slate-400" /><button aria-label={`Delete ${entry.title}`} className="rounded-lg p-2 text-slate-400 hover:bg-rose-50 hover:text-rose-600" onClick={() => { if (window.confirm('Delete this entry?')) { setDeleting(entry.key); deleteMutation.mutate({ kind: entry.kind, id: entry.id }) } }} disabled={deleting === entry.key}><Trash2 size={17} /></button></div></div>)}</div>}
      </Card>
      <p className="text-center text-xs text-slate-400">Existing records can be deleted. To correct a record, delete it and add a new missed entry.</p>
    </div>
  )
}

function ManualEntryForm({ onSaved }: { onSaved: () => void }) {
  const [kind, setKind] = useState<'session' | 'distraction'>('session')
  const [activity, setActivity] = useState<Activity>('PROJECT')
  const [category, setCategory] = useState<DistractionCategory>('YOUTUBE')
  const [start, setStart] = useState(() => localDateTimeValue(new Date(Date.now() - 60 * 60 * 1000)))
  const [end, setEnd] = useState(() => localDateTimeValue(new Date()))
  const [focus, setFocus] = useState(4)
  const mutation = useMutation({
    mutationFn: async (): Promise<unknown> => kind === 'session'
      ? api.createSession(activity, new Date(start).toISOString(), new Date(end).toISOString(), focus)
      : api.createDistraction(category, new Date(start).toISOString(), new Date(end).toISOString()),
    onSuccess: () => { toast.success('Entry added.'); onSaved() },
    onError: (error) => toast.error(getErrorMessage(error)),
  })
  return <Card className="border-indigo-200 bg-indigo-50/40"><div className="grid gap-4 sm:grid-cols-2"><label className="text-sm font-semibold text-slate-700">Entry type<select className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={kind} onChange={(event) => setKind(event.target.value as 'session' | 'distraction')}><option value="session">Work session</option><option value="distraction">Distraction</option></select></label>{kind === 'session' ? <label className="text-sm font-semibold text-slate-700">Activity<select className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={activity} onChange={(event) => setActivity(event.target.value as Activity)}>{activities.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select></label> : <label className="text-sm font-semibold text-slate-700">Category<select className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={category} onChange={(event) => setCategory(event.target.value as DistractionCategory)}>{distractions.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select></label>}<label className="text-sm font-semibold text-slate-700">Started<input type="datetime-local" className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={start} onChange={(event) => setStart(event.target.value)} /></label><label className="text-sm font-semibold text-slate-700">Ended<input type="datetime-local" className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={end} onChange={(event) => setEnd(event.target.value)} /></label>{kind === 'session' && <label className="text-sm font-semibold text-slate-700">Focus score<select className="mt-1 min-h-11 w-full rounded-xl border border-slate-200 bg-white px-3" value={focus} onChange={(event) => setFocus(Number(event.target.value))}>{[1, 2, 3, 4, 5].map((item) => <option key={item} value={item}>{item} / 5</option>)}</select></label>}</div><Button className="mt-4" loading={mutation.isPending} onClick={() => mutation.mutate()}>Save missed entry</Button></Card>
}

function localDateTimeValue(value: Date): string {
  const offset = value.getTimezoneOffset()
  return new Date(value.getTime() - offset * 60 * 1000).toISOString().slice(0, 16)
}

function SettingsPage() {
  const [confirm, setConfirm] = useState('')
  const exportMutation = useMutation({ mutationFn: api.exportData, onSuccess: (data) => { const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'personal-analytics-export.json'; anchor.click(); URL.revokeObjectURL(url) }, onError: (error) => toast.error(getErrorMessage(error)) })
  const deleteMutation = useMutation({ mutationFn: api.deleteData, onSuccess: () => { toast.success('All data was deleted.'); setConfirm('') }, onError: (error) => toast.error(getErrorMessage(error)) })
  return <div className="space-y-6"><div><h1 className="text-3xl font-bold">Settings</h1><p className="mt-1 text-slate-500">Keep control of your data.</p></div><Card><h2 className="font-bold">Export data</h2><p className="mt-1 text-sm text-slate-500">Download all records as a JSON file.</p><Button className="mt-4" loading={exportMutation.isPending} onClick={() => exportMutation.mutate()}><span className="flex items-center gap-2"><Download size={16} />Download export</span></Button></Card><Card className="border-rose-200"><h2 className="font-bold text-rose-800">Delete all data</h2><p className="mt-1 text-sm text-slate-500">This cannot be undone. Type DELETE to enable the action.</p><div className="mt-4 flex flex-wrap gap-2"><input aria-label="Type DELETE to confirm" className="min-h-11 rounded-xl border border-slate-200 px-3" value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="DELETE" /><Button variant="danger" disabled={confirm !== 'DELETE'} loading={deleteMutation.isPending} onClick={() => deleteMutation.mutate()}><span className="flex items-center gap-2"><Trash2 size={16} />Delete everything</span></Button></div></Card></div>
}

function SectionTitle({ title, subtitle }: { title: string; subtitle: string }) { return <div><h2 className="font-bold">{title}</h2><p className="mt-1 text-sm text-slate-500">{subtitle}</p></div> }
function Metric({ label: name, value }: { label: string; value: string }) { return <div className="rounded-xl bg-slate-50 p-3"><p className="text-xs font-medium text-slate-500">{name}</p><p className="mt-1 text-lg font-bold">{value}</p></div> }
function QuickButton({ label: name, icon, onClick }: { label: string; icon: ReactNode; onClick: () => void }) { return <button onClick={onClick} className="flex min-h-12 items-center justify-center gap-2 rounded-xl bg-slate-100 px-3 text-sm font-semibold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700">{icon}{name}</button> }
function LiveTimer({ start }: { start: string }) { const [now, setNow] = useState(() => Date.now()); useEffect(() => { const timer = window.setInterval(() => setNow(Date.now()), 1000); return () => window.clearInterval(timer) }, []); return <p className="mt-1 font-mono text-xl text-indigo-700">{duration((now - new Date(start).getTime()) / 60000)}</p> }
function Loading() { return <div className="flex min-h-40 items-center justify-center text-slate-400"><Clock3 className="animate-pulse" /></div> }

export default function App() { return <BrowserRouter><AppShell /></BrowserRouter> }
