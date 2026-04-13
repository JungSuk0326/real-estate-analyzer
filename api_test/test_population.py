"""
행정안전부 — 행정동별(통반단위) 주민등록 인구 및 세대현황 API 검증

검증 항목:
- 서울시 특정 동(마포구 서교동) 인구 조회
- 연령대별 인구 데이터 제공 여부
- 시계열 조회 가능 여부
"""

import json
import requests
import xmltodict
from api_test.config import MOIS_API_KEY

# 행정안전부 주민등록 인구 및 세대현황 API
BASE_URL = "https://apis.data.go.kr/1741000/admmPpltnHhStus/selectAdmmPpltnHhStus"

# 테스트 파라미터 - 서울특별시 마포구 서교동
PARAMS = {
    "serviceKey": MOIS_API_KEY,
    "ctpvNm": "서울특별시",     # 시도명
    "signguNm": "마포구",       # 시군구명
    "adongNm": "서교동",        # 행정동명
    "type": "json",
    "numOfRows": "10",
    "pageNo": "1",
}


def test_api():
    print("=" * 60)
    print("행정안전부 — 주민등록 인구 및 세대현황 API 테스트")
    print("=" * 60)

    if not MOIS_API_KEY or MOIS_API_KEY == "your_key_here":
        print("[ERROR] MOIS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    print(f"\n[요청 URL] {BASE_URL}")
    print(f"[파라미터] {PARAMS['ctpvNm']} {PARAMS['signguNm']} {PARAMS['adongNm']}")

    try:
        resp = requests.get(BASE_URL, params=PARAMS, timeout=30)
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
        print("  - [ ] 동 단위 인구수 데이터 존재 여부")
        print("  - [ ] 연령대별 인구 구분 가능 여부")
        print("  - [ ] 월별 시계열 데이터 제공 여부")
        print("  - [ ] MVP 활용 가능 여부 판단")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] API 호출 실패: {e}")
        print("\n[확인사항]")
        print("  1. API 키가 올바른지 확인")
        print("  2. data.go.kr에서 실제 엔드포인트 URL 확인")
        print("  3. 요청 파라미터명이 API 명세와 일치하는지 확인")


if __name__ == "__main__":
    test_api()
