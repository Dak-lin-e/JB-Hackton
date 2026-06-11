import type { ReactNode } from 'react'
import type { RiskLevel } from '../../types'

interface BadgeProps {
  children: ReactNode
  tone?: 'blue' | 'green' | 'amber' | 'red' | 'slate'
}

const toneClasses = {
  blue: 'bg-blue-50 text-blue-700 ring-blue-200',
  green: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  amber: 'bg-amber-50 text-amber-700 ring-amber-200',
  red: 'bg-rose-50 text-rose-700 ring-rose-200',
  slate: 'bg-slate-100 text-slate-700 ring-slate-200',
}

export function Badge({ children, tone = 'slate' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${toneClasses[tone]}`}>
      {children}
    </span>
  )
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  const tone = level === '높음' ? 'red' : level === '보통' ? 'amber' : 'green'
  return <Badge tone={tone}>{level}</Badge>
}
