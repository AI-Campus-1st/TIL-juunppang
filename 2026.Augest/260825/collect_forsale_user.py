import time
import requests
import pandas as pd

# collect_forsale.py
URL = 'https://realty.asil.kr/api_asil/data_sale_of_apt_nomal.aspx'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://asil.kr'
}

DATA = {
 'oidx': 1,
 'oby': 'down',
 'total': 20,
 }


def fetch(seq, page=1):
    res = requests.post(URL, data={**DATA, 'asil_bldcode': seq, 'focus_bldcode': seq, 'last_mm_num': (page-1)*20 }, headers=HEADERS, timeout=10)
    res.raise_for_status()
    return res.json()

def parse(datas, seq):
    detail = []
    for data in datas['list_result']:
        detail.append({
            'seq': seq,
            'uid': data.get('mm_uid', ''),
            '상세': data.get('FETR_DESC', ''),
            '중개사': data.get('BRKG_NM', ''),
            '매물유형': data.get('DEALTYPE_NM', ''),
            '동': data.get('BDONG_NM', ''),
            '층': data.get('CORES_FLR_CNT_NM', ''),
            '공급면적': data.get('CTRT_SPC', '') if data.get('CTRT_SPC') else data.get('SPLY_SPC', ''),
            '전용면적': data.get('EXCLS_SPC', ''),
            '매매가': data.get('DEAL_AMT', ''),
            '보증금': data.get('WRRNT_AMT', ''),
            '월세': data.get('LEASE_AMT', ''),
            '등록일': data.get('SVC_DATE_STRT', ''),
        })

    nxt = datas['next_page']
    return detail, nxt