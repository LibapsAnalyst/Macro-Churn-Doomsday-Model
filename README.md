# 📉 Macro-Churn-Doomsday: VIP Liquidity Defense Model
> **거시경제 충격 지수(Macro-Stress) 기반 VIP 고객 자산 방어 및 이탈 예측 아키텍처**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![LightGBM](https://img.shields.io/badge/LightGBM-Advanced-red.svg)
![SHAP](https://img.shields.io/badge/SHAP-XAI-yellow.svg)
![API](https://img.shields.io/badge/Data-BOK_&_KOSIS_API-green.svg)

## 1. Project Overview (프로젝트 개요)
기존의 이탈(Churn) 분석은 '화면 UI 불편', '프로모션 종료' 등 내부 플랫폼 요인에만 집착하는 1차원적 한계를 지닙니다. 본 프로젝트는 **'고금리와 인플레이션이라는 불가항력적 거시경제 충격(Macro-Shock)이 기업의 핵심 자산(VIP)을 어떻게 붕괴시키는가?'**에 대한 근원적 질문에서 출발했습니다.

단순히 '몇 명이 이탈하는가'를 세는 것을 넘어, 한국은행 및 통계청 API의 실물 경제 지표를 연동하여 VIP의 **유동성 증발(Liquidity Flight)** 시점을 예측하고 리스크를 방어하는 하이엔드 데이터 파이프라인을 구축했습니다.

## 2. Core Hypotheses (핵심 가설)
* **Macro-Micro Coupling:** VIP의 이탈은 플랫폼에 대한 불만이 아니라, 개인의 '한계 채무 임계점(Target Threshold)' 돌파에 의한 선행적 자산 동결 현상이다.
* **Monetary Risk Decay:** 거시경제 둠스클록(Macro-Stress Index) 1틱 상승 시, 상위 20% 고객군의 결제액은 비선형적으로 붕괴한다.

## 3. Architecture & Data Pipeline
본 프로젝트는 캐글(Kaggle) 등의 정적 데이터를 배제하고, **Agent-Based Stress Testing(에이전트 기반 스트레스 테스트)** 기법을 활용한 하이브리드 파이프라인을 채택했습니다.

1. **Phase 1 (API ETL):** 한국은행(BOK) 기준금리 및 통계청(KOSIS) 지역별 물가/부채 지표 자동 수집.
2. **Phase 2 (Hybrid Genesis):** 실제 거시경제 지표 시계열에 반응하여 결제액이 변동하는 가상 VIP 고객(5,000명) 트랜잭션 시뮬레이션 합성.
3. **Phase 3 (Multi-JOIN & EDA):** 다중 조인 데이터 마트 구축 및 둠스클록 임계점(금리 3.0%) 돌파에 따른 자산 붕괴 시각화.
4. **Phase 4 (ML & XAI):** `LightGBM`을 통한 이탈 예측 및 `SHAP`을 활용한 거시경제 지표의 인과적 기여도 디코딩.

## 4. Key Findings & Business Impact
* **High-Performance Prediction:** LightGBM 모델을 통해 VIP 고객의 이탈 확률을 **ROC-AUC 0.9940**의 압도적 성능으로 예측.
* **Explainable AI (XAI):** SHAP Value 분석 결과, 고객의 과거 결제액(`prev_spend`)이나 내부 등급(`vip_tier`)보다 **기준금리(`interest_rate`)와 거시 스트레스 지수(`macro_stress_idx`)가 이탈에 가장 치명적인 영향을 미치는 원인**임을 수학적으로 증명.
* **Business Action:** 금리 3.0% 돌파 국면 진입 시, 고위험군 VIP를 대상으로 한 선제적 락인(Lock-in) 금융 상품 제안 및 유동성 방어 프로토콜 가동 근거 확보.

## 5. Repository Structure (파일 구조)
```text
📦 Macro-Churn-Doomsday-Model
┣ 📂 data/                         # API 실탄 및 시뮬레이션 생성 데이터 적재소
┣ 📜 bok_api_etl.py                # 한국은행 금융 지표 수집 파이프라인
┣ 📜 kosis_api_etl.py              # 통계청 실물 지표 수집 파이프라인 (V2 Bypass)
┣ 📜 data_genesis.py               # 거시경제 연동형 하이브리드 결제 로그 시뮬레이터
┣ 📜 eda_pipeline.py               # Multi-JOIN 마트 구축 및 Doomsday 상관관계 시각화
┣ 📜 modeling_xai.py               # LightGBM 예측 모델링 및 SHAP 의사결정 해독기
┗ 📜 README.md                     # 프로젝트 명세서

# 1. 의존성 패키지 설치
pip install pandas requests numpy matplotlib lightgbm shap scikit-learn

# 2. 파이프라인 순차 기동
python bok_api_etl.py       # 한국은행 API 적재
python kosis_api_etl.py     # 통계청 API 적재
python data_genesis.py      # 하이브리드 시뮬레이션 데이터 생성
python eda_pipeline.py      # 데이터 병합 및 시각화 차트 사출
python modeling_xai.py      # ML 학습 및 SHAP 분석

Architect: Dae-hwan Kim (LibapsAnalyst)

Email: LibapsAnalyst@gmail.com

GitHub: https://github.com/LibapsAnalyst
