import type { ABTestIdea } from '../../../types'
import { Badge } from '../../../shared/components/Badge'

export function ABTestCard({ idea }: { idea: ABTestIdea }) {
  const tone = idea.variant === 'A안' ? 'blue' : idea.variant === 'B안' ? 'green' : 'amber'

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <Badge tone={tone}>{idea.variant}</Badge>
          <h3 className="mt-3 text-lg font-bold text-slate-950">{idea.title}</h3>
        </div>
      </div>
      <dl className="mt-4 space-y-3 text-sm">
        <div>
          <dt className="font-semibold text-slate-950">첫 3초 훅</dt>
          <dd className="mt-1 text-slate-600">{idea.hook}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-950">핵심 메시지</dt>
          <dd className="mt-1 text-slate-600">{idea.message}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-950">예상 반응</dt>
          <dd className="mt-1 text-slate-600">{idea.expectedReaction}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-950">추천 채널</dt>
          <dd className="mt-1 text-slate-600">{idea.channel}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-950">장점</dt>
          <dd className="mt-1 text-slate-600">{idea.strength}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-950">주의점</dt>
          <dd className="mt-1 text-slate-600">{idea.caution}</dd>
        </div>
      </dl>
    </article>
  )
}
