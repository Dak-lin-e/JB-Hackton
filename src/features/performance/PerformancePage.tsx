import { BarChart3, Clock, LineChart, MousePointerClick, TrendingUp } from 'lucide-react'
import { Badge } from '../../shared/components/Badge'

const upcomingItems = [
  {
    title: '채널별 실성과 연동',
    description: 'Instagram, YouTube, TikTok 광고 지표를 캠페인 단위로 연결할 예정입니다.',
    icon: LineChart,
  },
  {
    title: 'CTR·전환율 자동 분석',
    description: '노출, 조회, 클릭, 저장, 댓글, 가입 데이터를 기반으로 성과를 계산합니다.',
    icon: MousePointerClick,
  },
  {
    title: '다음 캠페인 개선안',
    description: '성과가 좋은 훅, 이미지 톤, CTA 구조를 다음 광고안에 반영합니다.',
    icon: TrendingUp,
  },
]

export function PerformancePage() {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <Badge tone="blue">Coming Soon</Badge>
            <h2 className="mt-4 text-3xl font-bold text-slate-950">성과 분석은 곧 연결됩니다</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              현재는 광고 기획, 이미지 생성, 리스크 점검 워크플로우에 집중하고 있습니다.
              실제 집행 데이터 연동이 준비되면 이 화면에서 광고안별 성과와 다음 캠페인 개선 전략을 확인할 수 있습니다.
            </p>
          </div>
          <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-lg bg-cyan-50 text-cyan-700">
            <BarChart3 size={40} />
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {upcomingItems.map(({ title, description, icon: Icon }) => (
          <article key={title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <Icon className="text-cyan-700" size={24} />
            <h3 className="mt-4 font-bold text-slate-950">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
          </article>
        ))}
      </section>

      <section className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6">
        <div className="flex items-start gap-3">
          <Clock className="mt-0.5 text-slate-500" size={20} />
          <div>
            <h3 className="font-bold text-slate-950">예정된 데이터 입력</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              노출 수, 조회 수, 클릭 수, 저장 수, 댓글 수, 가입 수를 실제 캠페인 결과로 받아 CTR, 전환율, 참여율을 계산할 예정입니다.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
