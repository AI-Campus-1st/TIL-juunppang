import time
import requests
import pandas as pd

# collect_apt_user.py

URL = 'https://asil.kr/app/data/data_apt_list.jsp'
PARAMS = {
 'building': 'apt',
 'household': '50',
 'order': '0',
 'order_type': '0'}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://asil.kr/app/apt_list.jsp'
}

def fetch(dong):
    res = res = requests.get(URL, params={**PARAMS, 'dong':dong}, headers=HEADERS, timeout=10)
    res.raise_for_status()
    return res.json()

def parse(datas):
    apt_list = []
    for data in datas:
        apt_list.append({
            'seq': data.get('seq',''),
            '동': data.get('dongname', ''),
            '단지명': data.get('name',''),
            '세대수': data.get('household',''),
            '건축년도': data.get('movein', ''),
            '매물수': data.get('offer',''),
            '위도': data.get('lat',''),
            '경도': data.get('lng',''),
        })
    return apt_list