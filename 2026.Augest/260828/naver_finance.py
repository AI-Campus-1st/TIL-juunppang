import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

URL = 'https://finance.naver.com/item/sise_day.naver'

HEADERS = {'User-Agent':'Mozilla 5.0'}

class NaverFinanceStock:

    def _fetch(self, code, page):
        res = requests.get(URL, params={'code':code,'page':page}, headers=HEADERS)
        res.raise_for_status
        return res.text

    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        rows = []
        trs = soup.select('table.type2 tr')
        for tr in trs:
            td = tr.select('td')
            if len(td) < 7 :
                continue
            plus_mius = td[2].select_one('em.bu_p').text.strip()
            amount = td[2].select_one('span.tah').text
            rows.append({
                '날짜': td[0].text.strip(),
                '종가': td[1].text,
                '전일비':f'{plus_mius} {amount}',
                '시가': td[3].text,
                '고가':td[4].text,
                '저가':td[5].text,
                '거래량':td[6].text,
            })
        return rows
    def get_stock(self, code, last_days=365):
        result = []

        for page in range(1, 101):
            rows = self._parse(self._fetch(code,page))

            if not rows:
                print(f'{page}페이지가 비어 있습니다. 크롤링 종료')
                break

            result.extend(rows)

            last_date = rows[0]['날짜']
            if datetime.strptime(last_date, '%Y.%m.%d') < datetime.now() - timedelta(365):
                print(f'{last_date}, 1년 이전 날짜까지 데이터크롤링 완료')
                break
            
            print(f'{page}페이지, 누적{len(result)}건 수집 최종{rows[-1]['날짜']} ')
            time.sleep(0.7)
        return result