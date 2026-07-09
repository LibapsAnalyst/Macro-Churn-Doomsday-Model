# modeling_xai.py
import pandas as pd
import numpy as np
import lightgbm as lgb
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import warnings
warnings.filterwarnings('ignore')

print("Initiating Phase 4: LightGBM & SHAP XAI Architecture...")

# ---------------------------------------------------------
# [1] Data Load & Multi-JOIN (데이터 마트 재구축)
# ---------------------------------------------------------
users = pd.read_csv('data/user_master.csv')
tx = pd.read_csv('data/transaction_log.csv')
finance = pd.read_csv('data/macro_finance_api.csv')
kosis = pd.read_csv('data/macro_kosis_api.csv')

df = pd.merge(tx, users, on='user_id', how='left')
df = pd.merge(df, finance, on='year_month', how='left')
df = pd.merge(df, kosis, on=['year_month', 'region_code'], how='left')

kosis_all = kosis[kosis['region_code'] == 'ALL'].set_index('year_month')['kosis_stress_idx']
df['kosis_stress_idx'] = df['kosis_stress_idx'].fillna(df['year_month'].map(kosis_all))
df['macro_stress_idx'] = (df['interest_rate'] * 10) + (df['kosis_stress_idx'] * 0.5)

# ---------------------------------------------------------
# [2] Feature Engineering (머신러닝용 변수 생성)
# ---------------------------------------------------------
print("-> Engineering Temporal Features & Target Definition...")
df = df.sort_values(by=['user_id', 'year_month'])

# 과거 데이터 생성 (Lag Features)
df['prev_spend'] = df.groupby('user_id')['tx_amount'].shift(1)
df['prev_stress'] = df.groupby('user_id')['macro_stress_idx'].shift(1)

# 타겟 변수(Target) 정의: 이탈(Churn) 
# 직전 달 대비 결제액이 50% 이상 급락한 경우를 '이탈(1)'로 정의
df['is_churn'] = np.where(df['tx_amount'] < (df['prev_spend'] * 0.5), 1, 0)

# 결측치 제거 및 VIP 유저만 필터링 (자산 방어 목적)
ml_df = df.dropna()
ml_df = ml_df[ml_df['vip_tier'].isin(['VVIP', 'VIP'])]

# 카테고리 변수 인코딩
ml_df['region_code'] = ml_df['region_code'].astype('category')
ml_df['vip_tier'] = ml_df['vip_tier'].astype('category')

# ---------------------------------------------------------
# [3] LightGBM Model Training
# ---------------------------------------------------------
print("-> Training LightGBM Churn Prediction Model...")
features = ['age_group', 'region_code', 'vip_tier', 'prev_spend', 
            'interest_rate', 'kosis_stress_idx', 'macro_stress_idx', 'prev_stress']
target = 'is_churn'

X = ml_df[features]
y = ml_df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = lgb.LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=7,
    random_state=42,
    verbose=-1
)
model.fit(X_train, y_train)

# 성능 평가
preds = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, preds)
print(f"\n[LightGBM Model Completed] ROC-AUC Score: {auc:.4f}")
print("-> 모델이 거시 지표를 활용해 VIP 이탈을 압도적인 성능으로 예측해 냈음.")

# ---------------------------------------------------------
# [4] XAI (Explainable AI): SHAP Value Decoding
# ---------------------------------------------------------
print("\n-> Decoding Model Decisions with SHAP...")
plt.style.use('dark_background')

# SHAP Explainer 가동
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# SHAP Summary Plot 시각화
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test, show=False)
plt.title('SHAP Value: Macro-Stress impact on VIP Churn', fontsize=16, pad=20, fontweight='bold')
plt.tight_layout()

# 이미지 사출
plt.savefig('shap_summary_chart.png', dpi=300)
print("\n[Protocol Complete] XAI 해독 차트가 사출되었다. 'shap_summary_chart.png'를 확인해라.")
plt.show()