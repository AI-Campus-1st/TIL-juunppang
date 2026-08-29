import logging
import sys
import os
from dotenv import load_dotenv
from pymysql.cursors import DictCursor
import pymysql
import pandas as pd

load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'analysis'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME2', 'fsc_db'),
    'charset': 'utf8mb4',
    'cursorclass' : DictCursor
}

def connect():
    conn = pymysql.connect(**db_config)
    return conn



logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler("mart_report.log", encoding="utf-8")])
log = logging.getLogger("mart")

DAILY_COLS = ['bas_dt', 'srtn_cd', 'clpr', 'trqu', 'chg_pct', 'ma5', 'ma20', 'vol_ratio']

MONTHLY_COLS = ['srtn_cd', 'ym', 'trd_days', 'open_clpr', 'close_clpr', 'avg_clpr', 'max_clpr', 'min_clpr', 'sum_trqu', 'avg_trqu']

BATCH = 500

SOURCE = 'fsc'

# clean 테이블 데이터 load
def load_clean(table : str) -> pd.DataFrame:
    conn =connect()
    with conn.cursor() as cur:
        cur.execute(f'SELECT bas_dt, srtn_cd, itms_nm, clpr, mkp, hipr, lopr, trqu FROM {table}')
        rows = cur.fetchall()
    conn.close()

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df['bas_dt'] = pd.to_datetime(df['bas_dt'])
    return df

# 일 마트 집계
def build_daily(df:pd.DataFrame) -> pd.DataFrame:
    d = df.sort_values(['srtn_cd', 'bas_dt']).copy()
    g = d.groupby('srtn_cd')
#.pct_change = (현재값 - 이전값)/ 이전값
    d['chg_pct'] = (g['clpr'].pct_change(fill_method=None)*100).round(2)
    d['ma5'] = g['clpr'].transform(lambda s: s.rolling(5).mean()).round(1)
    d['ma20'] = g['clpr'].transform(lambda s: s.rolling(5).mean()).round(1)
    vol_ma20 = g['trqu'].transform(lambda s: s.rolling(20).mean())
    d['vol_ratio'] = (d['trqu'] / vol_ma20).round(2)
    return d[DAILY_COLS]

# 월 마트 집계
def build_monthly(df:pd.DataFrame, min_days:int = 10) -> pd.DataFrame:
    d = df.sort_values(['srtn_cd', 'bas_dt']).copy()
    d['ym'] = d['bas_dt'].dt.strftime('%Y-%m')

    m = (d.groupby(['srtn_cd', 'ym'], as_index =False)
            .agg(trd_days=("bas_dt", "count"),
                open_clpr=("clpr", "first"),
                close_clpr=("clpr", "last"),
                avg_clpr=("clpr", "mean"),
                max_clpr=("clpr", "max"),
                min_clpr=("clpr", "min"),
                sum_trqu=("trqu", "sum"),
                avg_trqu=("trqu", "mean")))

    before = len(m)
    m = m[m['trd_days'] >= min_days]
    if before != len(m):
        log.info('거래일 %d일 미만 %d행 제거', min_days, before - len(m))

    for c in ('avg_clpr', 'avg_trqu'):
        m[c] = m[c].round(0)
    return m[MONTHLY_COLS]

# MONTHLY_COLS = {'srtn_cd', 'ym', 'trd_days', 'open_clpr', 'close_clpr', 'avg_clpr', 'max_clpr', 'min_clpr', 'sum_trqu', 'avg_trqu'}

# 데이터 insert 함수
def insert_batch(table: str, cols: list, df:pd.DataFrame) -> int:
    conn = connect()
    if df.empty:
        return 0
    sql = (f'INSERT INTO {table} ({','.join(cols)})'
           f'VALUES ({','.join(['%s'] * len(cols))})'
           f'ON DUPLICATE KEY UPDATE {cols[-1]}=VALUES({cols[-1]})')
    
    out = df.copy()
    if 'bas_dt' in out:
        out['bas_dt'] = pd.to_datetime(out['bas_dt']).dt.strftime('%Y-%m-%d')

    # Nan값 처리
    params = [tuple(None if pd.isna(v) else v for v in row) for row in out[cols].values]

    for i in range(0, len(params), BATCH):
        with conn.cursor() as cur:
            cur.executemany(sql, params[i:i+BATCH])
        conn.commit()
    conn.close()
    return len(params)

def main():
    table = 'tb_fsc_stock'

    df = load_clean(table)
    if df.empty:
        log.warning("[MART] %s 가 비어 있습니다. cleansing 먼저 실행하세요.", table)
        return
    
    log.info("[MART] Clean %d행 (%s ~ %s · 종목 %d개)",
             len(df), df["bas_dt"].min().date(), df["bas_dt"].max().date(),
             df["srtn_cd"].nunique())

    daily = build_daily(df)
    monthly = build_monthly(df)

    n1 = insert_batch('tb_mart_stock_daily', DAILY_COLS, daily)
    n2 = insert_batch('tb_mart_stock_monthly', MONTHLY_COLS, monthly)

    log.info('[MART:%s] 적재 완료 - daily %d행 · monthly %d행', SOURCE, n1, n2)

if __name__ == '__main__' :
    main()


