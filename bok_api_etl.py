# bok_api_etl.py
import requests
import pandas as pd

# [1] API Configuration
# 네가 발급받은 ECOS 오픈 API 마스터키
API_KEY = "YOUR_BOK_API_KEY_HERE"
BASE_URL = f"https://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/1/100"

# 조회 기간 세팅 (우리의 둠스클록 타겟 시계열)
START_MONTH = "202201"
END_MONTH = "202606"

def fetch_bok_data(stat_code, item_code, value_name):
    """
    한국은행 ECOS API를 호출하여 특정 거시경제 지표를 월별 시계열로 가져오는 헬퍼 함수
    """
    # M: 월별 데이터
    url = f"{BASE_URL}/{stat_code}/M/{START_MONTH}/{END_MONTH}/{item_code}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # HTTP 에러 발생 시 예외 처리
        data = response.json()
        
        # API 응답 구조 디코딩
        rows = data['StatisticSearch']['row']
        df = pd.DataFrame(rows)
        
        # 필요한 컬럼(시간, 데이터값)만 추출 및 이름 변경
        df = df[['TIME', 'DATA_VALUE']]
        df.rename(columns={'TIME': 'year_month', 'DATA_VALUE': value_name}, inplace=True)
        
        # 데이터 타입 캐스팅
        df['year_month'] = pd.to_datetime(df['year_month'], format='%Y%m').dt.strftime('%Y-%m')
        df[value_name] = df[value_name].astype(float)
        
        return df
        
    except Exception as e:
        print(f"[API Error] 데이터를 가져오는 중 문제가 발생했다: {e}")
        return None

# [2] Pipeline Execution
print("Initiating BOK API ETL Pipeline...")

# 1. 한국은행 기준금리 호출 (통계코드: 722Y001, 항목코드: 0101000)
# ※ 주의: 한은 통계코드는 개편에 따라 바뀔 수 있으므로 에러 시 코드 확인 필요
print("-> Fetching Base Interest Rate...")
df_rate = fetch_bok_data('722Y001', '0101000', 'interest_rate')

# 2. 소비자물가지수 총지수 호출 (통계코드: 901Y009, 항목코드: 0)
print("-> Fetching CPI (Consumer Price Index)...")
df_cpi = fetch_bok_data('901Y009', '0', 'cpi')

# [3] Data Integration (결합)
if df_rate is not None and df_cpi is not None:
    # 'year_month'를 기준으로 금리와 물가지수를 병합 (Inner JOIN)
    macro_finance_df = pd.merge(df_rate, df_cpi, on='year_month', how='inner')
    
    # 로컬에 실탄(CSV) 저장 (선택 사항: 메모리에 바로 올려도 됨)
    save_path = 'data/macro_finance_api.csv'
    
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
        
    macro_finance_df.to_csv(save_path, index=False)
    print(f"[Success] 거시경제 금융 둠스클록 데이터가 성공적으로 적재되었다: {save_path}")
    print(macro_finance_df.head())
else:
    print("[Critical Error] 파이프라인 가동 실패. 통신 상태를 확인해라.")