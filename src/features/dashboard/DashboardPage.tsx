import { ArrowRight, BarChart3, Bot, CheckCircle2, LineChart, Megaphone, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { TrendPatternCard } from '../new-campaign/components/TrendPatternCard'
import { trendPatterns } from '../new-campaign/data/trends'
import { Badge } from '../../shared/components/Badge'
import { StatCard } from '../../shared/components/StatCard'
import { AgentWorkflow } from './components/AgentWorkflow'
import { featureSummaries, recentCampaigns } from './data/campaigns'

const featureIcons = [LineChart, Megaphone, ShieldCheck, Bot, BarChart3]

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl">
            <Badge tone="blue">MZ 금융 마케팅 Agent</Badge>
            <h2 className="mt-4 text-3xl font-bold tracking-normal text-slate-950">SNS 트렌드에서 금융광고 캠페인까지 한 번에 설계합니다.</h2>
            <p className="mt-3 text-base leading-7 text-slate-600">
              금융상품 정보를 입력하면 밈 패턴 기반 광고 콘텐츠, 금융광고 리스크 점검, A/B 테스트안, 성과 개선 코멘트까지 스튜디오형 워크플로우로 제공합니다.
            </p>
          </div>
          <Link to="/trend-video-lab" className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-950 px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-slate-800">
            YouTube 트렌드 기반 생성하기
            <ArrowRight size={17} />
          </Link>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="이번 주 생성 캠페인" value="42건" caption="지난주 대비 18% 증가" icon={Megaphone} />
        <StatCard title="평균 리스크 완화율" value="91%" caption="고위험 문구 자동 수정 기준" icon={ShieldCheck} />
        <StatCard title="추천 성과 개선안" value="128개" caption="CTR, 전환율, 참여율 기반" icon={LineChart} />
      </div>

      <AgentWorkflow />

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-950">최근 SNS 트렌드 패턴</h2>
          <Link to="/trend-video-lab" className="text-sm font-bold text-cyan-700">트렌드 분석하기</Link>
        </div>
        <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
          {trendPatterns.slice(0, 3).map((pattern) => (
            <TrendPatternCard key={pattern.id} pattern={pattern} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold text-slate-950">최근 생성 캠페인</h2>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          {recentCampaigns.map((campaign) => (
            <article key={campaign.name} className="rounded-lg border border-slate-200 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-bold text-slate-950">{campaign.name}</h3>
                  <p className="mt-1 text-sm text-slate-500">{campaign.product}</p>
                </div>
                <Badge tone="green">{campaign.score}점</Badge>
              </div>
              <p className="mt-4 text-sm text-slate-600">{campaign.channel}</p>
              <p className="mt-2 text-sm font-semibold text-cyan-700">{campaign.status}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-5">
        {featureSummaries.map((feature, index) => {
          const Icon = featureIcons[index]
          return (
            <div key={feature} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <Icon className="text-cyan-700" size={22} />
              <p className="mt-3 text-sm font-bold text-slate-950">{feature}</p>
              <CheckCircle2 className="mt-4 text-emerald-600" size={18} />
            </div>
          )
        })}
      </section>
    </div>
  )
}
