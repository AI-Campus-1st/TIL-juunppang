# main.py
import logging
import os
import random
import sys
import time
from datetime import datetime

import pandas as pd
import requests

from collect_apt_user import fetch as fetch_apt, parse as parse_apt
from collect_forsale_user import fetch as fetch_sale, parse as parse_sale

# ─────────────── 설정 ───────────────
DELAY = 0.7
MAX_PAGE = 50 # 매물 1000건 기준

QUEUE, OUT, FAILED_APT, FAILED_FORSALE = "apts.csv", "forsales.csv", "failed_apt.csv", "failed_forsale.csv"

# 테스트용 행정동 (강동구) — 실제로는 행정안전부 법정동코드 데이터 활용
DONG_CODES = {
    '1174010100',
    '1174010200',
    '1174010300',
    '1174010500',
	'1174010600',
	'1174010700',
	'1174010800',
	'1174010900',
	'1174011000',
}
DONG_CSV = "법정동코드_서울.csv" # https://www.code.go.kr/stdcode/regCodeL.do 에서 다운로드 받아서 csv로 변환

# ─────────────── 로깅 ───────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('report.log', encoding='utf-8'),
    ],
)
log = logging.getLogger("AsilCrawler")

# ─────────────── 재시도 ───────────────
MAX_TRIES = 4
RETRY_STATUS = {429, 500, 502, 503, 504}         # 다시 보내면 달라질 수 있는 것
GIVEUP_STATUS = {400, 401, 403, 404, 410}        # 다시 보내도 소용없는 것

class GiveUp(Exception):
    """재시도해도 소용없는 오류."""
    

def with_retry(fn, *args, **kwargs):
    """collect_*.py 의 fetch 를 감싸 지수 백오프 재시도를 붙인다."""
    reason = ''
    for i in range(MAX_TRIES):
        try:
            return fn(*args, **kwargs)

        # 응답코드 처리
        except requests.HTTPError as e:                  # raise_for_status 처리
            code = e.response.status_code if e.response is not None else None
            if code in GIVEUP_STATUS:
                raise GiveUp(f"HTTP {code}")             # 404·400 → 즉시 포기
            if code not in RETRY_STATUS:
                raise                                    # 그 밖의 4xx 도 포기
            reason = f"HTTP {code}"
            wait = int(e.response.headers.get("Retry-After", 0) or 0) or 2 ** i

        # 연결 에러 (서버 먹통상태)
        except (requests.Timeout, requests.ConnectionError) as e:
            # 에러 클래스명 가져오는 방법
            reason = type(e).__name__
            wait = 2 ** i

        wait += random.random()                          # 지터 (랜덤 시간 추가)
        log.warning("재시도 %d/%d · %s · %.1f초 대기", i + 1, MAX_TRIES - 1, reason, wait)
        time.sleep(wait)
    else:
        raise RuntimeError(f"{MAX_TRIES}회 시도 실패 ({reason})")

# ─────────────── 1단계 : 아파트 목록 수집 ───────────────
def stage_apt(codes):
    log.info("[1단계] 시작 — 행정동 %d개 · 지연 %.1f초", len(codes), DELAY)
    
    # collected_at 기록용
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result, failed = [], []
    stat = {"ok": 0, "fail": 0, "skip": 0}

    for i, dong in enumerate(codes, 1):
        try:
            rows = parse_apt(with_retry(fetch_apt, dong))

            if not rows: # 아파트가 없는 동
                stat["skip"] += 1
                log.info("[%d/%d] %s · 결과 없음 — 건너뜀", i, len(codes), dong)
                continue

            for r in rows:
                result.append({
                    **r,
                    "seq": r["seq"], "dong": r["동"], "apt_name": r["단지명"],
                    "dong_code": dong, "household": r["세대수"],
                    "movein": r["건축년도"], "offer": r["매물수"],
                    "lat": r["위도"], "lng": r["경도"],
                    "status": "pending", "collected_at": now,
                })
            stat["ok"] += 1
            log.info("[%d/%d] %s · %d건 · 누적 %d건", i, len(codes), dong, len(rows), len(result))

        except GiveUp as e:
            stat["fail"] += 1
            failed.append({"key": dong, "error": "GiveUp", "detail": str(e)})
            log.warning("[%d/%d] %s 포기 : %s", i, len(codes), dong, e)

        except Exception as e: # 크롤러가 멈추지 않도록 예외처리
            stat["fail"] += 1
            failed.append({"key": dong, "error": type(e).__name__, "detail": str(e)[:200]})
            log.warning("[%d/%d] %s 실패 : %s", i, len(codes), dong, type(e).__name__)

        finally:
            time.sleep(DELAY) # 성공·실패와 무관하게

    df = pd.DataFrame(result).drop_duplicates(subset=["seq"])
    df.to_csv(QUEUE, index=False)

    pd.DataFrame(failed).to_csv(FAILED_APT, index=False)
    log.error("실패 %d건 → %s", len(rows), FAILED_APT)
    
    log.info("[1단계] 완료 — 성공 %(ok)d · 실패 %(fail)d · 건너뜀 %(skip)d", stat)
    log.info("%s 저장 (%d건)", QUEUE, len(df))

# ─────────────── 2단계 : 매물 수집 ───────────────
def collect_one(seq):
    """한 단지의 전체 페이지. 종료조건 3중 — 빈 응답 · next_page · 상한"""
    result, page, has_next = [], 1, True
    while has_next and page <= MAX_PAGE:
        rows, has_next = parse_sale(with_retry(fetch_sale, seq, page), seq)
        if not rows:
            break
        result.extend(rows)
        page += 1
        time.sleep(DELAY)
    return result

def stage_forsale(q):
    # 수집 대상 - pending
    todo = q[q["status"] == 'pending']

    log.info("[2단계] 시작 — 대상 %d건 / 전체 %d건", len(todo), len(q))

    result, failed = [], []
    stat = {"ok": 0, "fail": 0, "skip": 0}

    for i, seq in enumerate(todo["seq"], 1):
        try:
            rows = collect_one(seq)

            if not rows:
                stat["skip"] += 1
                q.loc[q["seq"] == seq, "status"] = "empty"
                log.info("[%d/%d] seq=%s 매물 없음 — 건너뜀", i, len(todo), seq)
                continue

            result.extend(rows)
            stat["ok"] += 1
            q.loc[q["seq"] == seq, "status"] = "done" # 체크포인트
            log.info("[%d/%d] seq=%s · %d건 · 누적 %d건", i, len(todo), seq, len(rows), len(result))

        except GiveUp as e:
            stat["fail"] += 1
            failed.append({"seq": seq, "error": "GiveUp", "detail": str(e)})
            q.loc[q["seq"] == seq, "status"] = "failed"
            log.warning("[%d/%d] seq=%s 포기 : %s", i, len(todo), seq, e)

        except Exception as e:
            stat["fail"] += 1
            failed.append({"seq": seq, "error": type(e).__name__, "detail": str(e)[:200]})
            q.loc[q["seq"] == seq, "status"] = "failed"
            log.warning("[%d/%d] seq=%s 실패 : %s", i, len(todo), seq, type(e).__name__)

        finally:
            time.sleep(DELAY)

    if result:
        header = not os.path.exists(OUT)
        # 추가적으로 수집된 매물 데이터는 append 처리
        pd.DataFrame(result).to_csv(OUT, mode="a", header=header, index=False)

    # queue 파일에 임시 데이터들 제외하고 상태 최신화
    q[~q["_tmp"]].drop(columns=["_tmp"]).to_csv(QUEUE, index=False)
    
    pd.DataFrame(failed).to_csv(FAILED_FORSALE, index=False)
    log.error("실패 %d건 → %s", len(rows), FAILED_FORSALE)

    log.info("[2단계] 완료 — 성공 %(ok)d · 실패 %(fail)d · 건너뜀 %(skip)d", stat)
    log.info("남은 pending %d건", int((q[~q["_tmp"]]["status"] == "pending").sum()))


# ─────────────── 진입점 ───────────────
if __name__ == "__main__":
    # 아파트 목록 수집 (codes: 법정동 코드 전달)
    if os.path.exists(DONG_CSV):
        d = pd.read_csv(DONG_CSV, dtype=str, encoding="utf-8-sig")
        codes = d[d["법정동명"].map(lambda x: len(str(x).split()) > 2)]["법정동코드"].tolist()
    else:
        codes = DONG_CODES
        log.warning("%s 가 없어 테스트용 %d개로 진행합니다", DONG_CSV, len(codes))

    # 아파트 목록 수집
    stage_apt(codes)

    # Queue 확인 (아파트 목록으로 매물 수집)
    if not os.path.exists(QUEUE):
        sys.exit(f"{QUEUE} 가 없습니다. 아파트 목록이 제대로 수집되는지 확인해주세요.")

    q = pd.read_csv(QUEUE, dtype={"seq": str})

    # 일부 실패 처리를 위함, 실패 발생했을 때도 크롤러가 멈추지 않도록 검증
    INJECT = 3
    # 실패한 아파트 매물 수집 재시도 or pending 처리
    RETRY_FAILED = False

    q["_tmp"] = False # 주입분 표시용
    if INJECT:
        fake = q.head(INJECT).copy()
        fake["seq"] = [f"___없는seq_{i}___" for i in range(INJECT)]
        fake["status"] = "pending"
        fake["_tmp"] = True 
        q = pd.concat([fake, q], ignore_index=True)
        log.warning("검증 모드 — 존재하지 않는 seq %d건 주입 (저장에선 제외)", INJECT)
    
    # 매물 목록 수집
    stage_forsale(q)
    
    log.info("[최종] 아실 매물 크롤링 완료")