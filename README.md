# 📉 Macro-Churn-Doomsday: VIP Liquidity Defense Model

## 1. Project Overview (프로젝트 개요)
- **Problem:** 기존 내부 로그 중심 이탈 분석의 한계와 거시경제 충격의 사각지대
- **Solution:** 금리/가계부채 기반 '둠스클록' 지수를 도입한 VIP 자산 붕괴 사전 예측
- **Impact:** 이탈 확률 예측을 넘어 기업의 예상 유동성 손실액(Monetary Decay) 방어

## 2. Architecture & Data Pipeline (아키텍처 및 데이터 파이프라인)
- **Data Sources:** Internal (RFM, Transaction Logs) + External (KOSIS, DART API)
- **Data Mart Schema:** ERD (Entity Relationship Diagram) 및 브릿지 스키마 설명

## 3. Core Methodology (핵심 분석 기법)
- Feature Engineering: Macro-Stress Index (둠스클록) 도출 공식
- Predictive Model: LightGBM (고차원 데이터 처리 및 과적합 방지)
- XAI (Explainable AI): SHAP Value를 통한 거시경제 지표의 인과적 기여도 디코딩

## 4. Key Findings & Business Action (인사이트 및 비즈니스 액션)
- 거시 충격 지수와 VIP LTV 간의 상관관계 시각화 (Lagged Effect)
- 리스크 방어를 위한 실무적 프로토콜 제안

## 5. Quick Start (실행 가이드)
- Requirements (requirements.txt)
- How to Run (ETL -> Modeling -> Simulation)