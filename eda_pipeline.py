# eda_pipeline.py
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("Initiating Phase 3: Multi-JOIN & Doomsday EDA Pipeline...")

# ---------------------------------------------------------
# [1] Data Loading (4개의 실탄 적재)
# ---------------------------------------------------------
try:
    users = pd.read_csv('data/user_master.csv')
    tx = pd.read_csv('data/transaction_log.csv')
    finance = pd.read_csv('data/macro_finance_api.csv')
    kosis = pd.read_csv('data/macro_kosis_api.csv')
    print("[Success] All 4 CSV Data components loaded into Memory.")
except FileNotFoundError:
    print("[Critical Error] CSV 파일을 찾을 수 없다. data 폴더를 확인해라.")
    exit()

# ---------------------------------------------------------
# [2] Multi-JOIN Data Mart Building
# ---------------------------------------------------------
def build_analytical_mart(users, tx, finance, kosis):
    print("-> Executing Multi-JOIN...")
    # 1. 결제 로그 + 유저 마스터
    df = pd.merge(tx, users, on='user_id', how='left')
    
    # 2. + 한국은행 금융 지표 (기준키: year_month)
    df = pd.merge(df, finance, on='year_month', how='left')
    
    # 3. + 통계청 실물 지표 (기준키: year_month, region_code)
    df = pd.merge(df, kosis, on=['year_month', 'region_code'], how='left')
    
    # [Architect Logic] 지역별 KOSIS 데이터가 비어있을 경우, 국가 전체(ALL) 지표로 보정(Fill)
    kosis_all = kosis[kosis['region_code'] == 'ALL'].set_index('year_month')['kosis_stress_idx']
    df['kosis_stress_idx'] = df['kosis_stress_idx'].fillna(df['year_month'].map(kosis_all))
    
    # 4. 파생 변수: Macro-Stress Index (둠스클록 지수)
    # 수식: (금리 * 가중치) + (물가 스트레스 * 가중치)
    df['macro_stress_idx'] = (df['interest_rate'] * 10) + (df['kosis_stress_idx'] * 0.5)
    
    return df

data_mart = build_analytical_mart(users, tx, finance, kosis)

# ---------------------------------------------------------
# [3] Doomsday Visualization (면접관 타격용 킬러 차트)
# ---------------------------------------------------------
def run_doomsday_eda(df):
    print("-> Compiling Visualization Chart...")
    # VIP 그룹 필터링
    vip_df = df[df['vip_tier'].isin(['VVIP', 'VIP'])]
    
    # 월별 평균 집계
    monthly_trend = vip_df.groupby('year_month').agg(
        avg_spend=('tx_amount', 'mean'),
        avg_stress=('macro_stress_idx', 'mean'),
        avg_rate=('interest_rate', 'mean')
    ).reset_index()
    
    # 하이엔드 다크 테마 세팅
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(15, 7))

    x_labels = monthly_trend['year_month']
    
    # [Line 1] VIP 평균 결제액 (Monetary Asset)
    color1 = '#00FFCC' # 네온 사이안
    ax1.set_xlabel('Timeline (Year-Month)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('VIP Average Spend (₩)', color=color1, fontsize=13, fontweight='bold')
    ax1.plot(x_labels, monthly_trend['avg_spend'], color=color1, marker='o', linewidth=2.5, label='VIP Average Spend')
    ax1.tick_params(axis='y', labelcolor=color1)
    plt.xticks(rotation=45)

    # [Line 2] Macro-Stress Index (Doomsday Clock)
    ax2 = ax1.twinx()  
    color2 = '#FF3366' # 네온 핑크
    ax2.set_ylabel('Macro-Stress Index (Doomsday Clock)', color=color2, fontsize=13, fontweight='bold')
    ax2.plot(x_labels, monthly_trend['avg_stress'], color=color2, marker='s', linestyle='--', linewidth=2, label='Macro-Stress Index')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Title & Guidelines
    plt.title('[Doomsday Correlation] Macroeconomic Shocks vs VIP Liquidity Flight', fontsize=18, pad=20, fontweight='bold')
    
    # 둠스클록 임계점(금리 3.0% 이상 돌파 시점) 시각적 하이라이트
    critical_month = monthly_trend[monthly_trend['avg_rate'] >= 3.0]['year_month'].min()
    if pd.notna(critical_month):
        plt.axvline(x=critical_month, color='#FFFF00', linestyle=':', linewidth=2)
        plt.text(critical_month, ax2.get_ylim()[1]*0.95, ' Target Threshold\n (Rate >= 3.0%)', color='#FFFF00', fontsize=11, fontweight='bold')

    fig.tight_layout()
    
    # 로컬에 차트 이미지 저장 및 화면 출력
    plt.savefig('doomsday_correlation_chart.png', dpi=300)
    print("[Protocol Complete] 차트가 사출되었다. 'doomsday_correlation_chart.png'를 확인해라.")
    plt.show()

run_doomsday_eda(data_mart)