import { BarChart3, Camera, Clapperboard, Home, Megaphone, Sparkles } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: '대시보드', icon: Home },
  { to: '/trend-video-lab', label: 'YouTube 전용 광고 생성하기', icon: Clapperboard },
  { to: '/instagram-trend-lab', label: 'instagram 전용 광고 생성하기', icon: Camera },
  { to: '/campaign/result', label: '결과 스튜디오', icon: Megaphone },
  { to: '/performance', label: '성과 분석', icon: BarChart3 },
]

export function Sidebar() {
  return (
    <aside className="sticky top-0 hidden h-screen w-72 shrink-0 border-r border-slate-200 bg-white px-5 py-6 lg:block">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-950 text-white">
          <Sparkles size={22} />
        </div>
        <div>
          <p className="text-sm font-semibold text-cyan-700">디지털 마케팅 AI Agent</p>
          <h1 className="text-lg font-bold leading-tight text-slate-950">Trend-to-FinAd Agent</h1>
        </div>
      </div>

      <nav className="mt-9 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                isActive ? 'bg-slate-950 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="absolute bottom-6 left-5 right-5 rounded-lg border border-cyan-100 bg-cyan-50 p-4">
        <p className="text-sm font-bold text-slate-950">리스크 우선 점검</p>
        <p className="mt-1 text-xs leading-5 text-slate-600">
          트렌디한 문구도 금융광고 리스크 기준을 먼저 통과하도록 설계합니다.
        </p>
      </div>
    </aside>
  )
}
