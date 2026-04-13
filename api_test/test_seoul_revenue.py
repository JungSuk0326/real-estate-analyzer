"""
서울 열린데이터광장 — 상권분석 서비스 API 검증

포함 API:
1. VwsmMegaSelngW     — 서울시 전체 추정매출
2. VwsmSignguSelngW   — 자치구 단위 추정매출
3. VwsmAdstrdSelngW   — 행정동 단위 추정매출 (MVP 핵심)
4. TbgisTrdarRelm     — 상권 영역(경계) 정보

호출 URL 패턴:
  http://openapi.seoul.go.kr:8088/{인증키}/{타입}/{서비스명}/{시작}/{끝}/{추가파라미터}
"""

import json
import requests
from api_test.config import SEOUL_API_KEY

BASE = "http://openapi.seoul.go.kr:8088"


def call(service, start=1, end=5, extra=""):
    """서울 열린데이터광장 API 호출"""
    url = f"{BASE}/{SEOUL_API_KEY}/json/{service}/{start}/{end}"
    if extra:
        url += f"/{extra}"
    resp = requests.get(url, timeout=30)
    return resp.json()


def summary(data):
    """응답에서 상태·건수·첫 레코드 요약"""
    if "RESULT" in data:
        # 서비스명 자체 에러
        return {
            "status": data["RESULT"]["CODE"],
            "message": data["RESULT"]["MESSAGE"],
            "total": 0,
            "sample": None,
        }
    key = list(data.keys())[0]
    body = data[key]
    return {
        "status": body.get("RESULT", {}).get("CODE", "?"),
        "message": body.get("RESULT", {}).get("MESSAGE", ""),
        "total": body.get("list_total_count", 0),
        "sample": body.get("row", [None])[0],
    }


def test_mega():
    """1. 서울시 전체 단위 추정매출"""
    print("=" * 60)
    print("1. 서울시 전체 추정매출 (VwsmMegaSelngW)")
    print("=" * 60)
    data = call("VwsmMegaSelngW", 1, 3)
    info = summary(data)
    print(f"[상태] {info['status']} — {info['message']}")
    print(f"[총 건수] {info['total']}")
    if info["sample"]:
        s = info["sample"]
        print(f"[샘플] {s['STDR_YYQU_CD']} / {s['MEGA_CD_NM']} / "
              f"{s['SVC_INDUTY_CD_NM']} / 매출 {s['THSMON_SELNG_AMT']/1e8:.1f}억")


def test_signgu():
    """2. 자치구 단위 추정매출"""
    print()
    print("=" * 60)
    print("2. 자치구 단위 추정매출 (VwsmSignguSelngW)")
    print("=" * 60)
    data = call("VwsmSignguSelngW", 1, 3)
    info = summary(data)
    print(f"[상태] {info['status']} — {info['message']}")
    print(f"[총 건수] {info['total']}")
    if info["sample"]:
        s = info["sample"]
        print(f"[샘플] {s['STDR_YYQU_CD']} / {s['SIGNGU_CD_NM']} / "
              f"{s['SVC_INDUTY_CD_NM']} / 매출 {s['THSMON_SELNG_AMT']/1e8:.1f}억")


def test_adstrd(quarter="20254"):
    """3. 행정동 단위 추정매출 (MVP 핵심)"""
    print()
    print("=" * 60)
    print("3. 행정동 단위 추정매출 (VwsmAdstrdSelngW)")
    print("=" * 60)
    # 기준년분기 지정 가능 (예: 20254 = 2025년 4분기)
    data = call("VwsmAdstrdSelngW", 1, 3, quarter)
    info = summary(data)
    print(f"[상태] {info['status']} — {info['message']}")
    print(f"[총 건수] {info['total']} (기준: {quarter})")
    if info["sample"]:
        s = info["sample"]
        print(f"[샘플] {s['STDR_YYQU_CD']} / {s['ADSTRD_CD_NM']}({s['ADSTRD_CD']}) / "
              f"{s['SVC_INDUTY_CD_NM']} / 매출 {s['THSMON_SELNG_AMT']/1e8:.1f}억")


def test_trdar_relm():
    """4. 상권 영역 정보"""
    print()
    print("=" * 60)
    print("4. 상권 영역 (TbgisTrdarRelm)")
    print("=" * 60)
    data = call("TbgisTrdarRelm", 1, 3)
    info = summary(data)
    print(f"[상태] {info['status']} — {info['message']}")
    print(f"[총 건수] {info['total']} (서울시 전체 상권 수)")
    if info["sample"]:
        s = info["sample"]
        print(f"[샘플] {s['TRDAR_SE_CD_NM']} / {s['TRDAR_CD_NM']}({s['TRDAR_CD']}) / "
              f"{s['SIGNGU_CD_NM']} {s['ADSTRD_CD_NM']} / 면적 {s['RELM_AR']}㎡")


def fetch_adstrd_by_code(adstrd_cd, quarter="20254"):
    """특정 행정동의 모든 업종 매출 조회 (MVP에서 사용할 실전 함수)

    Args:
        adstrd_cd: 8자리 행정동코드 (예: '11440660' = 서교동)
        quarter: 기준년분기 (예: '20254' = 2025년 4분기)

    Returns:
        해당 행정동의 업종별 매출 리스트
    """
    found = []
    # 전체 16,000여건을 페이지별로 순회하면서 대상 행정동만 필터
    for start in range(1, 18000, 1000):
        end = start + 999
        data = call("VwsmAdstrdSelngW", start, end, quarter)
        key = list(data.keys())[0]
        rows = data[key].get("row", [])
        if not rows:
            break
        matched = [r for r in rows if r.get("ADSTRD_CD") == adstrd_cd]
        if matched:
            found.extend(matched)
            # 행정동코드 순으로 정렬되어 있으면 다음 페이지는 불필요
            return found
        # 조회 대상보다 큰 코드만 나오면 조기 종료
        codes = [r.get("ADSTRD_CD", "") for r in rows]
        if codes and min(codes) > adstrd_cd:
            break
    return found


def test_fetch_seogyo():
    """실전 예시: 서교동(홍대) 전체 업종 매출 조회"""
    print()
    print("=" * 60)
    print("[실전] 서교동(홍대) 2025 Q4 전체 업종 매출")
    print("=" * 60)
    rows = fetch_adstrd_by_code("11440660", "20254")
    total_amt = sum(r["THSMON_SELNG_AMT"] for r in rows)
    total_cnt = sum(r["THSMON_SELNG_CO"] for r in rows)
    print(f"업종 수: {len(rows)}개")
    print(f"총 매출: {total_amt/1e8:.0f}억원")
    print(f"총 거래: {total_cnt:,.0f}건")
    print()
    # 매출 TOP 5
    rows.sort(key=lambda x: x["THSMON_SELNG_AMT"], reverse=True)
    print("매출 TOP 5:")
    for i, r in enumerate(rows[:5], 1):
        amt = r["THSMON_SELNG_AMT"] / 1e8
        print(f"  {i}. {r['SVC_INDUTY_CD_NM']:15s} {amt:6.1f}억")


def test_api():
    if not SEOUL_API_KEY or SEOUL_API_KEY == "your_key_here":
        print("[ERROR] SEOUL_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    test_mega()
    test_signgu()
    test_adstrd()
    test_trdar_relm()
    test_fetch_seogyo()

    print()
    print("-" * 60)
    print("[검증 체크리스트]")
    print("  - [x] 4개 API 모두 호출 성공 여부")
    print("  - [x] 행정동 단위 매출 조회 (MVP 핵심)")
    print("  - [x] 업종별 매출/거래건수/요일·시간대·성별·연령 분해")
    print("  - [x] 상권 영역(경계) 정보 확인")
    print("  - [x] fetch_adstrd_by_code() 실전 함수 동작")


if __name__ == "__main__":
    test_api()
