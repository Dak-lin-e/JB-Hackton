# Trend-to-FinAd Agent

JB금융그룹 공모전 프로젝트입니다.

금융상품 정보를 기반으로 YouTube/Instagram 숏폼 트렌드와 밈 패턴을 분석하고, MZ세대 대상 금융상품 광고 기획안, 광고 이미지, 광고 문구, 카드뉴스 문구, 리스크 점검, A/B 테스트안을 생성하는 AI 마케팅 캠페인 스튜디오입니다.

## Tech Stack

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Zustand
- FastAPI
- OpenAI API
- YouTube Data API
- Apify Instagram Trending Scraper
- LangChain

## Run

백엔드:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

FastAPI 문서:

```text
http://localhost:8000/docs
```

프론트엔드:

```bash
npm install
npm run dev
```

기본 상태에서는 React 프론트가 `http://localhost:8000` FastAPI 서버로 요청을 보냅니다.

백엔드 주소를 바꾸려면 `VITE_API_BASE_URL`을 지정하면 됩니다.

```bash
VITE_API_BASE_URL=http://localhost:8080 npm run dev
```

## Build

```bash
npm run build
```

## Main Routes

- `/` 대시보드
- `/trend-video-lab` YouTube 트렌드 분석 기반 광고 기획
- `/instagram-trend-lab` Instagram 트렌드 분석 기반 광고 기획
- `/campaign/result` 결과 스튜디오
- `/performance` 성과 분석 Coming Soon

## Core Flow

```text
금융상품 정보 입력
→ YouTube / Instagram 숏폼 트렌드 수집
→ Trend Analysis Agent
→ Lightweight RAG Layer
→ Creative Planning Agent
→ Quality Evaluation Agent
→ Compliance Agent
→ Revision Agent
→ Image Generation
→ Result Studio
```

## Environment

예시는 `backend/.env.example`을 참고하세요.

주요 설정:

```env
USE_MOCK_LLM=true
OPENAI_API_KEY=
OPENAI_MODEL=
OPENAI_MODEL_TREND=
OPENAI_MODEL_CREATIVE=
OPENAI_MODEL_COMPLIANCE=
OPENAI_MODEL_QUALITY=
OPENAI_MODEL_REVISION=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

USE_MOCK_YOUTUBE=true
YOUTUBE_API_KEY=

APIFY_API_TOKEN=
USE_MOCK_IMAGE_GENERATION=true
```

## Notes

- `.env`, `.runtime`, `backend/venv`, 생성 이미지 파일은 Git에 포함하지 않습니다.
- 트렌드 패턴과 임베딩 인덱스는 기본적으로 `.runtime` 아래에 저장됩니다.
- 원본 영상/문구/음악/썸네일을 복제하지 않고, 트렌드 구조와 문법만 추상화해 광고 기획에 활용합니다.
