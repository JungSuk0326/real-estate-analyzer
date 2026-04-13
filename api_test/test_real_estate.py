"""
국토교통부 — 상업업무용 부동산 매매 실거래가 자료 API 검증

검증 항목:
- 상가 거래 데이터 포함 여부
- 지역코드 기반 조회 (법정동 코드)
- 거래 금액, 면적, 거래일자 등 핵심 필드
- 최근 3년 데이터 조회 가능 여부
"""

import json
import requests
import xmltodict
from api_test.config import MOLIT_API_KEY

# 국토교통부 상업업무용 부동산 매매 실거래가
BASE_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcNrgTrade/getRTMSDataSvcNrgTrade"

# 테스트 파라미터 - 서울특별시 마포구, 2024년 6월
PARAMS = {
    "serviceKey": MOLIT_API_KEY,
    "LAWD_CD": "11440",      # 서울특별시 마포구 (법정동 앞 5자리)
    "DEAL_YMD": "202406",    # 거래 연월
    "numOfRows": "10",
    "pageNo": "1",
}


def test_api():
    print("=" * 60)
    print("국토교통부 — 상업업무용 부동산 매매 실거래가 API 테스트")
    print("=" * 60)

    if not MOLIT_API_KEY or MOLIT_API_KEY == "your_key_here":
        print("[ERROR] MOLIT_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    print(f"\n[요청 URL] {BASE_URL}")
    print(f"[파라미터] LAWD_CD={PARAMS['LAWD_CD']} (마포구), DEAL_YMD={PARAMS['DEAL_YMD']}")

    try:
        resp = requests.get(BASE_URL, params=PARAMS, timeout=10)
        print(f"\n[응답 코드] {resp.status_code}")
        print(f"[Content-Type] {resp.headers.get('Content-Type', 'N/A')}")

        # JSON 파싱 시도
        try:
            data = resp.json()
            print(f"[응답 포맷] JSON")
            print(f"\n[응답 데이터 (정렬 출력)]")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
        except ValueError:
            # XML 파싱 시도
            try:
                data = xmltodict.parse(resp.text)
                print(f"[응답 포맷] XML")
                print(f"\n[응답 데이터 (XML→Dict 변환)]")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
            except Exception:
                print(f"[응답 원문 (처음 2000자)]")
                print(resp.text[:2000])

        print("\n" + "-" * 60)
        print("[검증 체크리스트]")
        print("  - [ ] API 호출 성공 여부")
        print("  - [ ] 상가/상업용 거래 데이터 존재 여부")
        print("  - [ ] 거래금액(dealAmount) 필드 존재 여부")
        print("  - [ ] 전용면적(excluUseAr) 필드 존재 여부")
        print("  - [ ] 건물용도(usgNm) 구분 가능 여부")
        print("  - [ ] 법정동명(dealingGbn/sggNm) 필드 존재 여부")
        print("  - [ ] MVP 활용 가능 여부 판단")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] API 호출 실패: {e}")
        print("\n[확인사항]")
        print("  1. API 키가 올바른지 확인")
        print("  2. data.go.kr에서 실제 엔드포인트 URL 확인")
        print("  3. LAWD_CD(법정동코드)가 올바른지 확인 (마포구: 11440)")


if __name__ == "__main__":
    test_api()
