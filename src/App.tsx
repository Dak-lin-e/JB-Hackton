import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './layout/AppLayout'

const DashboardPage = lazy(() => import('./features/dashboard/DashboardPage').then((module) => ({ default: module.DashboardPage })))
const ResultStudioPage = lazy(() => import('./features/result-studio/ResultStudioPage').then((module) => ({ default: module.ResultStudioPage })))
const PerformancePage = lazy(() => import('./features/performance/PerformancePage').then((module) => ({ default: module.PerformancePage })))
const TrendVideoLabPage = lazy(() => import('./features/trend-video-lab/TrendVideoLabPage').then((module) => ({ default: module.TrendVideoLabPage })))
const InstagramTrendLabPage = lazy(() =>
  import('./features/instagram-trend-lab/InstagramTrendLabPage').then((module) => ({ default: module.InstagramTrendLabPage })),
)

function PageLoader() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm font-semibold text-slate-600 shadow-sm">
      화면을 준비하고 있습니다.
    </div>
  )
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="/campaign/new" element={<Navigate to="/trend-video-lab" replace />} />
          <Route path="/campaign/result" element={<ResultStudioPage />} />
          <Route path="/performance" element={<PerformancePage />} />
          <Route path="/trend-video-lab" element={<TrendVideoLabPage />} />
          <Route path="/instagram-trend-lab" element={<InstagramTrendLabPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
