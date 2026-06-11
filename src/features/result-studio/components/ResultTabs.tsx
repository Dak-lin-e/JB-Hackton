import type { ResultTab, ResultTabId } from '../types'

const tabs: ResultTab[] = [
  { id: 'concept', label: '광고 콘셉트' },
  { id: 'production', label: '영상/이미지 기획안' },
  { id: 'shorts', label: '릴스/쇼츠/틱톡' },
  { id: 'cardNews', label: '카드뉴스' },
  { id: 'risk', label: '리스크 점검' },
  { id: 'abTest', label: 'A/B 테스트' },
]

interface ResultTabsProps {
  activeTab: ResultTabId
  onChange: (tab: ResultTabId) => void
}

export function ResultTabs({ activeTab, onChange }: ResultTabsProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
      <div className="flex min-w-max gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={`rounded-lg px-4 py-2.5 text-sm font-bold transition ${
              activeTab === tab.id ? 'bg-slate-950 text-white' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  )
}
