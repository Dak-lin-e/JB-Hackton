import type { ReactNode } from 'react'
import { CopyButton } from './CopyButton'

interface GeneratedAdCardProps {
  title: string
  copyText?: string
  children: ReactNode
}

export function GeneratedAdCard({ title, copyText, children }: GeneratedAdCardProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-base font-bold text-slate-950">{title}</h3>
        {copyText && <CopyButton text={copyText} />}
      </div>
      <div className="mt-4 text-sm leading-7 text-slate-700">{children}</div>
    </section>
  )
}
