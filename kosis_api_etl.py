# kosis_api_etl.py
import requests
import pandas as pd
import os

# [1] KOSIS API Configuration
KOSIS_API_KEY = "YOUR_KOSIS_API_KEY_HERE"
START_MONTH = "202201"
END_MONTH = "202606"

def fetch_kosis_macro_data():
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    
    # [Architect Patch] 테이블 ID와 아이템 ID를 가장 안정적인 규격으로 우회
    params = {
        "method": "getList",
        "apiKey": KOSIS_API_KEY,
        "itmId": "ALL",         # 특정 코드 대신 ALL로 전체 개방
        "objL1": "ALL",         # 전지역
        "objL2": "",
        "objL3": "",
        "objL4": "",
        "objL5": "",
        "objL6": "",
        "objL7": "",
        "objL8": "",
        "format": "json",
        "jsonVD": "Y",
        "prdSe": "M",
        "startPrdDe": START_MONTH,
        "endPrdDe": END_MONTH,
        "orgId": "101",
        "tblId": "DT_1J22003"   # 시도별 소비자물가지수 (가장 대중적이고 안정적인 테이블)
    }
    
    try:
        print("-> Striking KOSIS API Server (V2 Bypass)...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # [방어 로직] KOSIS 서버가 에러 메시지를 반환했는지 검사
        if isinstance(data, dict) and "err" in data:
            print(f"[KOSIS Server Rejected] 서버 응답 거절 사유: {data.get('errMsg')}")
            return None
            
        # 정상 응답 시 DataFrame 변환
        df = pd.DataFrame(data)
        
        # '총지수' 항목만 필터링 (불필요한 세부 품목 노이즈 제거)
        if 'ITM_NM' in df.columns:
            df = df[df['ITM_NM'].str.contains('총지수', na=False)]
            
        # 필요한 컬럼 추출
        df = df[['PRD_DE', 'C1_NM', 'DT']]
        df.rename(columns={'PRD_DE': 'year_month', 'C1_NM': 'region_code', 'DT': 'kosis_stress_idx'}, inplace=True)
        
        df['year_month'] = pd.to_datetime(df['year_month'], format='%Y%m').dt.strftime('%Y-%m')
        df['kosis_stress_idx'] = pd.to_numeric(df['kosis_stress_idx'], errors='coerce')
        
        region_mapping = {
            '전국': 'ALL', '서울특별시': 'SEOUL', '부산광역시': 'BUSAN', 
            '대구광역시': 'DAEGU', '인천광역시': 'INCHEON', '경기도': 'GYEONGGI'
        }
        df['region_code'] = df['region_code'].map(region_mapping)
        df = df.dropna(subset=['region_code'])
        
        return df

    except Exception as e:
        print(f"[API Error] 파이프라인 붕괴: {e}")
        return None

# [2] Pipeline Execution
print("Initiating KOSIS API ETL Pipeline V2...")
df_kosis = fetch_kosis_macro_data()

if df_kosis is not None and not df_kosis.empty:
    if not os.path.exists('data'):
        os.makedirs('data')
        
    save_path = 'data/macro_kosis_api.csv'
    df_kosis.to_csv(save_path, index=False, encoding='utf-8-sig')
    
    print(f"[Success] 거시경제 실물 둠스클록(KOSIS) 데이터 적재 완료: {save_path}")
    print(df_kosis.head())
else:
    print("[Critical Error] KOSIS 파이프라인 가동 실패. 서버 또는 파라미터를 다시 확인해라.")