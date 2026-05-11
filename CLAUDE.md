# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

영수증 지출 관리 앱 — 영수증 이미지/PDF를 업로드하면 Upstage Vision LLM이 LangChain을 통해 자동 파싱하고, JSON으로 저장한 후 React 대시보드에서 지출 내역을 조회·관리할 수 있는 경량 웹 애플리케이션. 1일 스프린트 MVP로 Vercel 배포를 목표로 한다.

## 개발 명령어

### 백엔드 (FastAPI)
```bash
# 가상환경 생성 및 활성화 (최초 1회)
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 의존성 설치
pip install -r backend/requirements.txt

# 개발 서버 실행
uvicorn backend.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 프론트엔드 (React + Vite)
```bash
cd frontend
npm install
npm run dev       # → http://localhost:5173
npm run build     # 프로덕션 빌드
```

### 환경변수
`.env.example`을 `.env`로 복사 후 아래 값을 설정한다:
- `UPSTAGE_API_KEY` — Upstage 콘솔 API 키
- `VITE_API_BASE_URL` — 백엔드 URL (프로덕션에서 같은 도메인 사용 시 빈 문자열 `""`)
- `DATA_FILE_PATH` — expenses.json 저장 경로 (`VERCEL=1`이면 `/tmp/expenses.json`으로 자동 설정)

## 아키텍처

```
frontend/src/
  pages/          Dashboard.jsx | UploadPage.jsx | ExpenseDetail.jsx
  components/     DropZone, ParsePreview, ExpenseCard, SummaryCard,
                  FilterBar, Badge, Modal, Toast, ProgressBar
  api/axios.js    Axios 인스턴스 (baseURL은 VITE_API_BASE_URL 환경변수)

backend/
  main.py                     FastAPI 앱: CORS 설정, 라우터 등록
  routers/
    upload.py                 POST /api/upload
    expenses.py               GET|DELETE|PUT /api/expenses[/{id}]
    summary.py                GET /api/summary
  services/
    ocr_service.py            LangChain + ChatUpstage 이미지→JSON 파이프라인
    storage_service.py        expenses.json 읽기/쓰기/추가
  data/expenses.json          지출 항목 JSON 배열
```

## 핵심 설계 결정

**OCR 파이프라인**: Upstage Document Digitization API(`POST /v1/document-digitization`, `model=ocr`)로 영수증 텍스트를 추출한 후, `ChatUpstage`(solar-pro 계열) LangChain 체인으로 구조화 JSON을 생성한다. PRD의 `document-digitization-vision` 모델명은 실제 API 스펙과 달라 `ocr`로 교체한다.

**PDF 처리**: `pdf2image`로 PDF 페이지를 이미지로 변환한 뒤 처리한다. Vercel 환경에서는 일반 파일시스템이 읽기 전용이므로 임시 파일은 반드시 `/tmp/`에 저장해야 한다.

**데이터 영속성**: Vercel 서버리스 컨테이너는 재시작 시 파일시스템이 초기화된다. 프론트엔드에서 `localStorage`에 병행 저장하는 방식으로 대응한다. 안정적인 영속성이 필요하면 Railway/Render 또는 Vercel KV로 전환한다.

**Vercel 배포**: `vercel.json`에서 `/api/*` 경로는 Python 서버리스 함수(`@vercel/python` + Mangum)로, 나머지는 정적 프론트엔드 빌드로 라우팅한다.

## 지출 데이터 스키마

```json
{
  "id": "uuid-v4",
  "created_at": "ISO-8601",
  "store_name": "string",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM | null",
  "category": "식료품|외식|교통|쇼핑|의료|기타",
  "items": [{ "name": "", "quantity": 0, "unit_price": 0, "total_price": 0 }],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "string | null",
  "raw_image_path": "uploads/..."
}
```

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/health` | 서버 Health Check |
| POST | `/api/upload` | 영수증 파일 업로드 (multipart/form-data `file`), 파싱된 지출 JSON 반환 |
| GET | `/api/expenses` | 지출 목록 조회; 쿼리 파라미터: `from`, `to` (YYYY-MM-DD) |
| DELETE | `/api/expenses/{id}` | UUID로 항목 삭제 |
| PUT | `/api/expenses/{id}` | UUID로 항목 부분 수정 |
| GET | `/api/summary` | 합계 통계; 쿼리 파라미터: `month` (YYYY-MM) |

## UI / 스타일 규칙

- **색상**: 주요색 `indigo-600`, 배경 `gray-50`, 카드 `white`; 의미색: `green-500` 성공, `red-500` 오류, `amber-500` 경고
- **Toast**: `fixed bottom-4 right-4`, 3초 자동 소멸, 최신 메시지만 표시
- **버튼**: 요청 중 `disabled` + `opacity-50 cursor-not-allowed` 처리
- **폰트**: Pretendard CDN, fallback으로 `Noto Sans KR`
- **그리드**: 지출 카드 `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`
- 커스텀 Tailwind 애니메이션(`slide-up`, `scale-in`, `fade-in`)은 `tailwind.config.js`에 정의

## 주요 버그 체크리스트

| 증상 | 먼저 확인할 것 |
|------|--------------|
| CORS 오류 | `main.py`의 `allow_origins` 설정; `vercel.json` 라우팅 경로 일치 여부 |
| OCR 500 오류 | LLM 응답이 JSON 형식인지; `UPSTAGE_API_KEY` 유효한지 |
| PDF 변환 실패 | Poppler 설치 여부; Vercel에서 `/tmp/` 경로 사용 여부 |
| Vercel 데이터 소실 | 서버리스 FS 휘발성 — localStorage 병행 저장 동작 여부 확인 |
| 환경변수 미적용 | 프론트 변수에 `VITE_` 접두사 확인; Vercel 대시보드 등록 후 재배포 여부 |

## 유지보수 규칙

소스 코드 또는 라이브러리 버전이 변경되면 `PRD_영수증_지출관리앱.md`도 함께 업데이트하고, 완료된 항목의 체크박스를 반드시 체크한다.
