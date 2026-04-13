"""
소상공인시장진흥공단 — 상가(상권)정보 API 검증

검증 항목:
- 제공하는 세부 API 목록 (상권 목록, 업종 분포, 임대료 등)
- 서울 주요 상권(홍대, 강남, 성수 등) 조회 가능 여부
- 업종별 점포 수, 개업/폐업 데이터 제공 여부
- 임대료 관련 데이터 포함 여부
"""

import json
import requests
import xmltodict
from api_test.config import SEMAS_API_KEY

# 소상공인시장진흥공단 상가(상권)정보 API
# 세부 API 엔드포인트 목록
ENDPOINTS = {
    "상권목록": "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInDong",
    "업종별점포": "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInUpjong",
    "상권내점포": "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInArea",
}

# 테스트 1: 행정동 기반 점포 조회 (서교동)
PARAMS_DONG = {
    "serviceKey": SEMAS_API_KEY,
    "divId": "adongCd",
    "key": "1144053000",      # 서울특별시 마포구 서교동
    "numOfRows": "10",
    "pageNo": "1",
    "type": "json",
}

# 테스트 2: 업종별 점포 조회 (커피음료)
PARAMS_UPJONG = {
    "serviceKey": SEMAS_API_KEY,
    "divId": "indsLclsCd",
    "key": "Q",               # 음식 대분류코드
    "numOfRows": "10",
    "pageNo": "1",
    "type": "json",
}


def call_api(name, url, params):
    print(f"\n--- {name} ---")
    print(f"[요청 URL] {url}")

    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"[응답 코드] {resp.status_code}")
        print(f"[Content-Type] {resp.headers.get('Content-Type', 'N/A')}")

        # JSON 파싱 시도
        try:
            data = resp.json()
            print(f"[응답 포맷] JSON")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
            return data
        except ValueError:
            # XML 파싱 시도
            try:
                data = xmltodict.parse(resp.text)
                print(f"[응답 포맷] XML")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
                return data
            except Exception:
                print(f"[응답 원문 (처음 2000자)]")
                print(resp.text[:2000])
                return None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API 호출 실패: {e}")
        return None


def test_api():
    print("=" * 60)
    print("소상공인시장진흥공단 — 상가(상권)정보 API 테스트")
    print("=" * 60)

    if not SEMAS_API_KEY or SEMAS_API_KEY == "your_key_here":
        print("[ERROR] SEMAS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    # 테스트 1: 행정동 내 점포 목록
    call_api(
        "테스트 1: 행정동(서교동) 점포 목록",
        ENDPOINTS["상권목록"],
        PARAMS_DONG,
    )

    # 테스트 2: 업종별 점포 조회
    call_api(
        "테스트 2: 업종별(음식) 점포 조회",
        ENDPOINTS["업종별점포"],
        PARAMS_UPJONG,
    )

    print("\n" + "-" * 60)
    print("[검증 체크리스트]")
    print("  - [ ] API 호출 성공 여부")
    print("  - [ ] 서교동(홍대) 점포 데이터 존재 여부")
    print("  - [ ] 업종(상권업종대분류/중분류/소분류) 구분 가능 여부")
    print("  - [ ] 점포 개업/폐업 일자 필드 존재 여부")
    print("  - [ ] 임대료 관련 필드 존재 여부")
    print("  - [ ] 프랜차이즈 vs 개인 구분 가능 여부")
    print("  - [ ] MVP 활용 가능 여부 판단")

    print("\n[참고] data.go.kr에서 이 API의 세부 오퍼레이션 목록을 확인하세요.")
    print("  상권정보 API는 여러 세부 API를 포함할 수 있습니다:")
    print("  - 상권 목록 조회")
    print("  - 상권 내 점포 조회")
    print("  - 업종별 점포 조회")
    print("  - 수정/폐업 점포 조회 등")


if __name__ == "__main__":
    test_api()
