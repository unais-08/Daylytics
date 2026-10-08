import type { ButtonHTMLAttributes, PropsWithChildren, ReactNode } from 'react'
import { LoaderCircle } from 'lucide-react'

export function Card({ children, className = '' }: PropsWithChildren<{ className?: string }>) {
  return <section className={`rounded-2xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</section>
}

export function Button({
  children,
  loading = false,
  variant = 'primary',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean; variant?: 'primary' | 'secondary' | 'danger' }) {
  const styles = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700',
    secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200',
    danger: 'bg-rose-600 text-white hover:bg-rose-700',
  }
  return (
    <button {...props} disabled={loading || props.disabled} className={`min-h-11 rounded-xl px-4 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${props.className ?? ''}`}>
      {loading ? <LoaderCircle className="mx-auto animate-spin" size={18} /> : children}
    </button>
  )
}

export function EmptyState({ title, action }: { title: string; action?: ReactNode }) {
  return <div className="rounded-xl bg-slate-50 p-8 text-center text-slate-500"><p>{title}</p>{action && <div className="mt-4">{action}</div>}</div>
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="rounded-xl border border-rose-200 bg-rose-50 p-5 text-rose-800"><p>{message}</p><button className="mt-3 font-semibold underline" onClick={onRetry}>Try again</button></div>
}
