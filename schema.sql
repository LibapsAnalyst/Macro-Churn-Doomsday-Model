-- [1] 내부 고객 마스터 테이블 (Internal)
CREATE TABLE USER_MASTER (
    user_id VARCHAR(50) PRIMARY KEY,
    vip_tier VARCHAR(20),       -- VVIP, VIP, NORMAL
    age_group INT,              -- 20, 30, 40... (외부 데이터 브릿지 키)
    region_code VARCHAR(10),    -- 시도 단위 지역 코드 (외부 데이터 브릿지 키)
    tenure_months INT           -- 가입 기간
);

-- [2] 내부 고객 결제/활동 로그 (Internal)
CREATE TABLE TRANSACTION_LOG (
    tx_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) FOREIGN KEY,
    tx_date DATE,
    tx_amount DECIMAL(15,2),
    rfm_score INT               -- Recency, Frequency, Monetary 종합 지수
);

-- [3] 외부 거시경제 지표 - 통계청/KOSIS (External)
CREATE TABLE MACRO_KOSIS_DATA (
    base_year_month VARCHAR(7) PRIMARY KEY, -- YYYY-MM
    region_code VARCHAR(10),                -- 브릿지 키
    age_group INT,                          -- 브릿지 키
    avg_household_income DECIMAL(15,2),     -- 평균 가구 소득
    household_debt_idx DECIMAL(5,2)         -- 가계 대출 지표
);

-- [4] 외부 금융 지표 - DART/한국은행 (External)
CREATE TABLE MACRO_FINANCE_DATA (
    base_year_month VARCHAR(7) PRIMARY KEY, -- YYYY-MM
    base_interest_rate DECIMAL(4,2),        -- 기준 금리 / 코픽스 금리
    cpi_idx DECIMAL(5,2)                    -- 소비자물가지수(인플레이션)
);