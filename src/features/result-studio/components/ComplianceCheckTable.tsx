import { RiskBadge } from '../../../shared/components/Badge'
import type { ComplianceResult, RiskLevel } from '../../../types'

const rowTone: Record<RiskLevel, string> = {
  낮음: 'border-l-emerald-400 bg-emerald-50/40',
  보통: 'border-l-amber-400 bg-amber-50/40',
  높음: 'border-l-rose-400 bg-rose-50/40',
}

interface ComplianceCheckTableProps {
  result?: ComplianceResult
}

export function ComplianceCheckTable({ result }: ComplianceCheckTableProps) {
  if (!result) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-lg font-bold text-slate-950">금융광고 리스크 점검</h3>
        <p className="mt-2 text-sm text-slate-500">YouTube 트렌드 분석에서 광고 기획안을 생성하면 결과가 표시됩니다.</p>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold text-slate-950">금융광고 리스크 점검</h3>
          <p className="mt-1 text-sm text-slate-500">생성 문구에서 주의해야 할 표현을 API 점검 결과로 표시합니다.</p>
        </div>
        <RiskBadge level={result.riskLevel} />
      </div>
      <div className="mt-5 overflow-x-auto">
        <table className="min-w-[760px] w-full border-separate border-spacing-0 text-left text-sm">
          <thead>
            <tr className="text-slate-500">
              <th className="border-b border-slate-200 pb-3 font-semibold">점검 문구</th>
              <th className="border-b border-slate-200 pb-3 font-semibold">위험 유형</th>
              <th className="border-b border-slate-200 pb-3 font-semibold">위험도</th>
              <th className="border-b border-slate-200 pb-3 font-semibold">수정 제안</th>
            </tr>
          </thead>
          <tbody>
            {result.issues.map((item) => (
              <tr key={`${item.text}-${item.riskType}`} className={`align-top border-l-4 ${rowTone[item.severity]}`}>
                <td className="border-b border-slate-100 py-4 pr-4 pl-3 font-medium text-slate-900">{item.text}</td>
                <td className="border-b border-slate-100 py-4 pr-4 text-slate-600">
                  <p>{item.riskType}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{item.reason}</p>
                </td>
                <td className="border-b border-slate-100 py-4 pr-4">
                  <RiskBadge level={item.severity} />
                </td>
                <td className="border-b border-slate-100 py-4 text-slate-600">{item.revision}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-4 rounded-lg bg-slate-50 p-4 text-sm font-medium leading-6 text-slate-700">{result.finalRecommendation}</p>
    </section>
  )
}
