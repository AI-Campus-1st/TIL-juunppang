import time
from datetime import datetime
import os
import json
import hashlib
import pandas as pd
import pymysql
from naver_finance import NaverFinanceStock
from dotenv import load_dotenv

load_dotenv()

URL = 'https://finance.naver.com/item/sise_day.naver'

CODES = ["005930", "000660", "035420", "051910", "005380",
         "006400", "035720", "068270", "105560", "055550"]

SOURCE = 'naver_finance'

HASHING = ['날짜', '종목코드']

BATCH = 500

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'analysis'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME2', 'fsc_db'),
    'charset': 'utf8mb4'
}

INSERT_SQL = """
            INSERT INTO raw_item(source, url, collected_at, payload, content_hash)
                VALUES(%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    payload = VALUES(payload),
                    collected_at = NOW()
        """


def connect():
    conn = pymysql.connect(**db_config)
    return conn

def main():
    result = []
    for code in CODES:
        naver_finance_api = NaverFinanceStock()
        items = naver_finance_api.get_stock(code, 365)
        items = [{**item, '종목코드': code} for item in items]
        result.extend(items)
        time.sleep(0.7)

    df = pd.DataFrame(result)
    collected_at = datetime.now()

    rows = []
    for item in df.to_dict(orient='records'):
        payload = json.dumps(item, ensure_ascii=False),
        key_str = '|'.join([SOURCE]+[item[c] for c in HASHING])
        content_hash = hashlib.sha256(key_str.encode()).hexdigest()
        rows.append((SOURCE, URL, collected_at, payload, content_hash))

    conn = connect()
    try:
        for i in range(0, len(rows), BATCH):
            with conn.cursor() as cur:
                cur.executemany(INSERT_SQL, rows[i:i+BATCH])
                conn.commit()
                cur.close()
                print(f'{SOURCE} · {len(rows)}건 적재 완료!')

    except Exception as e:
        print('알 수 없는 오류 발생:', e)

    finally:
        conn.close()

if __name__ == '__main__':
    main()