import { CheckCircle2, Hash } from 'lucide-react'
import type { TrendPattern } from '../../../types'
import { Badge } from '../../../shared/components/Badge'

interface TrendPatternCardProps {
  pattern: TrendPattern
  selected?: boolean
  onSelect?: (pattern: TrendPattern) => void
}

export function TrendPatternCard({ pattern, selected = false, onSelect }: TrendPatternCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(pattern)}
      className={`h-full rounded-lg border bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${
        selected ? 'border-cyan-500 ring-2 ring-cyan-100' : 'border-slate-200'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
          <Hash size={19} />
        </div>
        {selected && <CheckCircle2 className="text-cyan-600" size={20} />}
      </div>
      <h3 className="mt-4 text-base font-bold text-slate-950">{pattern.title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{pattern.description}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {pattern.tags.map((tag) => (
          <Badge key={tag} tone="blue">
            {tag}
          </Badge>
        ))}
      </div>
    </button>
  )
}
