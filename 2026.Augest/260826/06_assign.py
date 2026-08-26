# 문항 1 순차 · 스레드 · 프로세스 속도 비교

# 같은 작업을 세 가지 방식으로 실행해 소요시간을 비교하시오.

# 대상은 로컬 Flask 서버를 활용하세요.

# 세 방식

# 순차 반복문

# multiprocessing.dummy.Pool(n).map (스레드)

# multiprocessing.Pool(n).map (프로세스)

# 워커 수 1 · 3 · 5 · 10 을 바꿔가며 측정해 표로 정리

# 측정 결과를 보고 두 방식의 차이가 어디서 오는지 2~3줄로 설명할 것 (힌트: 대기 시간, 풀 생성 비용 · 메모리 · 직렬화 제약도 함께 생각해볼 것)

import requests
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
import time

BASE = 'http://127.0.0.1:5000/item/{}'
URLS = [BASE.format(i) for i in range(1, 61)] 

def fetch(url):
    res = requests.get(url, timeout=10)
    return res.json()['id']

# 순차 처리

def run_seq(urls):
    return [fetch(url) for url in urls ]

# 멀티 스레드

def run_multi_thread(urls, n):
    with ThreadPool(n) as pool:
        return pool.map(fetch, urls)

# 멀티 프로세싱

def run_multi_proc(urls, n):
    with Pool(n) as pool:
        return pool.map(fetch, urls)

def timeit(fn, *args):
    t0 = time.perf_counter()
    out = fn(*args)
    return round(time.perf_counter() - t0, 2), len(out)

def main():
    result = []

    sec, cnt = timeit(run_seq, URLS)
    result.append({'방식': '순차', '소요시간': sec, '건수': cnt})
    print(f'순차            {sec:6.2f}초')

    for n in (1, 3, 5, 10):
        sec, cnt = timeit(run_multi_thread, URLS, n)
        result.append({'방식': '멀티스레드', '워커': n, '소요시간': sec, '건수': cnt})
        print(f'멀티스레드   {n:2d} {sec:6.2f}초')

    for n in (1, 3, 5, 10):
        sec, cnt = timeit(run_multi_proc, URLS, n)
        result.append({'방식': '멀티프로세스', '워커': n, '소요시간': sec, '건수': cnt})
        print(f'멀티프로세스 {n:2d} {sec:6.2f}초') 

    df = pd.DataFrame(result)
    df.to_csv('batch.csv', index=False, encoding='utf-8-sig')
    print('\n', df.pivot_table(index='워커', columns='방식', values='소요시간'))
        

if __name__ == '__main__':
    main()

# 두 방식의 차이(2~3줄)
# 1. 풀 생성비용은 스레드에 비해 프로세스가 더 크다.
# 2. 프로세스는 lamda, 세션 객체, 드라이버를 넘길 수 없는 직렬화 제약이 있다.
# 3. 스레딩은 하나의 프로세스안에 여러 작업자가 존재하는것과 같고(메모리 공유), 프로세싱은 여러 프로세스가 독립된 CPU와 메모리를 가지면서 프로그램을 실행하는 것.



# 문항 2 Scrapy 포팅 또는 httpx 비동기 전환 (택일)
# B. httpx 비동기 전환
# A 대상을 httpx.AsyncClient + asyncio.gather 로 다시 작성할 것

# asyncio.Semaphore 와 httpx.Limits 로 동시 수를 이중 제한할 것

# time.sleep 대신 await asyncio.sleep 을 쓸 것

# return_exceptions=True 로 부분 실패를 허용할 것

# 소요시간을 측정해볼 것

