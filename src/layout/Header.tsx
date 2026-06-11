import { Bell, Menu, Search } from 'lucide-react'

export function Header() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 px-4 py-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-3">
        <button className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-slate-700 lg:hidden" aria-label="메뉴 열기">
          <Menu size={20} />
        </button>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold tracking-[0.18em] text-cyan-700">디지털 마케팅 AI Agent</p>
          <h2 className="truncate text-xl font-bold text-slate-950">Trend-to-FinAd Agent</h2>
        </div>
        <div className="hidden min-w-72 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500 md:flex">
          <Search size={17} />
          캠페인, 트렌드, 상품 검색
        </div>
        <button className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-slate-700" aria-label="알림">
          <Bell size={19} />
        </button>
      </div>
    </header>
  )
}
