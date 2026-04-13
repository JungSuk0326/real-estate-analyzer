# Claude Code 작업 지침서

> 이 파일은 새 Claude Code 세션에서 자동 로드됩니다. 프로젝트 맥락을 빠르게 복원하기 위한 가이드입니다.

## 프로젝트 한 줄 정의
공공데이터 + AI로 소상공인·세입자·투자자에게 부동산/상권의 숨겨진 정보를 해석해 전달하는 데이터 인텔리전스 플랫폼.

## 개발자 프로필
- 반도체 장비 자동화 엔지니어 (C#/.NET 기반)
- 웹 서비스 신규 개발 (Python/JS)
- 목표: 패시브 인컴 시스템 구축

## 중요 문서 읽기 순서
새 세션 시작 시 이 순서로 읽으면 맥락 복원이 가능:
1. **CONTEXT.md** — 비전·타겟·수익모델 (기획 원안)
2. **PLAN.md** — MVP 실행 계획 (현재 Phase, 로드맵)
3. **DECISIONS.md** — 의사결정 로그 (왜 이렇게 됐는가)
4. **docs/api_reference.md** — API 호출 패턴·주요 코드
5. **git log --oneline -20** — 최근 진행 이력

## 현재 상태 (Phase)
- **Sprint 0 완료**: 4개 공공데이터 API 검증
- **다음**: MVP v1 백엔드 구축 (데이터 적재 → 분석 → LLM 리포트)

## 프로젝트 구조
```
real-estate-analyzer/
├── CLAUDE.md                  # 이 파일
├── CONTEXT.md                 # 비전·기획 원안
├── PLAN.md                    # MVP 실행 기획안
├── DECISIONS.md               # 의사결정 기록
├── docs/
│   └── api_reference.md       # API 호출 레퍼런스
├── api_test/                  # Sprint 0 검증 스크립트
│   ├── config.py              # 4개 API 키 로드
│   ├── test_seoul_revenue.py  # ★ 서울 열린데이터광장 (MVP 핵심)
│   ├── test_commercial.py     # 소상공인진흥공단
│   ├── test_real_estate.py    # 국토교통부
│   └── test_population.py     # 행정안전부 (미완)
├── 서울시 상권분석서비스(영역-상권)/  # 1,650개 상권 shapefile
└── .env / .env.example        # API 키
```

## 기술 스택
- Python 3.13 (venv: `.venv`)
- FastAPI (v1에서 도입 예정, 아직 없음)
- PostgreSQL (v1에서 도입 예정)
- Claude API (자연어 리포트 생성)
- Next.js (v1 후반)

## 현재까지 확보한 4개 API

| API | 상태 | MVP 역할 |
|---|:-:|---|
| 서울 열린데이터광장 (VwsmAdstrdSelngW) | 정상 | **매출 분석의 핵심** |
| 국토교통부 상업용 실거래가 | 정상 | 매매가만 있음 (임대료 X) |
| 소상공인진흥공단 상가정보 | 정상 | 점포 위치·업종 |
| 행정안전부 인구 | **미완** | 엔드포인트 확인했으나 파라미터 미해결 |

## 주요 함정 (Gotcha)

### 1. 상가 "임대료" 데이터가 없다
- 국토교통부 실거래가 API는 **매매가만** 제공
- CONTEXT.md 원안의 "임대료 상승률 연 X%"는 **현재 구현 불가**
- 별도 API(상업용 전월세 실거래가) 신청 필요

### 2. 서울 열린데이터광장 서비스명 패턴
- 패턴: `Vwsm{단위}SelngW` (Mega=서울시, Signgu=자치구, Adstrd=행정동)
- **`VwsmTrdarSelngW`(상권 단위)는 존재하지 않음** — 이 이름 시도하지 말 것
- 상권 단위 매출 분석이 필요하면 행정동 단위 데이터를 좌표로 재집계

### 3. 행정동 코드는 8자리
- 예: 서교동 `11440660` (10자리 `1144053000` 아님)
- 소상공인진흥공단은 8자리 요구
- 자세한 코드는 `docs/api_reference.md` 참고

### 4. 서울 매출 API 페이지네이션
- 한 번에 최대 1,000건
- 2025 Q4 행정동 매출 총 16,718건 → 17번 호출 필요
- 행정동코드 오름차순 정렬되어 있어 조기 종료 가능

### 5. 분기 코드 포맷
- `YYYY{1~4}` 형식, 예: `20254` = 2025년 4분기
- 최신 가용: **2025 Q4** (2026-04 현재)
- 2019 Q1부터 제공

### 6. 소상공인진흥공단 API
- 매출 데이터 **없음** (점포 목록만)
- 개업/폐업 일자 **없음** (현재 스냅샷만)
- 시계열은 서울 매출 API에서 얻음

## 코딩 컨벤션

### Python
- 인코딩: UTF-8 (파일 기본)
- 문자열: 한글 주석/출력 적극 사용
- API 함수: `requests` + JSON 응답 + 30초 타임아웃
- 설정: `.env` → `api_test/config.py`에서 로드

### Git
- 커밋 메시지는 **"왜"**를 포함할 것
- 예: "서울 매출 API 4종 검증 완료 — VwsmAdstrdSelngW를 MVP 기본 API로 채택"
- `.env`는 절대 커밋 금지 (`.gitignore` 확인됨)

### API 키 관리
- **로컬**: `.env` 파일 (git 추적 제외)
- **백업**: 비밀번호 관리자(Bitwarden/1Password 등)의 Secure Note
  - Note 제목: `real-estate-analyzer .env`
  - 내용: `.env` 파일 전체 복사 저장
- **새 PC 셋업**: Secure Note에서 내용 복사 → `.env`에 붙여넣기
- **채팅 노출 금지**: PAT나 API 키를 대화창에 붙여넣지 말 것
- **절대 금지**: `.gitignore`에서 `.env` 제외하지 말 것 (커밋 시 영구 유출)

## 세션 시작 루틴 (권장)
새 PC나 새 세션에서 시작할 때:
```
1. CLAUDE.md, PLAN.md, DECISIONS.md 읽기
2. git log --oneline -10 로 최근 이력 확인
3. "현재 상태 요약해줘, 다음 작업 제안해줘" 질문
```

## 세션 종료 루틴 (권장)
중요한 결정이나 발견이 있었다면:
```
"이번 세션에서 결정/발견한 것을 DECISIONS.md와 
해당되면 CLAUDE.md의 함정 섹션에 반영해줘"
```

## 하지 말 것
- **CONTEXT.md는 수정하지 말 것** (원안 보존)
- **PLAN.md/DECISIONS.md는 업데이트 O** (살아있는 문서)
- `.env` 파일 commit 금지
- 실제 토큰·비밀번호를 코드나 문서에 하드코딩 금지
- 소상공인진흥공단 API에서 매출을 찾지 말 것 (없음)

## 자주 쓰는 명령어

```bash
# 가상환경 활성화
source .venv/bin/activate

# 서울 매출 API 테스트
python -m api_test.test_seoul_revenue

# 특정 행정동 데이터 수집 (예: 서교동)
python -c "from api_test.test_seoul_revenue import fetch_adstrd_by_code; print(fetch_adstrd_by_code('11440660', '20254'))"
```
