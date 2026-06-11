import { BarChart3, FileText, FlaskConical, Megaphone, RefreshCw, ShieldCheck, Sparkles } from 'lucide-react'

const workflowSteps = [
  { label: '금융상품 입력', icon: FileText },
  { label: 'SNS 트렌드 패턴 분석', icon: Sparkles },
  { label: '광고 콘텐츠 생성', icon: Megaphone },
  { label: '금융광고 리스크 점검', icon: ShieldCheck },
  { label: 'A/B 테스트', icon: FlaskConical },
  { label: '성과 분석', icon: BarChart3 },
  { label: '다음 캠페인 개선', icon: RefreshCw },
]

export function AgentWorkflow() {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <p className="text-sm font-semibold text-cyan-700">에이전트 워크플로우</p>
        <h2 className="mt-1 text-xl font-bold text-slate-950">캠페인 제작부터 개선까지 이어지는 작업 흐름</h2>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-2 2xl:grid-cols-7">
        {workflowSteps.map((step, index) => {
          const Icon = step.icon
          return (
            <div key={step.label} className="relative rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-cyan-700 shadow-sm">
                <Icon size={20} />
              </div>
              <p className="mt-4 text-xs font-semibold text-slate-400">{String(index + 1).padStart(2, '0')}</p>
              <h3 className="mt-1 text-sm font-bold leading-6 text-slate-950">{step.label}</h3>
            </div>
          )
        })}
      </div>
    </section>
  )
}
