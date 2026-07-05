import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# [1] System Config & Seed (재현성 확보)
# ---------------------------------------------------------
np.random.seed(42)
NUM_USERS = 5000
REGIONS = ['SEOUL', 'GYEONGGI', 'BUSAN', 'DAEGU']
AGE_GROUPS = [20, 30, 40, 50]
MONTHS = pd.date_range(start='2022-01-01', end='2023-12-31', freq='MS')

# ---------------------------------------------------------
# [2] External Data: Macro Indicators (거시경제 둠스클록 지표)
# ---------------------------------------------------------
def generate_macro_data():
    """
    통계청 및 한은 API를 가정한 거시경제 지표 생성.
    시간이 지날수록 고금리/고부채 국면으로 진입하도록 시계열 설계.
    """
    finance_data = []
    base_rate = 1.25  # 2022년 초 저금리 가정
    
    for dt in MONTHS:
        ym = dt.strftime('%Y-%m')
        # 금리는 매달 점진적 상승 (둠스클록 가속)
        base_rate += np.random.uniform(0.0, 0.25) 
        cpi = 100 + (base_rate * 2) + np.random.normal(0, 1)
        finance_data.append({'year_month': ym, 'interest_rate': round(base_rate, 2), 'cpi': round(cpi, 2)})
        
    df_finance = pd.DataFrame(finance_data)
    
    # 지역/연령별 가계부채 지표 (KOSIS 가정)
    kosis_data = []
    for dt in MONTHS:
        ym = dt.strftime('%Y-%m')
        for r in REGIONS:
            for a in AGE_GROUPS:
                # 서울/경기 3040의 부채율이 가장 높도록 가중치 부여
                debt_weight = 1.5 if r in ['SEOUL', 'GYEONGGI'] and a in [30, 40] else 1.0
                kosis_data.append({
                    'year_month': ym,
                    'region_code': r,
                    'age_group': a,
                    'household_debt_idx': round(100 + (df_finance[df_finance['year_month']==ym]['interest_rate'].values[0] * 5) * debt_weight, 2)
                })
                
    df_kosis = pd.DataFrame(kosis_data)
    return df_finance, df_kosis

# ---------------------------------------------------------
# [3] Internal Data: User Master & Transaction Logs 
# ---------------------------------------------------------
def generate_internal_data(df_finance, df_kosis):
    """
    내부 고객 마스터 및 결제 로그 생성.
    [핵심 로직] 거시경제 지표(금리/부채)가 임계점을 넘으면 VIP의 결제액(LTV)이 붕괴함.
    """
    # 1. User Master
    users = pd.DataFrame({
        'user_id': [f'USR_{str(i).zfill(5)}' for i in range(NUM_USERS)],
        'age_group': np.random.choice(AGE_GROUPS, NUM_USERS, p=[0.2, 0.4, 0.3, 0.1]),
        'region_code': np.random.choice(REGIONS, NUM_USERS, p=[0.4, 0.3, 0.2, 0.1]),
        'vip_tier': np.random.choice(['VVIP', 'VIP', 'NORMAL'], NUM_USERS, p=[0.05, 0.15, 0.80])
    })
    
    # 2. Transaction Logs (월별 결제 로그)
    transactions = []
    
    for _, user in users.iterrows():
        # 기본 월 결제액 (VVIP일수록 큼)
        base_spend = 500000 if user['vip_tier'] == 'VVIP' else (200000 if user['vip_tier'] == 'VIP' else 50000)
        
        for dt in MONTHS:
            ym = dt.strftime('%Y-%m')
            
            # 현재 시점의 거시 지표 룩업 (Look-up)
            current_rate = df_finance[df_finance['year_month'] == ym]['interest_rate'].values[0]
            current_debt = df_kosis[(df_kosis['year_month'] == ym) & 
                                    (df_kosis['region_code'] == user['region_code']) & 
                                    (df_kosis['age_group'] == user['age_group'])]['household_debt_idx'].values[0]
            
            # [도메인 논리 주입] 둠스클록 임계점(금리 4.0% 이상 & 부채지수 120 이상) 돌파 시, 
            # 고위험군(영끌족 3040 VIP)의 현금 흐름 동결 현상 발생 (결제액 70% 삭감)
            macro_shock_penalty = 1.0
            if current_rate >= 4.0 and current_debt >= 120 and user['vip_tier'] in ['VVIP', 'VIP']:
                macro_shock_penalty = 0.3  # 70% 자산 증발 (Churn 발생)
                
            # 노이즈를 섞어 최종 결제액 산출
            final_spend = base_spend * macro_shock_penalty * np.random.uniform(0.8, 1.2)
            
            transactions.append({
                'tx_id': f"TX_{user['user_id']}_{ym.replace('-','')}",
                'user_id': user['user_id'],
                'year_month': ym,
                'tx_amount': round(final_spend, 0)
            })
            
    df_transactions = pd.DataFrame(transactions)
    return users, df_transactions

# Execute Genesis Pipeline
print("Initializing Data Genesis Pipeline...")
macro_finance, macro_kosis = generate_macro_data()
user_master, tx_logs = generate_internal_data(macro_finance, macro_kosis)
print("Data Generation Complete. Ready for Multi-JOIN.")