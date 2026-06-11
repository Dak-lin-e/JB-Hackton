import { FormEvent, useMemo, useState } from 'react'
import { Bot, RotateCcw, Send } from 'lucide-react'
import { useCampaignStore } from '../store/campaignStore'
import type { AssistantChatMessage, GeneratedAdResult } from '../types'

const suggestedQuestions = [
  '이 문구를 더 MZ스럽게 바꿔줘',
  '금융광고 리스크를 낮춰줘',
  '인스타그램용으로 더 짧게 줄여줘',
  '신뢰감 있는 톤으로 바꿔줘',
  'A안과 B안을 섞어서 새 문구를 만들어줘',
]

interface AssistantPanelProps {
  className?: string
}

function createMessage(role: AssistantChatMessage['role'], text: string): AssistantChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    text,
    createdAt: new Date().toISOString(),
  }
}

function compactCaption(text: string, fallback: string) {
  const firstLine = text.split('\n').find(Boolean) ?? fallback
  return `${firstLine.slice(0, 42)}\n조건과 유의사항을 확인하고 시작해보세요.`
}

function reviseAd(request: string, ad: GeneratedAdResult | undefined, productName: string) {
  if (!ad) {
    return {
      answer:
        '아직 수정할 광고 결과가 없어요. 먼저 YouTube 트렌드 분석 화면에서 광고 기획안을 생성하면, 그 결과를 기억하고 여기서 바로 수정할 수 있습니다.',
    }
  }

  const lowerRequest = request.toLowerCase()
  let nextAd: GeneratedAdResult | undefined
  let answer = '요청을 반영해서 현재 저장된 광고 결과를 업데이트했어요. 결과 스튜디오에서 수정된 문구를 바로 확인할 수 있습니다.'

  if (request.includes('MZ') || request.includes('mz') || request.includes('밈') || request.includes('재밌')) {
    nextAd = {
      ...ad,
      instagramCaption: `${productName}, 어렵게 설명하지 말고 루틴으로.\n이번 달 소비 흐름이 살짝 흔들렸다면 조건과 유의사항부터 확인하고 나에게 맞는 금융 루틴을 잡아보세요.`,
      tiktokCopy: `돈 관리, 감으로 하지 말고 ${productName} 조건부터 체크.`,
      cta: '내 루틴에 맞는 조건 확인하기',
    }
    answer = '더 MZ스럽게 바꾸되 금융광고라 과장 표현은 뺐어요. 공감형 첫 문장과 짧은 루틴 메시지로 수정했습니다.'
  } else if (request.includes('리스크') || request.includes('위험') || request.includes('완화')) {
    nextAd = {
      ...ad,
      instagramCaption: `${ad.instagramCaption}\n\n가입 조건, 우대 조건, 수수료 및 중도해지 유의사항은 상품 설명서에서 확인해주세요.`,
      cta: '조건과 유의사항 확인 후 시작하기',
    }
    answer = '금융광고 리스크를 낮추기 위해 단정적인 표현을 줄이고, 조건 확인과 유의사항 안내를 CTA 주변에 보강했습니다.'
  } else if (request.includes('짧게') || request.includes('줄여') || request.includes('인스타')) {
    nextAd = {
      ...ad,
      instagramCaption: compactCaption(ad.instagramCaption, `${productName} 조건 확인하고 시작하기.`),
    }
    answer = '인스타그램 릴스 캡션용으로 짧게 줄였어요. 첫 줄에서 훅을 만들고, 두 번째 줄에 조건 확인 문구를 남겼습니다.'
  } else if (request.includes('신뢰') || request.includes('차분') || request.includes('금융권')) {
    nextAd = {
      ...ad,
      instagramCaption: `${productName}의 혜택과 가입 조건을 차분하게 확인해보세요.\n조건 충족 여부와 유의사항을 살핀 뒤, 나에게 맞는 금융 루틴으로 활용할 수 있습니다.`,
      tiktokCopy: `${productName}, 혜택보다 먼저 조건과 유의사항을 확인하세요.`,
      cta: '상품 조건 자세히 확인하기',
    }
    answer = '신뢰감 있는 톤으로 바꿨어요. 혜택을 과하게 밀기보다 조건, 확인, 선택의 언어를 중심으로 정리했습니다.'
  } else if (request.includes('A안') || request.includes('B안') || lowerRequest.includes('a안') || lowerRequest.includes('b안')) {
    const first = ad.abTests[0]
    const second = ad.abTests[1]
    nextAd = {
      ...ad,
      concept: `${first?.hook ?? ad.concept}\n\n${second?.message ?? ad.concept}`,
      instagramCaption: `${first?.hook ?? productName}\n${second?.message ?? '혜택과 조건을 함께 확인해보세요.'}`,
      cta: second?.channel ? `${second.channel}에서 조건 확인하기` : ad.cta,
    }
    answer = 'A안의 공감형 훅과 B안의 혜택 설명 구조를 섞어서 콘셉트와 캡션을 업데이트했습니다.'
  } else if (request.includes('카드뉴스')) {
    nextAd = {
      ...ad,
      cardNewsCopies: [
        `${productName}, 먼저 어떤 상품인지 한 줄로 확인`,
        `핵심 혜택은 짧게, 조건은 명확하게`,
        `내 상황에 맞는지 가입 조건 점검`,
        `유의사항과 제한 조건 확인`,
        `조건 확인 후 나에게 맞으면 시작`,
      ],
    }
    answer = '카드뉴스 문구를 더 실제 금융광고 흐름에 맞게 정리했습니다. 혜택, 조건, 유의사항 순서가 보이도록 바꿨어요.'
  } else {
    nextAd = {
      ...ad,
      instagramCaption: `${ad.instagramCaption}\n\n요청 반영 메모: ${request}`,
    }
  }

  return { answer, nextAd }
}

export function AssistantPanel({ className = '' }: AssistantPanelProps) {
  const {
    formData,
    generatedAd,
    creativePlan,
    assistantMessages,
    addAssistantMessage,
    clearAssistantMessages,
    setGeneratedAd,
  } = useCampaignStore()
  const [input, setInput] = useState('')

  const contextLabel = useMemo(() => {
    if (!generatedAd) return '수정할 광고 없음'
    return `${formData.productName || '최근 생성 광고'} 기억 중`
  }, [formData.productName, generatedAd])

  const ask = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return

    addAssistantMessage(createMessage('user', trimmed))
    const { answer, nextAd } = reviseAd(trimmed, generatedAd, formData.productName || '금융상품')
    if (nextAd) {
      setGeneratedAd(nextAd)
    }

    const trendNote = creativePlan?.usedTrendPatterns?.length
      ? `\n\n참고한 트렌드 문법: ${creativePlan.usedTrendPatterns.slice(0, 3).join(', ')}`
      : ''
    addAssistantMessage(createMessage('assistant', `${answer}${trendNote}`))
    setInput('')
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    ask(input)
  }

  return (
    <aside className={`rounded-lg border border-slate-200 bg-white shadow-sm xl:sticky xl:top-24 xl:h-[calc(100vh-7rem)] ${className}`}>
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-white">
            <Bot size={20} />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-950">AI 기획자 보조</h2>
            <p className="text-xs text-slate-500">{contextLabel}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={clearAssistantMessages}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100"
          aria-label="대화 초기화"
        >
          <RotateCcw size={16} />
        </button>
      </div>

      <div className="space-y-2 border-b border-slate-200 p-4">
        {suggestedQuestions.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => ask(question)}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-left text-xs font-medium text-slate-700 transition hover:border-cyan-300 hover:bg-cyan-50"
          >
            {question}
          </button>
        ))}
      </div>

      <div className="flex max-h-[360px] flex-col gap-3 overflow-y-auto p-4 xl:max-h-[calc(100vh-26rem)]">
        {assistantMessages.map((message) => (
          <div
            key={message.id}
            className={`rounded-lg px-3 py-2 text-sm leading-6 ${
              message.role === 'assistant' ? 'bg-slate-100 text-slate-700' : 'bg-cyan-600 text-white'
            }`}
          >
            {message.text}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 p-4">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          className="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
          placeholder="생성 광고 수정 요청 입력"
        />
        <button type="submit" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-white" aria-label="전송">
          <Send size={17} />
        </button>
      </form>
    </aside>
  )
}
