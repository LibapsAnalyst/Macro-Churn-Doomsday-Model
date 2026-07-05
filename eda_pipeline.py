import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# [1] Data Integration (다중 조인 파이프라인)
# ---------------------------------------------------------
def build_analytical_mart(users, tx, finance, kosis):
    """
    내/외부 데이터를 결합하여 분석용 데이터 마트(Data Mart) 구축
    Bridge Keys: 'user_id', 'year_month', 'region_code', 'age_group'
    """
    # 1. 결제 로그에 유저 마스터 결합
    df_merged = pd.merge(tx, users, on='user_id', how='left')
    
    # 2. 거시 금융 데이터(금리) 결합
    df_merged = pd.merge(df_merged, finance, on='year_month', how='left')
    
    # 3. KOSIS 데이터(부채 지수) 다중 키 결합
    df_merged = pd.merge(df_merged, kosis, 
                         on=['year_month', 'region_code', 'age_group'], 
                         how='left')
                         
    # 4. 파생 변수: Macro-Stress Index (둠스클록 지수)
    # 수식: (기준금리 * 0.4) + (가계부채지수 정규화 * 0.6)
    df_merged['macro_stress_idx'] = (df_merged['interest_rate'] * 10) + (df_merged['household_debt_idx'] * 0.5)
    
    return df_merged

data_mart = build_analytical_mart(user_master, tx_logs, macro_finance, macro_kosis)

# ---------------------------------------------------------
# [2] Exploratory Data Analysis (거시 충격과 자산 붕괴의 증명)
# ---------------------------------------------------------
def run_doomsday_eda(df):
    """
    면접관의 시선을 강탈할 핵심 차트 산출 로직.
    시간 흐름에 따른 '둠스클록 지수' 상승이 'VIP 평균 결제액'을 어떻게 박살내는지 시각화.
    """
    # VIP 그룹만 필터링
    vip_df = df[df['vip_tier'].isin(['VVIP', 'VIP'])]
    
    # 월별 집계
    monthly_trend = vip_df.groupby('year_month').agg(
        avg_spend=('tx_amount', 'mean'),
        avg_stress=('macro_stress_idx', 'mean'),
        avg_rate=('interest_rate', 'mean')
    ).reset_index()
    
    # Visualization setup
    plt.style.use('dark_background') # 하이엔드/해커톤 감성의 다크 테마
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # X축: 시간
    x_labels = monthly_trend['year_month']
    
    # Line 1: VIP 평균 결제액 (Monetary Asset)
    color1 = '#00FFCC' # Cyan
    ax1.set_xlabel('Timeline (Year-Month)', fontsize=12)
    ax1.set_ylabel('VIP Average Spend (₩)', color=color1, fontsize=12)
    ax1.plot(x_labels, monthly_trend['avg_spend'], color=color1, marker='o', linewidth=2.5, label='VIP Spend')
    ax1.tick_params(axis='y', labelcolor=color1)
    plt.xticks(rotation=45)

    # Line 2: Macro-Stress Index (Doomsday Clock)
    ax2 = ax1.twinx()  
    color2 = '#FF3366' # Neon Pink
    ax2.set_ylabel('Macro-Stress Index (Doomsday Clock)', color=color2, fontsize=12)
    ax2.plot(x_labels, monthly_trend['avg_stress'], color=color2, marker='s', linestyle='--', linewidth=2, label='Stress Index')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Title & Guidelines
    plt.title('[Doomsday Correlation] Macro-Stress Impact on VIP Monetary Flight', fontsize=16, pad=20)
    
    # 금리 4.0% 돌파 시점(임계점) 시각적 표시
    critical_month = monthly_trend[monthly_trend['avg_rate'] >= 4.0]['year_month'].min()
    if pd.notna(critical_month):
        plt.axvline(x=critical_month, color='#FFFF00', linestyle=':', linewidth=2)
        plt.text(critical_month, ax2.get_ylim()[1]*0.95, ' Target Threshold\n (Rate >= 4.0%)', color='#FFFF00', fontsize=10)

    fig.tight_layout()
    # plt.show() # 로컬 환경 실행 시 주석 해제
    print("EDA Visual Compilation Complete.")

run_doomsday_eda(data_mart)