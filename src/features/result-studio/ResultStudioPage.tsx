import { useState } from 'react'
import { Link } from 'react-router-dom'
import { toApiAssetUrl } from '../../services/api'
import { Badge } from '../../shared/components/Badge'
import { useCampaignStore } from '../../store/campaignStore'
import { ABTestCard } from './components/ABTestCard'
import { ComplianceCheckTable } from './components/ComplianceCheckTable'
import { GeneratedAdCard } from './components/GeneratedAdCard'
import { ResultTabs } from './components/ResultTabs'
import type { ResultTabId } from './types'

export function ResultStudioPage() {
  const { formData, selectedPattern, generatedAd, creativePlan, complianceResult, isGenerating, generationError } = useCampaignStore()
  const [activeTab, setActiveTab] = useState<ResultTabId>('concept')
  const youtubeText = generatedAd?.youtubeShortsScript.join('\n') ?? ''
  const cardNewsText = generatedAd?.cardNewsCopies.map((line, index) => `${index + 1}. ${line}`).join('\n') ?? ''
  const hashtagText = generatedAd ? `${generatedAd.hashtags.join(' ')}\n${generatedAd.cta}` : ''
  const productionText = creativePlan
    ? [
        '[광고영상기획안]',
        `${creativePlan.videoCreative.format} · ${creativePlan.videoCreative.duration}`,
        creativePlan.videoCreative.sceneByScene
          .map((scene) => `${scene.time}\n화면: ${scene.visualDirection}\n자막: ${scene.caption}\n내레이션: ${scene.narration}\n편집: ${scene.editingDirection}`)
          .join('\n\n'),
        `촬영 가이드: ${creativePlan.videoCreative.shootingGuide}`,
        `편집 가이드: ${creativePlan.videoCreative.editingGuide}`,
        `음악 가이드: ${creativePlan.videoCreative.musicGuide}`,
        '',
        '[광고이미지생성기획안]',
        creativePlan.imageCreative.instagramFeedCopy,
        `비주얼 방향: ${creativePlan.imageCreative.visualDirection}`,
        `레이아웃: ${creativePlan.imageCreative.layoutGuide}`,
        `이미지 생성용 안전 프롬프트: ${creativePlan.imageCreative.safeImagePrompt}`,
      ].join('\n')
    : ''
  const generatedImageUrl = toApiAssetUrl(creativePlan?.imageCreative.generatedImage?.url)

  if (isGenerating) {
    return (
      <section className="rounded-lg border border-cyan-200 bg-cyan-50 p-6 text-sm font-semibold text-cyan-700">
        AI Agent가 SNS 트렌드 구조를 분석하고 있습니다...
      </section>
    )
  }

  if (generationError) {
    return (
      <section className="rounded-lg border border-rose-200 bg-rose-50 p-6">
        <h2 className="text-lg font-bold text-rose-800">광고 생성 결과를 불러오지 못했습니다.</h2>
        <p className="mt-2 text-sm text-rose-700">{generationError}</p>
        <Link to="/trend-video-lab" className="mt-4 inline-flex rounded-lg bg-rose-700 px-4 py-2 text-sm font-bold text-white">
          다시 생성하기
        </Link>
      </section>
    )
  }

  if (!generatedAd) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-950">아직 생성된 광고 결과가 없습니다.</h2>
        <p className="mt-2 text-sm text-slate-500">YouTube 트렌드 분석 화면에서 상품 정보를 입력하면 AI Agent 결과가 이곳에 저장됩니다.</p>
        <Link to="/trend-video-lab" className="mt-4 inline-flex rounded-lg bg-slate-950 px-4 py-2 text-sm font-bold text-white">
          YouTube 트렌드 분석 시작하기
        </Link>
      </section>
    )
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Badge tone="blue">{selectedPattern?.title ?? '월급 실종 밈'}</Badge>
            <h2 className="mt-3 text-2xl font-bold text-slate-950">{formData.productName} 광고 생성 결과</h2>
            <p className="mt-2 text-sm text-slate-500">
              {formData.targetCustomer} 대상 · {formData.channel} 중심 · {formData.goal}
            </p>
          </div>
          <Link to="/trend-video-lab" className="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-100">
            입력값 수정
          </Link>
        </div>
      </section>

      <ResultTabs activeTab={activeTab} onChange={setActiveTab} />

      {activeTab === 'concept' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <GeneratedAdCard title="추천 광고 콘셉트" copyText={generatedAd.concept}>
            <p className="whitespace-pre-line">{generatedAd.concept}</p>
            {creativePlan?.trendAdaptationNotes?.length ? (
              <div className="mt-4 rounded-lg bg-cyan-50 p-3">
                <p className="text-xs font-bold text-cyan-700">숏폼 트렌드 반영 방식</p>
                <ul className="mt-2 space-y-1 text-sm leading-6 text-cyan-900">
                  {creativePlan.trendAdaptationNotes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {creativePlan?.ragInsights?.length ? (
              <div className="mt-4 rounded-lg border border-emerald-100 bg-emerald-50 p-3">
                <p className="text-xs font-bold text-emerald-700">RAG 기반 트렌드 선택 근거</p>
                <div className="mt-3 space-y-3">
                  {creativePlan.ragInsights.map((insight) => (
                    <div key={insight.patternId ?? insight.sourceTitle} className="rounded-lg bg-white/70 p-3 text-sm leading-6 text-emerald-950">
                      <p className="font-bold">{insight.sourceTitle}</p>
                      <p className="mt-1 text-xs text-emerald-800">{insight.reason}</p>
                      <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold">
                        <span className="rounded-full bg-emerald-100 px-2.5 py-1">유사도 {Math.round((insight.semanticSimilarity ?? 0) * 100)}%</span>
                        <span className="rounded-full bg-cyan-100 px-2.5 py-1 text-cyan-800">트렌드 {insight.trendScore ?? 0}</span>
                        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-700">최신성 {insight.freshnessScore ?? 0}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
            {creativePlan?.agentWorkflow && (
              <div className="mt-4 rounded-lg border border-slate-200 bg-white p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-bold text-slate-700">Agent 판단·검증·개선 로그</p>
                  <Badge tone={creativePlan.agentWorkflow.revisionApplied ? 'amber' : 'green'}>
                    {creativePlan.agentWorkflow.revisionApplied ? '자동 수정 적용' : '수정 불필요'}
                  </Badge>
                </div>
                <div className="mt-3 space-y-3">
                  {creativePlan.agentWorkflow.decisionLogs.map((log) => (
                    <div key={log.step} className="rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700">
                      <p className="font-bold text-slate-950">{log.step}</p>
                      {log.detail && <p className="mt-1 text-xs text-slate-500">{log.detail}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </GeneratedAdCard>
          <GeneratedAdCard title="추천 해시태그 & CTA" copyText={hashtagText}>
            <div className="flex flex-wrap gap-2">
              {generatedAd.hashtags.map((tag) => (
                <Badge key={tag} tone="slate">{tag}</Badge>
              ))}
            </div>
            <p className="mt-4 font-semibold text-slate-950">{generatedAd.cta}</p>
          </GeneratedAdCard>
        </div>
      )}

      {activeTab === 'concept' && creativePlan?.agentWorkflow && (
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-950">QualityEvaluationAgent / RevisionAgent 결과</h2>
              <p className="mt-1 text-sm text-slate-500">LangChain PromptTemplate → ChatOpenAI → JsonOutputParser 구조로 평가와 수정을 수행합니다.</p>
            </div>
            <div className="flex gap-2">
              <Badge tone="blue">초안 {creativePlan.agentWorkflow.initialQuality.overallScore}점</Badge>
              <Badge tone="green">최종 {creativePlan.agentWorkflow.finalQuality.overallScore}점</Badge>
            </div>
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="font-bold text-slate-950">품질 평가 요약</p>
              <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <div><dt className="text-slate-500">상품 반영도</dt><dd className="font-bold text-slate-950">{creativePlan.agentWorkflow.finalQuality.productGroundingScore}</dd></div>
                <div><dt className="text-slate-500">트렌드 적합도</dt><dd className="font-bold text-slate-950">{creativePlan.agentWorkflow.finalQuality.trendFitScore}</dd></div>
                <div><dt className="text-slate-500">제작 구체성</dt><dd className="font-bold text-slate-950">{creativePlan.agentWorkflow.finalQuality.productionReadinessScore}</dd></div>
                <div><dt className="text-slate-500">금융광고 안전성</dt><dd className="font-bold text-slate-950">{creativePlan.agentWorkflow.finalQuality.financialSafetyScore}</dd></div>
              </dl>
              <p className="mt-3 text-sm leading-6 text-slate-600">{creativePlan.agentWorkflow.finalQuality.finalRecommendation}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="font-bold text-slate-950">수정 전/후 비교</p>
              {creativePlan.agentWorkflow.changes.length ? (
                <div className="mt-3 space-y-3">
                  {creativePlan.agentWorkflow.changes.map((change) => (
                    <div key={`${change.field}-${change.reason}`} className="rounded-lg bg-white p-3 text-sm leading-6">
                      <p className="font-bold text-slate-950">{change.field}</p>
                      <p className="mt-1 text-slate-500">Before: {change.before}</p>
                      <p className="text-slate-800">After: {change.after}</p>
                      <p className="mt-1 text-xs text-cyan-700">{change.reason}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-500">자동 수정 없이 초안이 기준을 통과했습니다.</p>
              )}
            </div>
          </div>
        </section>
      )}

      {activeTab === 'production' && creativePlan && (
        <div className="grid gap-4 xl:grid-cols-2">
          <GeneratedAdCard title="광고영상기획안" copyText={productionText}>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-bold text-slate-950">
                  {creativePlan.videoCreative.format} · {creativePlan.videoCreative.duration}
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-600">{creativePlan.videoCreative.shootingGuide}</p>
              </div>
              <div className="space-y-3">
                {creativePlan.videoCreative.sceneByScene.map((scene) => (
                  <div key={scene.time} className="rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700">
                    <p className="font-bold text-slate-950">{scene.time}</p>
                    <p>화면: {scene.visualDirection}</p>
                    <p>자막: {scene.caption}</p>
                    <p>내레이션: {scene.narration}</p>
                    <p>편집: {scene.editingDirection}</p>
                  </div>
                ))}
              </div>
              <div className="rounded-lg bg-cyan-50 p-3 text-sm leading-6 text-cyan-900">
                <p><span className="font-bold">편집 가이드:</span> {creativePlan.videoCreative.editingGuide}</p>
                <p><span className="font-bold">음악 가이드:</span> {creativePlan.videoCreative.musicGuide}</p>
                <p><span className="font-bold">썸네일:</span> {creativePlan.videoCreative.thumbnailCopy} · {creativePlan.videoCreative.thumbnailDirection}</p>
              </div>
            </div>
          </GeneratedAdCard>

          <GeneratedAdCard title="광고이미지생성기획안" copyText={productionText}>
            <div className="space-y-4 text-sm leading-6 text-slate-700">
              {generatedImageUrl && (
                <div className="overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
                  <img src={generatedImageUrl} alt="생성된 광고 이미지 시안" className="aspect-square w-full object-cover" />
                  <div className="flex items-center justify-between gap-3 p-3">
                    <p className="text-xs font-semibold text-slate-500">
                      {creativePlan?.imageCreative.generatedImage?.model} · {creativePlan?.imageCreative.generatedImage?.status}
                    </p>
                    <a href={generatedImageUrl} target="_blank" rel="noreferrer" className="text-xs font-bold text-cyan-700">
                      이미지 파일 열기
                    </a>
                  </div>
                </div>
              )}
              <p className="font-semibold text-slate-950">{creativePlan.imageCreative.instagramFeedCopy}</p>
              <p><span className="font-bold text-slate-950">비주얼 방향:</span> {creativePlan.imageCreative.visualDirection}</p>
              <p><span className="font-bold text-slate-950">레이아웃:</span> {creativePlan.imageCreative.layoutGuide}</p>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="font-bold text-slate-950">카드뉴스 문구</p>
                <ol className="mt-2 space-y-1">
                  {creativePlan.imageCreative.cardNewsCopies.map((copy, index) => (
                    <li key={copy}>{index + 1}. {copy}</li>
                  ))}
                </ol>
              </div>
              <div className="rounded-lg bg-emerald-50 p-3 text-emerald-900">
                <p className="font-bold">이미지 생성용 안전 프롬프트</p>
                <p className="mt-2">{creativePlan.imageCreative.safeImagePrompt}</p>
              </div>
              {creativePlan.imageCreative.generatedImage?.referenceMediaUrls?.length ? (
                <div className="rounded-lg bg-slate-50 p-3">
                  <p className="font-bold text-slate-950">참조한 인스타 미디어 URL</p>
                  <ul className="mt-2 space-y-1 break-all text-xs text-slate-500">
                    {creativePlan.imageCreative.generatedImage.referenceMediaUrls.map((url) => (
                      <li key={url}>{url}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          </GeneratedAdCard>
        </div>
      )}

      {activeTab === 'shorts' && (
        <div className="grid gap-4 lg:grid-cols-3">
          <GeneratedAdCard title="인스타그램 릴스 캡션" copyText={generatedAd.instagramCaption}>
            <p className="whitespace-pre-line">{generatedAd.instagramCaption}</p>
          </GeneratedAdCard>
          <GeneratedAdCard title="유튜브 쇼츠 15초 스크립트" copyText={youtubeText}>
            <ul className="space-y-2">
              {generatedAd.youtubeShortsScript.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </GeneratedAdCard>
          <GeneratedAdCard title="틱톡용 짧은 카피" copyText={generatedAd.tiktokCopy}>
            <p>{generatedAd.tiktokCopy}</p>
          </GeneratedAdCard>
        </div>
      )}

      {activeTab === 'cardNews' && (
        <GeneratedAdCard title="카드뉴스 5장 문구" copyText={cardNewsText}>
          <ol className="space-y-2">
            {generatedAd.cardNewsCopies.map((line, index) => (
              <li key={line}>
                {index + 1}. {line}
              </li>
            ))}
          </ol>
        </GeneratedAdCard>
      )}

      {activeTab === 'risk' && <ComplianceCheckTable result={complianceResult} />}

      {activeTab === 'abTest' && (
        <section>
          <div className="mb-4">
            <h2 className="text-xl font-bold text-slate-950">A/B 테스트 광고안</h2>
            <p className="mt-1 text-sm text-slate-500">동일 상품을 세 가지 메시지 구조로 검증합니다.</p>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            {generatedAd.abTests.map((idea) => (
              <ABTestCard key={idea.variant} idea={idea} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
