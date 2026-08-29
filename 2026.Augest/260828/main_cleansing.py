import json
import logging
import os
import sys
from datetime import datetime
import re
import pandas as pd
import pymysql
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler("cleansing_report.log", encoding="utf-8")])
log = logging.getLogger("cleansing")

SRC = { 
    'nf':('naver_finance', 'tb_nf_stock'),
    'fsc':('fsc_api', 'tb_fsc_stock')
}

BATCH = 500

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'analysis'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME2', 'fsc_db'),
    'charset': 'utf8mb4'
}

def connect():
    conn = pymysql.connect(**db_config)
    return conn

#정제 함수 
def to_num(t: str) -> int:
    m = re.search(r'\d+', re.sub(r'[^\d\-]','',t))
    return int(m.group()) if m else None

# 전일비 처리용
def signed_vs(t: str) -> int:
    if '상승' in t:
        return to_num(t)
    elif '하락' in t:
        return -to_num(t)
    return 0

# 날짜 변환 함수
def to_date(d : str) -> datetime:
    try:
        return datetime.strptime(d, '%Y.%m.%d')
    except ValueError:
        ...
    try:
        return datetime.strptime(d, '%Y%m%d')
    except ValueError:
        ...
    return None

def clean_naver(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "bas_dt":  df["날짜"].apply(to_date),
        "srtn_cd": df["종목코드"].astype(str).str.zfill(6),
        "itms_nm": None,
        "clpr":    df["종가"].apply(to_num),
        "vs":      df["전일비"].apply(signed_vs),
        "mkp":     df["시가"].apply(to_num),
        "hipr":    df["고가"].apply(to_num),
        "lopr":    df["저가"].apply(to_num),
        "trqu":    df["거래량"].apply(to_num),
        "raw_id":  df["raw_id"],
    })

def clean_fsc(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "bas_dt":  df["basDt"].apply(to_date),
        "srtn_cd": df["srtnCd"].astype(str).str.zfill(6),
        "itms_nm": df["itmsNm"].astype(str).str.strip(),
        "clpr":    df["clpr"].apply(to_num),
        "vs":      df["vs"].apply(to_num),
        "mkp":     df["mkp"].apply(to_num),
        "hipr":    df["hipr"].apply(to_num),
        "lopr":    df["lopr"].apply(to_num),
        "trqu":    df["trqu"].apply(to_num),
        "raw_id":  df["raw_id"],
    })

# 정제 함수 설정
CLEANER = {"nf": clean_naver, "fsc": clean_fsc}
COLS = ["bas_dt", "srtn_cd", "itms_nm", "clpr", "vs", "mkp",
        "hipr", "lopr", "trqu", "raw_id"]

def main(src:str):
    source, table = SRC[src]
    conn = connect()

    #데이터 갯수 확인
    with conn.cursor() as cur:
        cur.execute(f'SELECT COUNT(*) FROM raw_item WHERE source= %s',(source,))
        total = cur.fetchone()[0]

        if not total:
            log.warning("[CLEAN:%s] raw_item 에 source='%s 데이터가 없습니다.", src, source)
            cur.close()
            conn.close()
            return
    log.info("[CLEAN:%s] Raw %d건 → %s (배치 %d)", src, total, table, BATCH)

    insert_sql = f"""
        INSERT INTO {table} ({','.join(COLS)})
                VALUES ({','.join(['%s']*len(COLS))})
                ON DUPLICATE KEY UPDATE clpr=VALUES(clpr), trqu=VALUES(trqu)
    """

    frames = []
    offset = 0
    # 원래는 정제 함수 적용 시 변환 실패도 집계해야함.
    stat = {"read": 0, "written": 0, "dup": 0}

    while offset < total:
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT raw_id, payload FROM raw_item WHERE source = %s "
                "ORDER BY raw_id LIMIT %s OFFSET %s"), (source, BATCH, offset))
            chunk = cur.fetchall()

            if not chunk:
                break

            raw = pd.DataFrame(
                [{**json.loads(p), 'raw_id': rid} for rid, p in chunk]
            )

            stat['read'] += len(raw)
            cleaned = CLEANER[src](raw)

            n0 = len(cleaned)
            cleaned = cleaned.drop_duplicates(subset=['bas_dt', 'srtn_cd'], keep='last')
            stat['dup'] += n0 - len(cleaned)

            cleaned['bas_dt'] = cleaned['bas_dt'].dt.strftime('%Y-%m-%d')
            params = [tuple(row) for row in cleaned[COLS].values]

            with conn.cursor() as cur:
                cur.executemany(insert_sql, params)
            conn.commit()
            stat['written'] += len(params)

            frames.append(cleaned)
            offset += BATCH
            log.info(' 적재 %d / %d', min(offset, total), total)

        report(pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(),
           stat, src, table)
    conn.close()

def report(df:pd.DataFrame, stat: dict, src: str, table: str):
    log.info("─────── 정제 요약 : %s → %s ───────", src, table)
    log.info("변환 건수      읽음 %d · 적재 %d", stat["read"], stat["written"])
    if df.empty:
        log.warning("적재된 행이 없습니다.")
        return

    d = pd.to_datetime(df["bas_dt"])
    log.info("기간           %s ~ %s", d.min().date(), d.max().date())
    log.info("종목수         %d", df["srtn_cd"].nunique())

    dup_rate = round(stat["dup"] / max(stat["read"], 1) * 100, 2)
    log.info("중복률         %.2f%% (중복 제거 %d건)", dup_rate, stat["dup"])

# ═══════════════ 진입점 ═══════════════
if __name__ == "__main__":
    for s in ['nf', 'fsc']:
        main(s)

# naver finance에 없는 종목명은 따로 종목코드 & 종목명 테이블을 만들어 join해서 붙히는 형태로 가면 될꺼 같다. 

