import { Bot, X } from 'lucide-react'
import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { AssistantPanel } from './AssistantPanel'
import { Header } from './Header'
import { MobileNav } from './MobileNav'
import { Sidebar } from './Sidebar'

export function AppLayout() {
  const [isAssistantOpen, setIsAssistantOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex">
        <Sidebar />
        <div className="min-w-0 flex-1">
          <Header />
          <MobileNav />
          <main className="grid gap-5 p-4 xl:grid-cols-[minmax(0,1fr)_340px] md:p-6">
            <div className="min-w-0">
              <Outlet />
            </div>
            <AssistantPanel className="hidden xl:block" />
          </main>
        </div>
      </div>
      <button
        type="button"
        onClick={() => setIsAssistantOpen((value) => !value)}
        className="fixed bottom-4 right-4 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-slate-950 text-white shadow-lg xl:hidden"
        aria-label={isAssistantOpen ? 'AI 기획자 보조 닫기' : 'AI 기획자 보조 열기'}
      >
        {isAssistantOpen ? <X size={21} /> : <Bot size={21} />}
      </button>
      {isAssistantOpen && (
        <div className="fixed inset-x-3 bottom-20 z-40 xl:hidden">
          <AssistantPanel className="max-h-[72vh] overflow-hidden" />
        </div>
      )}
    </div>
  )
}
