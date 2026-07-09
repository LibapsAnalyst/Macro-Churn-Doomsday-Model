# data_genesis.py (Phase 2: Hybrid Simulation Version)
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# [1] Configuration & Seed
np.random.seed(42)
NUM_USERS = 5000
REGIONS = ['SEOUL', 'GYEONGGI', 'BUSAN', 'DAEGU', 'ALL']
AGE_GROUPS = [20, 30, 40, 50]

print("Initiating Phase 2: Hybrid Data Genesis Pipeline...")

# [2] Load Real Macro Data (방금 API로 적재한 실탄 장전)
try:
    df_finance = pd.read_csv('data/macro_finance_api.csv')
    df_kosis = pd.read_csv('data/macro_kosis_api.csv')
    print("[Success] Real Macro Data Loaded.")
except FileNotFoundError:
    print("[Critical Error] API CSV 파일을 찾을 수 없다. Phase 1부터 다시 점검해라.")
    exit()

# [3] Generate Internal User Master (내부 고객 마스터 생성)
def create_user_master():
    print("-> Generating Virtual User Master Nodes...")
    users = pd.DataFrame({
        'user_id': [f'USR_{str(i).zfill(5)}' for i in range(NUM_USERS)],
        'age_group': np.random.choice(AGE_GROUPS, NUM_USERS, p=[0.2, 0.4, 0.3, 0.1]),
        'region_code': np.random.choice(REGIONS, NUM_USERS, p=[0.35, 0.35, 0.15, 0.05, 0.10]),
        'vip_tier': np.random.choice(['VVIP', 'VIP', 'NORMAL'], NUM_USERS, p=[0.05, 0.15, 0.80])
    })
    return users

# [4] Generate Transaction Logs with Macro-Shock Simulation
def simulate_transactions(users, df_finance, df_kosis):
    print("-> Simulating Transaction Logs based on Macro-Shock Rules...")
    transactions = []
    
    # KOSIS 데이터의 국가 전체(ALL) 평균 지표를 Base로 추출
    df_kosis_all = df_kosis[df_kosis['region_code'] == 'ALL']
    
    # 금리와 물가 지수가 존재하는 월(Month) 리스트 추출
    months = df_finance['year_month'].tolist()
    
    for _, user in users.iterrows():
        # 등급별 기본 월 결제액 (Monetary Baseline)
        base_spend = 800000 if user['vip_tier'] == 'VVIP' else (300000 if user['vip_tier'] == 'VIP' else 50000)
        
        for ym in months:
            # 1. 현재 시점의 실물 거시 지표 룩업
            current_rate = df_finance[df_finance['year_month'] == ym]['interest_rate'].values[0]
            
            # KOSIS 스트레스 지수 (해당 지역 값이 없으면 전국(ALL) 지표로 대체)
            kosis_val = df_kosis[(df_kosis['year_month'] == ym) & (df_kosis['region_code'] == user['region_code'])]['kosis_stress_idx'].values
            if len(kosis_val) == 0:
                kosis_val = df_kosis_all[df_kosis_all['year_month'] == ym]['kosis_stress_idx'].values
            current_stress = kosis_val[0] if len(kosis_val) > 0 else 100.0
            
            # [도메인 논리 주입] Doomsday Threshold (둠스클록 임계점)
            # 기준금리가 3.0%를 초과하고 물가 스트레스가 108을 넘어가면 VIP의 자산 회수(동결) 현상 발동
            macro_shock_penalty = 1.0
            
            if current_rate >= 3.0 and current_stress >= 108.0 and user['vip_tier'] in ['VVIP', 'VIP']:
                # 거시 충격 발동: 영끌족 3040의 경우 타격이 더 큼
                if user['age_group'] in [30, 40]:
                    macro_shock_penalty = np.random.uniform(0.2, 0.4) # 결제액 60~80% 증발
                else:
                    macro_shock_penalty = np.random.uniform(0.4, 0.6) # 결제액 40~60% 증발
                    
            # 최종 결제액 산출 (노이즈 추가)
            final_spend = base_spend * macro_shock_penalty * np.random.uniform(0.85, 1.15)
            
            transactions.append({
                'tx_id': f"TX_{user['user_id']}_{ym.replace('-','')}",
                'user_id': user['user_id'],
                'year_month': ym,
                'tx_amount': round(final_spend, 0)
            })
            
    return pd.DataFrame(transactions)

# [5] Execute & Export
user_master = create_user_master()
tx_logs = simulate_transactions(user_master, df_finance, df_kosis)

# 로컬 data 폴더에 적재
user_master.to_csv('data/user_master.csv', index=False)
tx_logs.to_csv('data/transaction_log.csv', index=False)

print("[Protocol Complete] 내부 고객 마스터 및 하이브리드 결제 로그 적재 완료.")
print("-> data/user_master.csv")
print("-> data/transaction_log.csv")