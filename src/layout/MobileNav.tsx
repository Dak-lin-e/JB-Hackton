import { BarChart3, Camera, Clapperboard, Home, Megaphone } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: '대시보드', icon: Home },
  { to: '/trend-video-lab', label: 'YouTube', icon: Clapperboard },
  { to: '/instagram-trend-lab', label: '인스타', icon: Camera },
  { to: '/campaign/result', label: '결과', icon: Megaphone },
  { to: '/performance', label: '성과', icon: BarChart3 },
]

export function MobileNav() {
  return (
    <nav className="flex gap-2 overflow-x-auto border-b border-slate-200 bg-white px-4 py-3 lg:hidden">
      {navItems.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `inline-flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-bold ${
              isActive ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-700'
            }`
          }
        >
          <Icon size={15} />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
