```sql
--네이버 주식용 테이블 tb_nf_stock 과 금융위 주식용 테이블 tb_fsc_stock 로 각각 테이블을 생성하고 적재하시오.

--스키마는 둘 다 공통적으로bas_dt(DATE) / srtn_cd(CHAR 6) / itms_nm / clpr / vs / mkp / hipr / lopr / trqu / raw_id 를 가진다.

--일자 / 종목코드 / 종목명 / 종가 / 전일비 / 시가 / 고가 / 저가 / 거래량

--Naver Finance 쪽의 종목명은 NULL이다. 현재 테이블 구조를 어떻게 수정하면 좋을지 주석으로 작성하시오.

CREATE TABLE IF NOT EXISTS tb_nf_stock(
    bas_dt  DATE    NOT NULL,
    srtn_cd CHAR(6) NOT NULL,
    itms_nm VARCHAR(100),
    clpr    BIGINT,
    vs      BIGINT,
    mkp     BIGINT,
    hipr    BIGINT,
    lopr    BIGINT,
    trqu    BIGINT,
    raw_id  BIGINT,
    PRIMARY KEY (bas_dt, srtn_cd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS tb_fsc_stock(
    bas_dt  DATE    NOT NULL,
    srtn_cd CHAR(6) NOT NULL,
    itms_nm VARCHAR(100),
    clpr    BIGINT,
    vs      BIGINT,
    mkp     BIGINT,
    hipr    BIGINT,
    lopr    BIGINT,
    trqu    BIGINT,
    raw_id  BIGINT,
    PRIMARY KEY (bas_dt, srtn_cd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- tb_fsc_stock 테이블에서 질문에 바로 답하는 형태의 Mart 테이블 두 개를 만드시오.

-- (1) tb_mart_stock_monthly — 종목 × 월 집계
-- 기준: 종목코드 · 연월(YYYY-MM)

-- 집계 항목

-- 평균 종가 / 최고 종가 / 최저 종가 / 월초 종가 / 월말 종가

-- 거래량 합계 / 거래량 평균

-- 거래일 수 (평균의 신뢰도를 판단하기 위해)

-- 거래일 수가 10일 미만인 달은 제외할 것 (신규 상장·상장폐지 달)

CREATE TABLE IF NOT EXISTS tb_mart_stock_monthly(
    srtn_cd     CHAR(6) NOT NULL,
    ym          CHAR(7) NOT NULL,
    trd_days    INT,
    open_clpr   BIGINT,
    close_clpr  BIGINT,
    avg_clpr    BIGINT,
    max_clpr    BIGINT,
    min_clpr    BIGINT,
    sum_trqu    BIGINT,
    avg_trqu    BIGINT,
    PRIMARY KEY (srtn_cd, ym)
) ENGINE InnoDB DEFAULT CHARSET=utf8mb4;

-- (2) tb_mart_stock_daily — 파생 지표 추가 테이블
-- 추가 파생 지표

-- chg_pct — 전일 대비 변동률(%)

-- ma5 · ma20 — 5일·20일 이동평균

-- vol_ratio — 당일 거래량 ÷ 20일 평균 거래량

-- 반드시 종목별로 그룹화 한 뒤 계산할 것

-- 계산 전에 (종목코드, 날짜) 순으로 정렬할 것

CREATE TABLE IF NOT EXISTS tb_mart_stock_daily(
    bas_dt      DATE    NOT NULL,
    srtn_cd     CHAR(6) NOT NULL,
    clpr        BIGINT,
    trqu        BIGINT,
    chg_pct     DOUBLE,
    ma5         DOUBLE,
    ma20        DOUBLE,
    vol_ratio   DOUBLE,
    PRIMARY KEY (srtn_cd, bas_dt)
) ENGINE InnoDB DEFAULT CHARSET=utf8mb4;
```