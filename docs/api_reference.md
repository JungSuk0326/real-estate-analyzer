# API 참조 문서

> 검증된 공공데이터 API들의 호출 패턴, 주요 필드, 실전 예시.  
> 원본 테스트 코드: `api_test/test_*.py`

## 목차
1. [서울 열린데이터광장 — 상권분석 서비스](#1-서울-열린데이터광장--상권분석-서비스) ★ MVP 핵심
2. [소상공인시장진흥공단 — 상가(상권)정보](#2-소상공인시장진흥공단--상가상권정보)
3. [국토교통부 — 상업업무용 실거래가](#3-국토교통부--상업업무용-실거래가)
4. [행정안전부 — 주민등록 인구](#4-행정안전부--주민등록-인구-미완)
5. [공통 참조 — 행정동 코드 표](#5-공통-참조--주요-행정동-코드-표)

---

## 1. 서울 열린데이터광장 — 상권분석 서비스

### 기본 정보
- **원본**: https://data.seoul.go.kr
- **환경변수**: `SEOUL_API_KEY`
- **URL 패턴**: `http://openapi.seoul.go.kr:8088/{KEY}/{TYPE}/{SERVICE}/{START}/{END}/{EXTRA}`
- **TYPE**: `json` 권장 (`xml`, `xls` 가능)
- **최대**: 1회 호출당 1,000건, 초과 시 페이지네이션

### 1-1. VwsmAdstrdSelngW — 행정동 단위 추정매출 ★ MVP 핵심

**역할**: 행정동(동) 단위로 업종별 분기 매출 조회

**파라미터**:
- `START_INDEX`, `END_INDEX` (필수)
- `STDR_YYQU_CD` (옵션, 특정 분기만 필터): `20254` = 2025 Q4

**예시**:
```python
url = f"http://openapi.seoul.go.kr:8088/{KEY}/json/VwsmAdstrdSelngW/1/1000/20254"
```

**주요 응답 필드**:
```python
{
  "STDR_YYQU_CD": "20254",              # 분기 코드
  "ADSTRD_CD": "11440660",              # 행정동코드 (8자리)
  "ADSTRD_CD_NM": "서교동",             # 행정동명
  "SVC_INDUTY_CD": "CS100001",          # 업종 코드
  "SVC_INDUTY_CD_NM": "한식음식점",     # 업종명
  "THSMON_SELNG_AMT": 74106000000.0,    # 당월 매출 금액 (원)
  "THSMON_SELNG_CO": 2058746.0,         # 당월 매출 건수
  
  # 요일별: MON/TUES/WED/THUR/FRI/SAT/SUN_SELNG_AMT (원), _SELNG_CO (건수)
  # 시간대: TMZON_00_06 / 06_11 / 11_14 / 14_17 / 17_21 / 21_24
  # 성별: ML(남)/FML(여)_SELNG_AMT
  # 연령: AGRDE_10/20/30/40/50/60_ABOVE_SELNG_AMT
  # (총 49개 필드)
}
```

**데이터 규모**:
- 분기별 ~16,800건 (서울 전체 행정동 × 업종)
- 서교동 예시: 1분기에 55개 업종 데이터

### 1-2. 기타 매출 API

| 서비스명 | 단위 | 건수 | 비고 |
|---|---|:-:|---|
| `VwsmMegaSelngW` | 서울시 전체 | 1,764 | 추세 비교용 |
| `VwsmSignguSelngW` | 자치구 | 43,043 (2019부터 누적) | 구 단위 집계 |
| `VwsmTrdarSelngW` | — | — | **존재하지 않음 (주의)** |

### 1-3. TbgisTrdarRelm — 상권 영역

**역할**: 서울시 1,650개 상권 경계 폴리곤 제공

**주요 필드**:
- `TRDAR_CD`: 상권 코드 (예: `3120103` = 홍대입구역)
- `TRDAR_CD_NM`: 상권명
- `TRDAR_SE_CD_NM`: 유형 (골목상권/전통시장/발달상권/관광특구)
- `SIGNGU_CD_NM`, `ADSTRD_CD_NM`: 자치구·행정동
- `RELM_AR`: 상권 면적 (㎡)
- `XCNTS_VALUE`, `YDNTS_VALUE`: TM좌표 (GRS80 TM)

**참고**: 프로젝트 루트의 `서울시 상권분석서비스(영역-상권)/*.shp` 파일에 동일 데이터 포함 (오프라인 사용 가능).

### 1-4. 분기 코드 포맷
- `YYYY{1~4}` 형식
- 예: `20191` (2019 Q1) ~ `20254` (2025 Q4, **최신**)
- 갱신 주기: 분기별 (매 분기 종료 후 2~3개월 후)

### 1-5. 실전 함수 (api_test/test_seoul_revenue.py)
```python
from api_test.test_seoul_revenue import fetch_adstrd_by_code

# 서교동(홍대) 2025 Q4 전체 업종 매출
rows = fetch_adstrd_by_code("11440660", "20254")
# → 55개 업종 리스트 반환
```

---

## 2. 소상공인시장진흥공단 — 상가(상권)정보

### 기본 정보
- **원본**: data.go.kr (공공데이터포털)
- **환경변수**: `SEMAS_API_KEY`
- **제공 데이터**: 점포 위치·업종 (매출·임대료·개폐업 일자는 **없음**)

### 2-1. 주요 엔드포인트

- **행정동 단위 점포**: `https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInDong`

**파라미터 조합**:
| divId | key | 의미 | 결과 |
|---|---|---|:-:|
| `ctprvnCd` | `11` | 서울시 | 대량 반환 |
| `signguCd` | `11440` | 마포구 | 구 단위 |
| **`adongCd`** | **`11440660`** | **서교동** | **★ 정밀** |

**주의**:
- `adongCd`는 **8자리** 필수 (10자리 `1144053000`은 `NODATA_ERROR`)
- `indsLclsCd=Q` (업종 대분류) 같은 경우는 `INVALID_REQUEST_PARAMETER_ERROR` 발생 가능 — 코드 포맷 엄격

**예시**:
```python
url = "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInDong"
params = {
    "serviceKey": SEMAS_API_KEY,
    "divId": "adongCd",
    "key": "11440660",        # 서교동
    "type": "json",
    "numOfRows": "1000",
    "pageNo": "1",
}
```

### 2-2. 주요 응답 필드
```python
{
  "bizesId": "MA010120220800001127",    # 사업자 ID
  "bizesNm": "상호명",
  "brchNm": "지점명 (있으면 프랜차이즈)",
  "indsLclsNm": "대분류 (예: 음식)",
  "indsMclsNm": "중분류 (예: 한식)",
  "indsSclsNm": "소분류 (예: 한식음식점)",
  "adongCd": "11440660",
  "adongNm": "서교동",
  "ldongCd": "1144012100",       # 법정동 (10자리)
  "ldongNm": "동교동",
  "rdnmAdr": "도로명주소",
  "lon": 126.926331,             # 경도
  "lat": 37.559901,              # 위도
  # 총 39개 필드
}
```

### 2-3. 함정
- **매출 데이터 없음** — 매출은 서울 열린데이터광장에서 얻어야 함
- **시계열 없음** — 현재 스냅샷만. 월별로 수집해 시계열을 만들어야 함
- **프랜차이즈 판별**: `brchNm`(지점명) 필드가 있으면 프랜차이즈로 간주 가능

---

## 3. 국토교통부 — 상업업무용 실거래가

### 기본 정보
- **원본**: data.go.kr
- **환경변수**: `MOLIT_API_KEY`
- **엔드포인트**: `https://apis.data.go.kr/1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade`
- **제공 데이터**: 상업용 부동산 **매매** 실거래가 (**임대료는 없음**)

### 3-1. 호출 예시
```python
params = {
    "serviceKey": MOLIT_API_KEY,
    "LAWD_CD": "11440",       # 법정동코드 앞 5자리 (시군구 단위)
    "DEAL_YMD": "202406",     # 거래 연월
    "numOfRows": "10",
    "pageNo": "1",
}
```

### 3-2. 주요 응답 필드 (XML)
```xml
<item>
  <dealAmount>277,142</dealAmount>        <!-- 거래금액 (만원) -->
  <dealYear>2024</dealYear>
  <dealMonth>6</dealMonth>
  <dealDay>13</dealDay>
  <sggCd>11440</sggCd>                    <!-- 시군구 -->
  <sggNm>마포구</sggNm>
  <umdNm>서교동</umdNm>                    <!-- 읍면동 -->
  <buildingAr>76.09</buildingAr>          <!-- 건물면적 (㎡) -->
  <buildingUse>제2종근린생활</buildingUse> <!-- 건물용도 -->
  <buildingType>일반</buildingType>       <!-- 일반/집합 -->
  <dealingGbn>중개거래</dealingGbn>
  <buildYear>1958</buildYear>
</item>
```

### 3-3. 함정
- **XML 응답** (JSON 아님) — `xmltodict`로 파싱
- **매매가만** — 임대료(월세/보증금) 필요하면 별도 API("상업업무용 전월세 실거래가") 신청 필요
- `dealAmount` 단위는 **만원** (쉼표 포함된 문자열)

---

## 4. 행정안전부 — 주민등록 인구 (미완)

### 기본 정보
- **엔드포인트**: `https://apis.data.go.kr/1741000/admmPpltnHhStus/selectAdmmPpltnHhStus`
- **환경변수**: `MOIS_API_KEY`
- **상세기능**: 시도명·시군구명·행정동명·총인구·세대수 등 조회

### 4-1. 현재 상태
- 엔드포인트 확인됨 (행정안전부 API 페이지 기준)
- 요청 파라미터 **정확한 이름 미확인** → 테스트 시 타임아웃
- `ctpvNm`, `signguNm`, `adongNm` 등 시도했으나 응답 없음
- **작업 필요**: data.go.kr의 "미리보기" 버튼으로 실제 파라미터명 확인

### 4-2. 기대 용도 (MVP 편입 시)
- 행정동 단위 인구 변화 (젠트리피케이션 선행 지표)
- 연령대별 인구 분포 (젊은층 유입 여부)

---

## 5. 공통 참조 — 주요 행정동 코드 표

MVP 대상 서울 주요 상권의 행정동 코드 (8자리):

### 마포구 (홍대·합정·연남 권역)
| 동명 | 행정동 코드 | 비고 |
|---|---|---|
| **서교동** | **11440660** | 홍대입구역 |
| 연남동 | 11440710 | 연트럴파크 |
| 합정동 | 11440680 | 합정역 |
| 망원1동 | 11440690 | 망원시장·망리단길 |
| 망원2동 | 11440700 | |
| 상암동 | 11440740 | DMC |
| 공덕동 | 11440565 | 공덕역 |
| 성산1/2동 | 11440720/730 | |

### 성동구 (성수동 권역)
| 동명 | 행정동 코드 | 비고 |
|---|---|---|
| 성수1가1동 | 11215710 | 서울숲·성수 카페거리 |
| 성수1가2동 | — | (추가 확인 필요) |

### 확장 대상 (MVP v1 타겟 20개 상권 후보)
- 강남구: 역삼동, 삼성동, 청담동, 신사동(가로수길)
- 종로구: 삼청동, 혜화동
- 중구: 명동, 을지로
- 용산구: 이태원동, 한남동
- 서초구: 반포동, 서초동
- 송파구: 잠실동
- 관악구: 봉천동(샤로수길)

### 상권 코드 (TbgisTrdarRelm 기준, 발달상권)
| 상권 코드 | 상권명 |
|---|---|
| 3120103 | 홍대입구역(홍대) |
| 3120104 | 연남동(홍대) |
| 3120102 | 서교동(홍대) |
| 3120105 | 상수역(홍대) |
| 3120101 | 합정역 |
| 3120100 | 망원역 |
| 3120098 | DMC(디지털미디어시티) |
| 3120099 | 월드컵경기장역 |

### 서비스 업종 코드 예시 (일부)
| 코드 | 업종명 |
|---|---|
| CS100001 | 한식음식점 |
| CS100002 | 중식음식점 |
| CS100003 | 일식음식점 |
| CS100004 | 양식음식점 |
| CS100008 | 호프-간이주점 |
| CS100009 | 분식전문점 |
| CS100010 | 커피-음료 |
| CS300010 | 편의점 |
| CS200005 | 스포츠 강습 |

> 전체 100개 업종 코드는 첨부된 `(251128)소상공인시장진흥공단_.../*_업종분류(2302)_*.xlsx` 참고

---

## 6. 호출 시 일반 팁

### 페이지네이션
```python
all_rows = []
for start in range(1, 18000, 1000):
    end = start + 999
    data = call_api(start=start, end=end)
    rows = data.get("row", [])
    if not rows:
        break
    all_rows.extend(rows)
```

### 타임아웃
- 서울 열린데이터광장: 10~30초
- 공공데이터포털 (국토교통부/소상공인/행안부): 30초 권장 (응답 느림)

### 에러 코드 (서울)
- `INFO-000`: 정상
- `ERROR-500`: 서버 오류 (주로 서비스명 오류)
- `RESULT-10x`: 파라미터 오류

### 에러 코드 (공공데이터포털)
- `00`: 정상
- `03`: `NODATA_ERROR`
- `10`: `INVALID_REQUEST_PARAMETER_ERROR`
- `11`: `NO_MANDATORY_REQUEST_PARAMETERS_ERROR`
