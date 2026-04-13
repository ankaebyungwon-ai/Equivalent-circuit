"""
ECM 등가회로 모델 연구포털
군산대학교 기계공학부
Plett (2015) Battery Management Systems Vol.1 Chapter 02
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import requests
import json
from math import exp, sqrt, log

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="ECM 연구포털 | 군산대학교 기계공학부",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Roboto+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: #0e3a6e !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { color: #e2e8f0 !important; font-size: 14px; }
[data-testid="stSidebar"] .stSelectbox label { color: #93c5fd !important; font-size: 12px; font-weight: 700; letter-spacing: .06em; }

/* METRIC CARDS */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #e8f1fb, #f0f9ff);
    border: 1px solid #c8ddf5;
    border-radius: 10px;
    padding: 12px;
    border-left: 4px solid #1a5fa8;
}

/* HEADERS */
h1 { color: #0e3a6e !important; font-weight: 700; }
h2 { color: #1a5fa8 !important; font-weight: 700; border-bottom: 2px solid #c8ddf5; padding-bottom: 8px; }
h3 { color: #0e3a6e !important; font-weight: 600; }

/* EQUATION BOXES */
.eq-box {
    background: #0f172a;
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'Roboto Mono', monospace;
    font-size: 14px;
    color: #7dd3fc;
    margin: 10px 0;
    line-height: 2;
    border-left: 4px solid #1a5fa8;
    overflow-x: auto;
}
.eq-box .cm { color: #6ee7b7; font-style: italic; }
.eq-box .va { color: #fde68a; }

/* KEYPOINT CARDS */
.kp-card {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 14px;
    margin: 6px 0;
    border-left: 4px solid #1a5fa8;
}
.kp-title { font-weight: 700; color: #1a5fa8; font-size: 13px; margin-bottom: 4px; }
.kp-text { color: #475569; font-size: 13px; line-height: 1.6; }

/* HERO BANNER */
.hero-banner {
    background: linear-gradient(135deg, #0e3a6e 0%, #1a5fa8 60%, #0891b2 100%);
    border-radius: 14px;
    padding: 32px 36px;
    color: white;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-title { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
.hero-sub { font-size: 14px; opacity: 0.85; line-height: 1.7; }
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 11px;
    margin-bottom: 12px;
    font-weight: 600;
}

/* INFO BOXES */
.info-box {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 13px;
    color: #0369a1;
    margin: 8px 0;
}
.warn-box {
    background: #fef9c3;
    border: 1px solid #fde047;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 13px;
    color: #854d0e;
    margin: 8px 0;
}
.success-box {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 13px;
    color: #166534;
    margin: 8px 0;
}

/* STEP CARDS */
.step-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px;
    margin: 6px 0;
    border-left: 4px solid;
}

/* COMPARE TABLE */
table.comp { width: 100%; border-collapse: collapse; font-size: 13px; }
table.comp th { background: #1a5fa8; color: white; padding: 9px 12px; text-align: left; }
table.comp td { padding: 8px 12px; border: 1px solid #e2e8f0; }
table.comp tr:nth-child(even) td { background: #f8fafc; }

/* NAV PILLS */
.nav-pill {
    display: inline-block;
    background: #e8f1fb;
    color: #1a5fa8;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
}

/* SoC BAR */
.soc-container {
    background: #e2e8f0;
    border-radius: 8px;
    height: 28px;
    overflow: hidden;
    position: relative;
    margin: 8px 0;
}

/* Stagger card colors */
.card-blue { border-left-color: #1a5fa8; }
.card-teal { border-left-color: #0891b2; }
.card-green { border-left-color: #16a34a; }
.card-amber { border-left-color: #d97706; }
.card-purple { border-left-color: #7c3aed; }
.card-red { border-left-color: #dc2626; }

/* hide streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────
TOPICS = {
    "2.1 개방회로 전압 (OCV)": {
        "icon": "⚡", "tags": ["OCV","LUT","GITT"],
        "desc": "무부하 평형 전압. SoC 추정의 핵심 기준값.",
        "keypoints": [
            {"icon":"⚡","title":"정의","text":"전류 i=0 상태의 단자 전압. 순수 전기화학적 평형 전압."},
            {"icon":"📈","title":"SoC 의존성","text":"SoC(z)와 온도(T)의 비선형 2차원 함수 OCV(z,T). 룩업 테이블(LUT)로 저장."},
            {"icon":"🔋","title":"배터리 종류별","text":"NMC: 단조 증가 S곡선. LFP: 극도로 평탄한 곡선 → SoC 추정 어려움."},
            {"icon":"⏱️","title":"측정 방법","text":"C/30 저속 방전(60시간+) 또는 GITT(소전류 펄스 후 정치 반복)."},
        ],
        "body": """
배터리의 단자 전압은 부하 전류, 온도, 이용 이력 등 다양한 요인에 의해 변합니다. 가장 단순한 모델은 배터리를 **이상적인 전압원**으로 가정합니다. 이 이상 모델과 실제 측정값의 차이를 "모델링 오류"로 정의하고, 단계적으로 항을 추가해 정확도를 높입니다.

OCV는 단일 값이 아니라 **OCV(z, T)**라는 2차원 함수로 표현됩니다. NMC 배터리는 SoC에 따라 단조롭게 증가하는 S자형 곡선을 보이는 반면, LFP 배터리는 3.33V 부근에서 극도로 평탄한 곡선을 보입니다. 이 평탄 구간에서는 수 mV의 전압 오차가 10~20%의 SoC 오차로 직결됩니다.
        """,
        "equations": [
            {
                "title": "이상적 전압원 모델",
                "code": "v(t) = OCV(z(t))            // i=0 가정\nOCV(z,T) = OCV₀(z) + T·OCVrel(z)  // 온도 보정",
                "desc": "전류=0 상태의 단자 전압. 온도 보정 항 포함."
            }
        ],
        "vars": [["z","SoC (0~1, 완충=1.0)"],["T","셀 내부 온도 [°C]"],["OCV₀(z)","0°C 기준 OCV vs SoC [V]"],["OCVrel(z)","°C당 OCV 변화율 [V/°C]"]],
        "graph_title": "OCV vs SoC (NMC / LFP 비교)",
        "compare": {
            "headers": ["항목","NMC","LFP"],
            "rows": [
                ["OCV 형태","단조 증가 S곡선","극도로 평탄 (3.33V 부근)"],
                ["히스테리시스","작음 (<10mV)","큼 (50~100mV)"],
                ["SoC 추정 난이도","보통","어려움"],
                ["OCV 범위","3.0~4.2V","2.8~3.65V"],
            ]
        },
        "refs": [("Plett 2004 Part I","Plett, G. L. (2004). Extended Kalman filtering for BMS — Part I. J. Power Sources, 134(1), 252–261.","10.1016/j.jpowsour.2004.02.032")],
    },
    "2.2 충전 상태 의존성 (SoC)": {
        "icon": "📊", "tags": ["SoC","쿨롱 효율","이산시간"],
        "desc": "잔존 전하량 정량화. 쿨롱 카운팅과 이산시간 점화식.",
        "keypoints": [
            {"icon":"🔢","title":"정의","text":"기호 z, 범위 0.0(완방전) ~ 1.0(완충). 무차원 양."},
            {"icon":"⚗️","title":"쿨롱 효율 η","text":"충전된 전하 중 방전에 이용 가능한 비율. 리튬이온: 99~99.9%."},
            {"icon":"💻","title":"이산시간 구현","text":"연속 ODE를 Δt로 이산화 → BMS MCU 실시간 연산 가능."},
            {"icon":"📊","title":"추정 정확도","text":"쿨롱 카운팅 ±2~5% → EKF 기반 ESC 모델 ±0.5~1.5%."},
        ],
        "body": """
SoC는 배터리 관리 시스템(BMS)에서 가장 핵심적인 상태 변수입니다. 셀의 총 용량 Q[Ah]는 100% → 0%로 방전 시 뽑히는 총 전하량으로 정의합니다.

**쿨롱 효율(η)**은 충전된 전하량 대비 실제 방전 가능한 전하량의 비율입니다. 리튬이온 배터리는 99~99.9% 수준으로 매우 높아, 대부분의 BMS 알고리즘에서 η=1로 단순화합니다.

BMS MCU에서 실시간 연산하기 위해 연속시간 미분방정식을 **이산시간 점화식**(recurrence relation)으로 변환합니다.
        """,
        "equations": [
            {"title":"SoC 연속시간 상태방정식 (식 2.1)","code":"ż(t) = −η(t)·i(t) / Q","desc":"충전 상태 z의 시간 변화율."},
            {"title":"SoC 이산시간 점화식 (식 2.4) — MCU 구현","code":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]","desc":"샘플링 주기 Δt로 이산화. 방전 시 i>0."},
        ],
        "vars": [["z","SoC (0.0~1.0)"],["η","쿨롱 효율 (리튬이온 ≈ 1)"],["Q","총 용량 [Ah]"],["i","전류 [A] (방전: 양수)"],["Δt","샘플링 주기 [s]"]],
        "graph_title": "SoC 추정 방법별 오차 비교 (쿨롱 카운팅 vs EKF)",
        "compare": {
            "headers": ["방법","RMSE","실시간","오차 누적"],
            "rows": [
                ["쿨롱 카운팅","±2~5%","✓","있음"],
                ["OCV 맵핑","±1~3%","✗ (정지 시만)","없음"],
                ["EKF (ESC)","±0.5~1.5%","✓","자가 교정"],
                ["LSTM+ECM","±0.3~0.8%","✓ (GPU)","자가 교정"],
            ]
        },
        "refs": [("Zheng 2018","Zheng, Y., et al. (2018). J. Power Sources, 377, 161–188.","10.1016/j.jpowsour.2017.11.044")],
    },
    "2.3 등가 직렬 저항 (R₀)": {
        "icon": "🔌", "tags": ["ESR","R₀","온도의존성"],
        "desc": "순간 전압 강하로 측정. 저온에서 3~5배 증가.",
        "keypoints": [
            {"icon":"⚡","title":"구성 성분","text":"전해질 저항 + 집전체 저항 + SEI(고체 전해질 계면) 저항의 합."},
            {"icon":"❄️","title":"온도 의존성","text":"저온에서 기하급수적 증가. 0°C 이하: 25°C 대비 3~5배. 겨울철 전기차 출력 저하 주원인."},
            {"icon":"🔬","title":"측정 방법","text":"전류 인가/차단 직후 순간 전압 강하(ΔV₀)로 측정. R₀=|ΔV₀/Δi|."},
            {"icon":"📐","title":"교재 실험값","text":"Δi=5A 펄스: ΔV₀=41mV → R₀=41mV÷5A=8.2mΩ"},
        ],
        "body": """
R₀는 배터리 내부의 순수 옴(Ohmic) 저항으로, **전류 인가/차단 직후 즉각적으로 나타나는 전압 강하**의 원인입니다. RC 분극 전압과 달리 순간적으로 반응합니다.

온도가 낮을수록 전해질의 이온 전도도가 떨어져 R₀가 급격히 증가합니다. 아레니우스(Arrhenius) 방정식에 따라 온도의 지수함수적으로 변합니다. 겨울철 전기차 주행거리 감소의 핵심 원인입니다.
        """,
        "equations": [
            {"title":"단자 전압 (R₀ 포함)","code":"v(t) = OCV(z(t)) − i(t)·R₀\nv[k] = OCV(z[k]) − i[k]·R₀  // 이산시간","desc":"R₀만 고려한 가장 단순한 ECM."},
            {"title":"R₀ 실험적 추출","code":"R₀ = |ΔV₀ / Δi|\n// 교재: |ΔV₀|=41mV, Δi=5A → R₀=8.2mΩ","desc":"전류 펄스 직후 순간 전압 강하로 추출."},
        ],
        "vars": [["R₀","등가 직렬 저항 [Ω]"],["ΔV₀","순간 전압 강하 [V]"],["Δi","전류 변화량 [A]"]],
        "graph_title": "R₀ vs 온도 (NMC 배터리, 아레니우스)",
        "compare": {
            "headers": ["온도","R₀ (상대값)","출력 저하","비고"],
            "rows": [
                ["−30°C","~5배","~80%","시동 불가, 주행거리 급감"],
                ["0°C","~3배","~50%","겨울철 전기차 주행거리 감소"],
                ["25°C","1배 (기준)","0%","정상 동작"],
                ["45°C","~0.8배","성능 향상","과열 시 다른 문제 발생"],
            ]
        },
        "refs": [("Hu 2012","Hu, X., Li, S., & Peng, H. (2012). J. Power Sources, 198, 359–367.","10.1016/j.jpowsour.2011.10.013")],
    },
    "2.4 확산 전압": {
        "icon": "📐", "tags": ["RC 회로","ZOH","분극"],
        "desc": "리튬 이온 농도 구배로 발생하는 느린 동적 전압. RC 근사.",
        "keypoints": [
            {"icon":"🔬","title":"물리적 원인","text":"전극 내부 리튬 이온의 농도 구배. 확산 속도가 느려 시간 지연 발생."},
            {"icon":"💡","title":"손전등 비유","text":"거의 방전된 손전등을 끄고 2분 기다리면 다시 켜짐 → 확산 전압이 서서히 해소."},
            {"icon":"⚙️","title":"RC 모델링","text":"R₁-C₁ 병렬 서브회로로 근사. 시정수 τ=R₁C₁이 클수록 느리게 변화."},
            {"icon":"💻","title":"ZOH 이산화","text":"연속 ODE를 Zero-Order Hold로 정확히 이산화 → MCU 실시간 연산 가능."},
        ],
        "body": """
확산 전압은 **리튬 이온의 농도 구배**에 의해 발생하며, 분 단위의 느린 시간 상수를 가집니다. R₀에 의한 즉각적인 강하와는 달리 지수함수적으로 서서히 변합니다.

교재 실험값: τ = R₁×C₁ = 0.0158Ω × 38,000F ≈ **600초(10분)**. 4τ ≈ 2400초(40분)에서 98% 수렴합니다.

ZOH(Zero-Order Hold) 이산화는 샘플링 구간 내 입력이 일정하다고 가정하고 연속 ODE를 정확하게 이산화하는 방법입니다. 오일러 방법보다 정확하고 수치적으로 안정합니다.
        """,
        "equations": [
            {"title":"연속시간 ODE (식 2.5)","code":"d(i_R1)/dt = −(1/R₁C₁)·i_R1(t) + (1/R₁C₁)·i(t)","desc":"RC 서브회로의 연속시간 1차 미분방정식."},
            {"title":"ZOH 이산화 결과 (식 2.8 핵심 점화식)","code":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\n\nF₁ = exp(−Δt / R₁C₁)   // 속도계수 (0 < F₁ < 1)\n\nv[k] = OCV(z[k]) − R₁·i_R1[k] − R₀·i[k]","desc":"ZOH 이산화로 얻은 정확한 점화식."},
        ],
        "vars": [["i_R1[k]","k번째 샘플의 RC 저항 전류 [A]"],["F₁","속도계수 exp(−Δt/R₁C₁)"],["R₁","분극 저항 [Ω] (교재: 15.8mΩ)"],["C₁","분극 커패시턴스 [F] (교재: 38kF)"],["τ","시정수 R₁×C₁ [s] (교재: ≈600s)"]],
        "graph_title": "RC 확산 전압 응답 (방전 펄스)",
        "compare": {
            "headers": ["모델","RC 쌍","RMSE","파라미터","비고"],
            "rows": [
                ["1RC (ESC)","1개","5~15mV","3개","교재 표준 모델"],
                ["2RC","2개","3~8mV","5개","정확도 ↑"],
                ["FO-ECM","분수차","2~5mV","4~6개","고정확도"],
                ["DFN","없음","<2mV","많음","화학적 원인 해석"],
            ]
        },
        "refs": [("Seaman 2014","Seaman, A., et al. (2014). J. Power Sources, 256, 410–423.","10.1016/j.jpowsour.2013.11.037")],
    },
    "2.5 파라미터 추출": {
        "icon": "🔧", "tags": ["HPPC","펄스 분석"],
        "desc": "R₀=8.2mΩ, R₁=15.8mΩ, C₁≈38kF — 펄스 응답으로 추출.",
        "keypoints": [
            {"icon":"⚡","title":"R₀ 추출","text":"전류 인가 직후 순간 강하 ΔV₀. R₀=|ΔV₀/Δi|. 교재: 41mV÷5A=8.2mΩ"},
            {"icon":"📈","title":"R₁ 추출","text":"정상상태 추가 강하. R₁=|ΔV∞/Δi|−R₀. 교재: 120mV÷5A−8.2=15.8mΩ"},
            {"icon":"⏱️","title":"C₁ 추출","text":"회복 시간 역산. C₁≈Δt_recovery/(4×R₁). 교재: 2400s÷(4×0.0158)≈38kF"},
            {"icon":"🔄","title":"반복 정제","text":"추출값을 모델에 대입 → 최소제곱법으로 최적화"},
        ],
        "body": """
파라미터 추출은 3단계로 진행됩니다. 먼저 **순간 전압 강하**로 R₀를 추출하고, 이어서 **정상상태 전압**에서 R₁을 계산하며, 마지막으로 **전압 회복 시간 상수**에서 C₁을 역산합니다.

추출된 파라미터는 모델에 대입하여 시뮬레이션 전압과 실측 전압을 비교합니다. 오차가 크면 최소제곱법으로 파라미터를 정제합니다.
        """,
        "equations": [
            {"title":"파라미터 추출 공식 + 교재 실험값 (Δi=5A)","code":"R₀ = |ΔV₀ / Δi|         // 순간 강하 → 8.2 mΩ\nR₁ = |ΔV∞ / Δi| − R₀   // 정상상태 → 15.8 mΩ\nC₁ ≈ Δt_rec / (4·R₁)   // 4τ에서 98% → ≈38 kF\nτ = R₁×C₁ = 0.0158×38000 = 600.4 s","desc":"3단계 파라미터 추출 과정."},
        ],
        "vars": [["ΔV₀","순간 전압 강하 (R₀에 의한)"],["ΔV∞","정상상태 강하 (R₀+R₁에 의한)"],["Δt_rec","98% 회복 시간 ≈ 4τ"]],
        "graph_title": "전류 펄스에 대한 단자 전압 응답",
        "compare": {
            "headers": ["파라미터","물리적 의미","교재값","온도 의존성"],
            "rows": [
                ["R₀","전해질+집전체+SEI","8.2 mΩ","강함 (아레니우스)"],
                ["R₁","전극 분극 저항","15.8 mΩ","있음"],
                ["C₁","분극 커패시턴스","38,000 F","있음 (비단조)"],
                ["τ=R₁C₁","RC 시정수","600 s (10분)","온도에 따라 변화"],
            ]
        },
        "refs": [("He 2011","He, H., Xiong, R., & Fan, J. (2011). Energies, 4(4), 582–598.","10.3390/en4040582")],
    },
    "2.6 와버그 임피던스": {
        "icon": "📡", "tags": ["EIS","나이키스트","45°"],
        "desc": "고체 확산을 주파수 영역으로 표현. 나이키스트 45° 직선.",
        "keypoints": [
            {"icon":"📡","title":"EIS란","text":"주파수를 바꿔가며 교류 전압을 인가하고 전류 응답으로 임피던스를 측정."},
            {"icon":"📐","title":"와버그 특성","text":"Z_W = A_W/√(jω) → 실수부=허수부 → 위상각 45° → 나이키스트 45° 직선."},
            {"icon":"🔬","title":"나이키스트 구간","text":"고주파: R₀ 교점. 중주파: RC 반원(분극). 저주파: 45° 직선(와버그)."},
            {"icon":"⚡","title":"랜들스 회로","text":"Rₛ + (Cdl // (Rct + Z_W)) — 표준 전기화학 등가회로."},
        ],
        "body": """
EIS(전기화학 임피던스 분광법)는 다양한 주파수에서 배터리의 임피던스를 측정하는 기법입니다. 나이키스트 플롯에서 각 주파수 대역이 서로 다른 전기화학적 현상을 나타냅니다.

저주파 영역에서 나타나는 **45° 직선**이 와버그 임피던스입니다. Z_W = A_W/√(jω)에서 실수부와 허수부가 동일한 크기를 가지므로 위상각이 정확히 45°입니다.
        """,
        "equations": [
            {"title":"와버그 임피던스 + 랜들스 회로","code":"Z_W(jω) = A_W / √(jω)\n\n// 위상각 = 45° (실수부 = 허수부)\n// 랜들스 회로 총 임피던스\nZ_total = Rₛ + 1/(jω·Cdl + 1/(Rct + Z_W))","desc":"주파수(ω)에 따른 와버그 임피던스."},
        ],
        "vars": [["Z_W","와버그 임피던스 [Ω]"],["A_W","와버그 계수 [Ω/√s]"],["ω","각주파수 [rad/s]"],["Rₛ","전해질 저항"],["Rct","전하 이동 저항"]],
        "graph_title": "나이키스트 플롯 (EIS 시뮬레이션)",
        "compare": {
            "headers": ["주파수 대역","나이키스트 위치","현상"],
            "rows": [
                ["고주파 (kHz)","실수축 교점","전해질 저항 R₀"],
                ["중주파 (Hz)","반원","분극(RC) 과정"],
                ["저주파 (mHz)","45° 직선","고체 확산 (와버그)"],
                ["극저주파","수직선","이중층 충전"],
            ]
        },
        "refs": [("Randles 1947","Randles, J.E.B. (1947). Discuss. Faraday Soc., 1, 11–19.","10.1039/df9470100011")],
    },
    "2.7 히스테리시스 전압": {
        "icon": "🔄", "tags": ["히스테리시스","LFP","이력현상"],
        "desc": "충전/방전 경로에 따라 OCV가 달라지는 이력 현상.",
        "keypoints": [
            {"icon":"🔄","title":"정의","text":"같은 SoC에서 충전 후 OCV와 방전 후 OCV가 다름. 경로 의존적."},
            {"icon":"🔋","title":"LFP에서 특히 큼","text":"LFP: 50~100mV. NMC: <10mV. LFP SoC 추정을 어렵게 하는 주원인."},
            {"icon":"⏱️","title":"시간 의존성 없음","text":"확산 전압과 달리: 시간이 지나도 소멸하지 않음. 오직 SoC 변화 시에만 변함."},
            {"icon":"📐","title":"두 종류","text":"① 동적 M·h[k]: SoC 변화에 따라 지수 감쇠. ② 순간 M₀·s[k]: 전류 방향에 따라 즉각 변화."},
        ],
        "body": """
히스테리시스는 배터리의 **상변환(Phase Transition)** 특성에서 기인합니다. 충전과 방전이 서로 다른 에너지 경로를 따르기 때문에 발생합니다.

**확산 전압과의 결정적 차이**: RC 확산 전압은 전류를 끊으면 시간이 지나 0으로 소멸합니다. 반면 히스테리시스 전압은 시간에 무관하고, 오직 SoC가 변할 때만 변합니다.
        """,
        "equations": [
            {"title":"동적 히스테리시스 (Section 2.7.1)","code":"h[k+1] = exp(−|η·i[k]·γ·Δt/Q|)·h[k]\n        − (1−exp(···))·sgn(i[k])\n\n// −1 ≤ h[k] ≤ 1,  γ ≈ 90 (교재 최적값)","desc":"SoC 변화량에 따라 지수 감쇠."},
            {"title":"전체 히스테리시스 전압","code":"s[k] = sgn(i[k])  if |i[k]| > 0  else  s[k−1]\nV_hys[k] = M₀·s[k] + M·h[k]","desc":"순간 + 동적 히스테리시스 전압."},
        ],
        "vars": [["γ","히스테리시스 감쇠 상수 (최적 ≈ 90)"],["M","동적 히스테리시스 크기 [V]"],["M₀","순간 히스테리시스 크기 [V]"],["h[k]","동적 히스테리시스 상태 (−1~1)"],["s[k]","순간 히스테리시스 상태 (±1)"]],
        "graph_title": "히스테리시스 루프 (LFP OCV vs SoC)",
        "compare": {
            "headers": ["특성","히스테리시스 전압","확산 전압 (RC)"],
            "rows": [
                ["시간 의존성","없음 (SoC에만 의존)","있음 (시간에 따라 소멸)"],
                ["전류 정지 시","변하지 않음","0으로 수렴"],
                ["크기 (LFP)","50~100mV","수십 mV"],
                ["크기 (NMC)","<10mV","수십 mV"],
                ["모델링","동적+순간 2종","RC 서브회로"],
            ]
        },
        "refs": [("Dreyer 2010","Dreyer, W., et al. (2010). Nature Materials, 9(5), 448–453.","10.1038/nmat2718")],
    },
    "2.8 ESC 완성 모델": {
        "icon": "🎯", "tags": ["ESC","상태공간","EKF"],
        "desc": "모든 요소를 통합한 최종 완성형 배터리 모델.",
        "keypoints": [
            {"icon":"🔗","title":"통합 구조","text":"상태벡터 x=[z, i_R, h]ᵀ에 SoC·RC전류·히스테리시스를 모두 담음."},
            {"icon":"🔄","title":"자가 교정","text":"전류=0 휴지 시 RC→0, 전압이 자동으로 OCV+히스테리시스 평형값으로 수렴."},
            {"icon":"📊","title":"검증 성능","text":"25Ah NMC, UDDS 10시간: RMSE = 5.37mV."},
            {"icon":"🤖","title":"EKF와 결합","text":"ESC + 확장 칼만 필터 → 실시간 SoC 자가 교정 추정."},
        ],
        "body": """
ESC(Enhanced Self-Correcting) 모델은 2장의 모든 내용을 통합합니다. "자가 교정"이라 불리는 이유는, 셀이 쉬는 동안(i=0) RC 분극이 0으로 감소하면서 시뮬레이션 전압이 자발적으로 OCV+히스테리시스 평형값으로 수렴하기 때문입니다.

확장 칼만 필터(EKF)와 결합하면 실시간 SoC 추정과 자가 교정이 동시에 이루어집니다.
        """,
        "equations": [
            {"title":"ESC 상태 공간 방정식","code":"// 상태벡터: x = [z, i_R, h]ᵀ\n// 상태방정식\n[z[k+1]  ] = [1   0      0   ] [z[k]  ] + B·u[k]\n[i_R[k+1]]   [0  A_RC    0   ] [i_R[k]]\n[h[k+1]  ]   [0   0   A_H[k]] [h[k]  ]\n\nA_RC = exp(−Δt/R₁C₁)\nA_H[k] = exp(−|η·i·γ·Δt/Q|)\n\n// 출력방정식\nv[k] = OCV(z[k],T[k]) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]\n\n// 검증: 25Ah NMC, UDDS 10h → RMSE = 5.37 mV ✓","desc":"전체 ESC 모델 상태 공간 표현."},
        ],
        "vars": [["x=[z,i_R,h]","상태벡터: SoC, RC전류, 히스테리시스"],["A_RC","RC 상태전이 exp(−Δt/R₁C₁)"],["A_H[k]","히스테리시스 상태전이"],["RMSE","5.37mV (교재 검증값)"]],
        "graph_title": "ESC 모델 검증: 시뮬레이션 vs 실측 (UDDS)",
        "compare": {
            "headers": ["모델","RMSE","장점","단점"],
            "rows": [
                ["단순 전압원","~100mV","가장 단순","매우 부정확"],
                ["R₀만 포함","~50mV","간단","분극 무시"],
                ["1RC ESC","~10mV","실용적 균형","노화 예측 불가"],
                ["2RC ESC","~5mV","높은 정확도","파라미터 많음"],
                ["DFN+ML 하이브리드","<2mV","최고 정확도","복잡, GPU 필요"],
            ]
        },
        "refs": [
            ("Plett 2004 Part I","Plett, G. L. (2004). EKF for BMS — Part I. J. Power Sources, 134(1), 252–261.","10.1016/j.jpowsour.2004.02.032"),
            ("Plett 2004 Part II","Plett, G. L. (2004). EKF for BMS — Part II. J. Power Sources, 134(2), 262–276.","10.1016/j.jpowsour.2004.02.033"),
        ],
    },
}

# OCV lookup table
OCV_TABLE = [3.0, 3.35, 3.55, 3.65, 3.72, 3.78, 3.85, 3.92, 4.0, 4.1, 4.2]
def get_ocv(z):
    z = max(0, min(1, z))
    idx = min(int(z * 10), 9)
    frac = z * 10 - idx
    return OCV_TABLE[idx] + frac * (OCV_TABLE[idx+1] - OCV_TABLE[idx])

# ──────────────────────────────────────────────
# GRAPH GENERATORS
# ──────────────────────────────────────────────
def make_graph(topic_key):
    dark = False
    bg = "rgba(0,0,0,0)"
    grid = "rgba(226,232,240,0.6)"
    txt = "#475569"
    font = dict(family="Noto Sans KR", color=txt)

    layout_base = dict(
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=font,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", y=-0.15),
        xaxis=dict(gridcolor=grid, zerolinecolor=grid),
        yaxis=dict(gridcolor=grid, zerolinecolor=grid),
        height=280,
    )

    if "2.1" in topic_key:
        soc = np.linspace(0, 1, 11)
        nmc = [3.0,3.40,3.65,3.75,3.82,3.89,3.97,4.05,4.12,4.18,4.20]
        lfp = [2.8,3.20,3.30,3.32,3.33,3.33,3.34,3.35,3.36,3.50,3.65]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=soc, y=nmc, name="NMC OCV", line=dict(color="#1a5fa8", width=2.5)))
        fig.add_trace(go.Scatter(x=soc, y=lfp, name="LFP OCV", line=dict(color="#16a34a", width=2.5, dash="dash")))
        fig.update_layout(**layout_base, title="OCV vs SoC (NMC / LFP 비교)",
                          xaxis_title="SoC", yaxis_title="OCV (V)")
        return fig

    elif "2.2" in topic_key:
        t = list(range(11))
        coulomb = [0, 0.3, 0.7, 1.2, 1.8, 2.5, 3.0, 3.8, 4.5, 5.0, 5.8]
        ekf = [0, 0.2, 0.3, 0.3, 0.4, 0.5, 0.5, 0.6, 0.7, 0.8, 0.9]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=coulomb, name="쿨롱 카운팅", line=dict(color="#dc2626", width=2.5)))
        fig.add_trace(go.Scatter(x=t, y=ekf, name="EKF (ESC)", line=dict(color="#1a5fa8", width=2.5)))
        fig.update_layout(**layout_base, title="SoC 추정 방법별 오차 누적",
                          xaxis_title="시간 경과 →", yaxis_title="SoC 오차 (%)")
        return fig

    elif "2.3" in topic_key:
        temp = [-30, -20, -10, 0, 10, 20, 25, 30, 35, 40, 45]
        r0 = [42, 35, 25, 18, 13, 10, 8.2, 7.5, 7.0, 6.8, 6.5]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=temp, y=r0, name="R₀", fill="tozeroy",
                                 line=dict(color="#dc2626", width=2.5),
                                 fillcolor="rgba(220,38,38,0.1)"))
        fig.add_shape(type="line", x0=25, x1=25, y0=0, y1=42,
                      line=dict(color="#1a5fa8", dash="dash", width=1.5))
        fig.add_annotation(x=25, y=20, text="25°C (기준)", showarrow=False,
                           font=dict(color="#1a5fa8", size=11))
        fig.update_layout(**layout_base, title="R₀ vs 온도 (아레니우스 의존성)",
                          xaxis_title="온도 (°C)", yaxis_title="R₀ (mΩ)")
        return fig

    elif "2.4" in topic_key:
        t = list(range(81))
        R1, C1, R0 = 0.0158, 38000, 0.0082
        I = 5
        v, irc_arr = [], []
        irc = 0
        for tt in t:
            if tt < 5:
                v.append(4.1); irc_arr.append(0)
            else:
                F = exp(-1/(R1*C1))
                irc = F*irc + (1-F)*I
                v.append(4.1 - R1*irc - R0*I)
                irc_arr.append(irc)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=[4.1]*81, name="OCV 기준선",
                                 line=dict(color="#dc2626", width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=t, y=v, name="단자 전압",
                                 fill="tonexty", line=dict(color="#1a5fa8", width=2.5),
                                 fillcolor="rgba(26,95,168,0.07)"))
        fig.update_layout(**layout_base, title="RC 확산 전압 응답 (I=5A 방전 펄스)",
                          xaxis_title="시간 (s)", yaxis_title="전압 (V)",
                          yaxis=dict(range=[4.0, 4.14], gridcolor=grid))
        return fig

    elif "2.5" in topic_key:
        t = list(range(41))
        v = [4.1]*5 + [4.059]*1 + [4.059 + 0.041*(1-exp(-tt/10)) for tt in range(35)]
        ocv_line = [4.1]*41
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=ocv_line, name="OCV 기준선",
                                 line=dict(color="#dc2626", width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=t, y=v, name="단자 전압",
                                 line=dict(color="#1a5fa8", width=2.5)))
        fig.add_annotation(x=5.5, y=4.065, text="ΔV₀=41mV\nR₀=8.2mΩ",
                           showarrow=True, arrowhead=2, font=dict(size=10, color="#dc2626"))
        fig.update_layout(**layout_base, title="전류 펄스(Δi=5A)에 대한 전압 응답",
                          xaxis_title="시간 →", yaxis_title="전압 (V)")
        return fig

    elif "2.6" in topic_key:
        # Nyquist plot simulation
        omega = np.logspace(4, -3, 300)
        R0, R1, C1 = 0.0082, 0.0158, 38000
        Aw = 0.002
        re_z, im_z = [], []
        for w in omega:
            jw = complex(0, w)
            Z_rc = R1 / (1 + jw * R1 * C1)
            Z_w = Aw / (jw ** 0.5)
            Z_tot = R0 + Z_rc + Z_w
            re_z.append(Z_tot.real * 1000)
            im_z.append(-Z_tot.imag * 1000)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=re_z, y=im_z, mode="lines",
                                 name="나이키스트 임피던스",
                                 line=dict(color="#1a5fa8", width=2.5)))
        fig.add_annotation(x=8.5, y=0.5, text="R₀ (고주파)", showarrow=True,
                           font=dict(size=10, color="#dc2626"))
        fig.update_layout(**layout_base, title="나이키스트 플롯 (EIS 시뮬레이션)",
                          xaxis_title="Re(Z) (mΩ)", yaxis_title="-Im(Z) (mΩ)")
        return fig

    elif "2.7" in topic_key:
        soc = np.linspace(0, 1, 11)
        charge_ocv = [2.80,3.30,3.34,3.35,3.36,3.37,3.38,3.40,3.45,3.50,3.65]
        discharge_ocv = [2.80,3.20,3.27,3.28,3.29,3.30,3.31,3.33,3.38,3.44,3.60]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=soc, y=charge_ocv, name="충전 OCV",
                                 line=dict(color="#1a5fa8", width=2.5)))
        fig.add_trace(go.Scatter(x=soc, y=discharge_ocv, name="방전 OCV",
                                 line=dict(color="#16a34a", width=2.5, dash="dash")))
        fig.add_vrect(x0=0.2, x1=0.8, fillcolor="#fef9c3", opacity=0.4,
                      annotation_text="히스테리시스\n30~60mV", annotation_position="top left")
        fig.update_layout(**layout_base, title="히스테리시스 루프 (LFP OCV vs SoC)",
                          xaxis_title="SoC", yaxis_title="OCV (V)")
        return fig

    elif "2.8" in topic_key:
        t = list(range(11))
        measured = [3.82,3.74,3.69,3.75,3.71,3.66,3.70,3.73,3.68,3.65,3.70]
        modeled  = [3.822,3.742,3.692,3.752,3.712,3.662,3.702,3.732,3.682,3.652,3.702]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=measured, name="실측 전압",
                                 line=dict(color="#475569", width=2, dash="dot"),
                                 mode="lines+markers", marker=dict(size=4)))
        fig.add_trace(go.Scatter(x=t, y=modeled, name="ESC 모델",
                                 line=dict(color="#1a5fa8", width=2.5)))
        fig.add_annotation(x=5, y=3.69, text="RMSE = 5.37 mV ✓",
                           showarrow=False, font=dict(size=12, color="#16a34a"),
                           bgcolor="#dcfce7", bordercolor="#86efac", borderwidth=1)
        fig.update_layout(**layout_base, title="ESC 모델 검증: 시뮬레이션 vs 실측 (UDDS 10h)",
                          xaxis_title="시간 →", yaxis_title="전압 (V)")
        return fig

    return None

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <div style="font-size:36px;">🔋</div>
        <div style="font-size:15px;font-weight:700;color:white;margin-top:4px;">ECM 연구포털</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-top:4px;">군산대학교 기계공학부<br>BMS Vol.1 · Chapter 02</div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.15);margin:12px 0;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "📌 메뉴",
        ["🏠 홈", "📖 주제별 학습", "🛠 인터랙티브 실습", "🧮 파라미터 계산기", "📝 이해도 퀴즈"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**🔗 관련 자료**", unsafe_allow_html=False)
    st.markdown(
        "📦 [ESCtoolbox (MATLAB)](http://mocha-java.uccs.edu/BMS1/)  \n"
        "📄 [Plett 2004 DOI](https://doi.org/10.1016/j.jpowsour.2004.02.032)  \n"
        "📘 BMS Vol.1, Artech House 2015"
    )

    st.markdown("---")
    # Weather widget
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=35.98&longitude=126.71"
            "&current=temperature_2m,weathercode,wind_speed_10m,relative_humidity_2m"
            "&timezone=Asia%2FSeoul&forecast_days=1", timeout=3
        )
        wd = r.json()["current"]
        wic = {0:"☀️",1:"🌤",2:"⛅",3:"☁️",45:"🌫",61:"🌧",71:"❄️",80:"🌦",95:"⛈"}
        wdesc = {0:"맑음",1:"대체로 맑음",2:"구름 조금",3:"흐림",45:"안개",61:"비",71:"눈",80:"소나기",95:"뇌우"}
        code = wd["weathercode"]
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:10px 12px;">
            <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-bottom:4px;">🌤 군산 날씨 · 실시간</div>
            <div style="font-size:22px;font-weight:700;color:white;">{wic.get(code,'🌡')} {round(wd['temperature_2m'])}°C</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.7);">{wdesc.get(code,'날씨')} · 💨{round(wd['wind_speed_10m'])}km/h · 💧{round(wd['relative_humidity_2m'])}%</div>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("<div style='color:rgba(255,255,255,0.4);font-size:11px;'>🌤 날씨 불러오기 실패</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAGE: HOME
# ──────────────────────────────────────────────
if page == "🏠 홈":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">📚 Plett(2015) BMS Vol.1 · Chapter 02</div>
        <div class="hero-title">배터리 <span style="color:#7dd3fc">등가회로 모델</span> 연구포털</div>
        <div class="hero-sub">OCV·ESR·확산전압·히스테리시스를 통합한 ESC 모델 —<br>
        핵심 개념·수식·인터랙티브 실습을 한눈에. 군산대학교 기계공학부</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📖 주제 섹션", "8개", "BMS Ch.02")
    c2.metric("📊 모델 RMSE", "5.37 mV", "UDDS 10h")
    c3.metric("🔋 쿨롱 효율 η", "99.9 %", "리튬이온")
    c4.metric("📝 퀴즈 문제", "10문제", "4지선다")

    st.markdown("---")
    st.markdown("## 📋 주요 콘텐츠")

    sections = [
        ("⚡", "개방회로 전압 (OCV)", "무부하 평형 전압. SoC 추정의 핵심 기준값.", "#dbeafe"),
        ("📊", "충전 상태 (SoC)", "잔존 전하량 정량화. 쿨롱 카운팅과 이산시간 변환.", "#dcfce7"),
        ("🔌", "등가 직렬 저항 R₀", "순간 전압 강하로 측정. 저온에서 3~5배 증가.", "#fef9c3"),
        ("📐", "확산 전압 (RC)", "리튬 이온 농도 구배 → RC 회로로 근사. ZOH 이산화.", "#f3e8ff"),
        ("🔧", "파라미터 추출", "R₀=8.2mΩ, R₁=15.8mΩ, C₁≈38kF 실험적 추출.", "#fee2e2"),
        ("📡", "와버그 임피던스", "EIS로 측정하는 고체 확산. 나이키스트 45° 직선.", "#f0fdf4"),
        ("🔄", "히스테리시스 전압", "경로 의존적 이력 현상. LFP에서 특히 중요.", "#fef3c7"),
        ("🎯", "ESC 완성 모델", "모든 요소 통합 → RMSE 5.37mV. EKF로 실시간 SoC.", "#e0f2fe"),
    ]
    cols = st.columns(4)
    for i, (ico, title, desc, color) in enumerate(sections):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:{color};border-radius:10px;padding:14px;margin-bottom:12px;height:130px;">
                <div style="font-size:22px;margin-bottom:6px;">{ico}</div>
                <div style="font-size:13px;font-weight:700;color:#0e3a6e;margin-bottom:4px;">{title}</div>
                <div style="font-size:11px;color:#475569;line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📌 핵심 수식 요약")
    eq_cols = st.columns(2)
    eqs = [
        ("SoC 이산시간 점화식", "z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"),
        ("RC 속도계수", "F₁ = exp(−Δt / R₁C₁)  →  교재: ≈0.9983"),
        ("RC 확산 점화식", "i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]"),
        ("ESC 단자 전압", "v[k] = OCV(z,T) + M₀·s[k] + M·h[k] − R₁·i_R1[k] − R₀·i[k]"),
    ]
    for i, (title, eq) in enumerate(eqs):
        with eq_cols[i % 2]:
            st.markdown(f"**{title}**")
            st.code(eq, language=None)

# ──────────────────────────────────────────────
# PAGE: 주제별 학습
# ──────────────────────────────────────────────
elif page == "📖 주제별 학습":
    st.markdown("## 📖 주제별 학습")
    st.markdown("**14개 섹션**에서 배터리 등가회로 모델의 핵심 개념을 학습합니다.")

    topic_key = st.selectbox(
        "섹션 선택",
        list(TOPICS.keys()),
        format_func=lambda x: x
    )
    tp = TOPICS[topic_key]

    # Tags
    tag_html = " ".join([f'<span class="nav-pill">{t}</span>' for t in tp["tags"]])
    st.markdown(tag_html, unsafe_allow_html=True)
    st.markdown("")

    # TABS
    tab_concept, tab_eq, tab_graph, tab_compare, tab_ref = st.tabs(
        ["📖 개념 설명", "🔢 핵심 수식", "📊 AI 그래프", "📋 비교 분석", "📄 참고문헌"]
    )

    # ── 개념 설명 탭 ──
    with tab_concept:
        st.markdown(f"### {tp['icon']} {topic_key}")

        # Keypoints (핵심 포인트)
        st.markdown("#### 🎯 핵심 포인트")
        kp_cols = st.columns(2)
        for i, kp in enumerate(tp["keypoints"]):
            with kp_cols[i % 2]:
                st.markdown(f"""
                <div class="kp-card">
                    <div style="font-size:20px;margin-bottom:4px;">{kp['icon']}</div>
                    <div class="kp-title">{kp['title']}</div>
                    <div class="kp-text">{kp['text']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📝 상세 내용")
        st.markdown(tp["body"])

    # ── 핵심 수식 탭 ──
    with tab_eq:
        st.markdown("#### 🔢 핵심 수식")
        for eq in tp["equations"]:
            st.markdown(f"**{eq['title']}**")
            st.markdown(f"""
            <div class="eq-box">{eq['code'].replace(chr(10), '<br>')}</div>
            """, unsafe_allow_html=True)
            st.caption(f"▶ {eq['desc']}")
            st.markdown("")

        if tp.get("vars"):
            st.markdown("#### 📐 기호 정의")
            df_vars = pd.DataFrame(tp["vars"], columns=["기호", "의미"])
            st.dataframe(df_vars, use_container_width=True, hide_index=True)

    # ── AI 그래프 탭 ──
    with tab_graph:
        st.markdown("#### 📊 AI 그래프")
        st.markdown(f"**{tp['graph_title']}**")
        st.info("💡 그래프는 교재 데이터 기반으로 시뮬레이션한 예시 그래프입니다.")
        fig = make_graph(topic_key)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=f"graph_{topic_key}")
        else:
            st.warning("이 섹션의 그래프는 준비 중입니다.")

    # ── 비교 분석 탭 ──
    with tab_compare:
        st.markdown("#### 📋 비교 분석")
        comp = tp.get("compare")
        if comp:
            df_comp = pd.DataFrame(comp["rows"], columns=comp["headers"])
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # ── 참고문헌 탭 ──
    with tab_ref:
        st.markdown("#### 📄 참고문헌 (APA 7th Edition)")
        for label, text, doi in tp.get("refs", []):
            st.markdown(f"""
            <div style="background:#f0f9ff;border:1px solid #bae6fd;border-left:4px solid #1a5fa8;
                        border-radius:0 8px 8px 0;padding:12px 14px;margin-bottom:10px;">
                <div style="font-size:10px;font-weight:700;color:#1a5fa8;margin-bottom:4px;letter-spacing:.05em;">{label}</div>
                <div style="font-size:13px;color:#475569;line-height:1.7;">{text}</div>
                {"<div style='font-family:monospace;font-size:11px;color:#1a5fa8;margin-top:4px;'>DOI: <a href='https://doi.org/"+doi+"' target='_blank'>"+doi+"</a></div>" if doi else ""}
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAGE: 인터랙티브 실습
# ──────────────────────────────────────────────
elif page == "🛠 인터랙티브 실습":
    st.markdown("## 🛠 인터랙티브 실습 프로그램")
    st.markdown("**실제로 작동하는** 3가지 배터리 모델링 실습 프로그램입니다.")

    lab_tab1, lab_tab2, lab_tab3 = st.tabs(
        ["🔋 SoC 실시간 시뮬레이터", "📡 나이키스트 플롯 단계별", "⚡ ESC 모델 구성 단계"]
    )

    # ── Lab 1: SoC 실시간 시뮬레이터 ──
    with lab_tab1:
        st.markdown("### 🔋 SoC 실시간 시뮬레이터")
        st.markdown("슬라이더를 조절하면 SoC와 단자 전압이 **실시간**으로 계산됩니다.")

        col_ctrl, col_result = st.columns([1, 1.5])

        with col_ctrl:
            st.markdown("**⚙️ 파라미터 설정**")
            I_val = st.slider("방전 전류 I (A)", 1.0, 50.0, 10.0, 0.5)
            z0_val = st.slider("초기 SoC (%)", 10, 100, 80, 1) / 100
            Q_val = st.slider("총 용량 Q (Ah)", 1.0, 100.0, 25.0, 1.0)
            R0_val = st.slider("R₀ (mΩ)", 1.0, 50.0, 8.2, 0.1) / 1000
            R1_val = st.slider("R₁ (mΩ)", 1.0, 50.0, 15.8, 0.1) / 1000
            C1_val = st.slider("C₁ (kF)", 1.0, 100.0, 38.0, 1.0) * 1000

        with col_result:
            # Simulate
            dt = 3600  # 1시간
            tau = R1_val * C1_val

            # Multi-step simulation
            z_arr, v_arr, t_arr = [], [], []
            z, irc = z0_val, 0.0
            for step in range(13):
                t_sec = step * 300  # 5분 간격
                z_arr.append(max(0, z))
                ocv = get_ocv(max(0, z))
                F = exp(-300 / tau) if tau > 0 else 0
                irc = F * irc + (1 - F) * I_val
                vt = ocv - R1_val * irc - R0_val * I_val
                v_arr.append(vt)
                t_arr.append(t_sec // 60)
                z = max(0, z - (300 / 3600) * I_val / Q_val)

            # Current SoC display
            cur_soc = z_arr[-1] if z_arr else z0_val
            cur_v = v_arr[-1] if v_arr else 4.0
            cur_pct = int(cur_soc * 100)

            # SoC progress bar
            soc_color = "#16a34a" if cur_pct > 50 else "#d97706" if cur_pct > 20 else "#dc2626"
            st.markdown(f"""
            <div style="margin-bottom:8px;">
                <div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:4px;">
                    📊 SoC (1시간 방전 후)
                </div>
                <div style="background:#e2e8f0;border-radius:8px;height:32px;position:relative;">
                    <div style="background:{soc_color};width:{cur_pct}%;height:100%;border-radius:8px;transition:width 0.3s;"></div>
                    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                                font-size:13px;font-weight:700;color:white;text-shadow:0 1px 3px rgba(0,0,0,0.5);">
                        {cur_pct}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            m1, m2 = st.columns(2)
            m1.metric("단자 전압 V(t)", f"{cur_v:.3f} V")
            m2.metric("시정수 τ", f"{tau:.0f} s ({tau/60:.1f}분)")

            # Time series chart
            fig_soc = go.Figure()
            fig_soc.add_trace(go.Scatter(x=t_arr, y=v_arr, name="단자 전압",
                                         line=dict(color="#1a5fa8", width=2.5),
                                         fill="tozeroy", fillcolor="rgba(26,95,168,0.08)"))
            fig_soc.add_trace(go.Scatter(x=t_arr, y=[get_ocv(z) for z in z_arr],
                                         name="OCV (참조)", line=dict(color="#dc2626", width=1.5, dash="dash")))
            fig_soc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=10, t=30, b=30),
                height=200,
                xaxis_title="시간 (분)", yaxis_title="전압 (V)",
                legend=dict(orientation="h", y=-0.25),
                font=dict(size=11),
                title=f"전압 응답 (I={I_val}A, τ={tau:.0f}s)",
            )
            st.plotly_chart(fig_soc, use_container_width=True)

        # Formula display
        st.markdown("**📐 적용 수식**")
        st.code(f"""# 1시간 방전 시뮬레이션
z_new = z₀ - (3600/Q) * I = {z0_val:.2f} - (3600/{Q_val}) * {I_val} = {max(0, z0_val - 3600/Q_val*I_val/3600):.3f}
τ = R₁ × C₁ = {R1_val*1000:.1f}mΩ × {C1_val/1000:.0f}kF = {tau:.0f} s
F₁ = exp(-Δt/τ) = exp(-300/{tau:.0f}) = {exp(-300/tau):.4f}
V(t) ≈ OCV(z) - R₀·I = {get_ocv(max(0,z_arr[-1])):.3f} - {R0_val*1000:.1f}×10⁻³ × {I_val} = {cur_v:.3f} V""", language="python")

    # ── Lab 2: 나이키스트 플롯 단계별 ──
    with lab_tab2:
        st.markdown("### 📡 나이키스트 플롯 단계별 학습")
        st.markdown("각 주파수 구간을 선택하면 해당 구간의 물리적 의미와 수식이 표시됩니다.")

        nyq_steps = {
            "① 고주파 (kHz) — 전해질 저항 R₀": {
                "desc": "수백 kHz 이상에서 나이키스트 플롯이 **실수축과 교차하는 점**이 R₀입니다. 전해질 이온 이동에 의한 순수 옴 저항.",
                "eq": "Z(ω→∞) = R₀ = 8.2 mΩ  (교재 예시)",
                "color": "#dc2626",
                "range": (200, 300),
            },
            "② 중주파 (Hz) — RC 분극 반원": {
                "desc": "수 Hz ~ 수 kHz 구간에서 **반원 형태**로 나타납니다. 반원의 지름이 R₁. 정점 주파수에서 시정수 τ=R₁C₁ 추출 가능.",
                "eq": "Z_RC(ω) = R₁ / (1 + jω·R₁C₁)   →   반원 지름 = R₁",
                "color": "#d97706",
                "range": (100, 200),
            },
            "③ 저주파 (mHz) — 와버그 확산 (45°)": {
                "desc": "수십 mHz 이하에서 나타나는 **45° 직선**입니다. 고체 전극 내 리튬 이온의 확산에 의한 임피던스.",
                "eq": "Z_W(jω) = A_W / √(jω)  →  위상각 = 45°",
                "color": "#7c3aed",
                "range": (0, 100),
            },
            "④ 극저주파 — 이중층 커패시턴스": {
                "desc": "mHz 이하에서 임피던스가 **수직으로 상승**하는 구간. 전극-전해질 계면의 이중층 충전에 의한 순수 커패시터 거동.",
                "eq": "Z_C(ω→0) → ∞  (순수 커패시터)",
                "color": "#0891b2",
                "range": None,
            },
        }

        selected_step = st.radio("구간 선택", list(nyq_steps.keys()), label_visibility="collapsed")
        step_data = nyq_steps[selected_step]

        col_nyq, col_nyq_info = st.columns([1.5, 1])

        with col_nyq:
            # Generate Nyquist data
            omega = np.logspace(4, -4, 500)
            R0, R1, C1 = 0.0082, 0.0158, 38000
            Aw = 0.002
            re_z, im_z, freq_hz = [], [], []
            for w in omega:
                jw = complex(0, w)
                Z_rc = R1 / (1 + jw * R1 * C1)
                Z_w = Aw / (complex(0, 1) ** 0.5 * w ** 0.5)
                Z_tot = R0 + Z_rc + Z_w
                re_z.append(Z_tot.real * 1000)
                im_z.append(-Z_tot.imag * 1000)
                freq_hz.append(w / (2 * np.pi))

            fig_nyq = go.Figure()

            # Highlight selected range
            rng = step_data["range"]
            if rng:
                re_h = re_z[rng[0]:rng[1]]
                im_h = im_z[rng[0]:rng[1]]
                fig_nyq.add_trace(go.Scatter(x=re_h, y=im_h, mode="lines",
                                             line=dict(color=step_data["color"], width=5),
                                             name="선택 구간"))
            fig_nyq.add_trace(go.Scatter(x=re_z, y=im_z, mode="lines",
                                         line=dict(color="rgba(100,116,139,0.4)", width=1.5),
                                         name="전체 나이키스트"))

            fig_nyq.add_annotation(x=8.5, y=0.1, text="R₀", showarrow=False,
                                   font=dict(color="#dc2626", size=11))
            fig_nyq.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=10, t=30, b=30), height=280,
                xaxis_title="Re(Z) (mΩ)", yaxis_title="-Im(Z) (mΩ)",
                legend=dict(orientation="h", y=-0.2),
                title="나이키스트 플롯 (EIS)",
            )
            st.plotly_chart(fig_nyq, use_container_width=True)

        with col_nyq_info:
            st.markdown(f"**{selected_step}**")
            st.markdown(f"""
            <div style="background:#f0f9ff;border-left:4px solid {step_data['color']};
                        border-radius:0 8px 8px 0;padding:12px 14px;margin:8px 0;">
                {step_data['desc']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**수식:**")
            st.code(step_data["eq"], language=None)

    # ── Lab 3: ESC 모델 단계별 구성 ──
    with lab_tab3:
        st.markdown("### ⚡ ESC 모델 단계별 구성")
        st.markdown("각 단계를 클릭하면 모델이 어떻게 완성되는지 확인할 수 있습니다.")

        esc_steps = [
            {
                "title": "Step 1: 이상적 전압원 v = OCV(z)",
                "desc": "가장 단순한 모델. R₀, 분극, 히스테리시스 모두 무시.",
                "eq": "v(t) = OCV(z(t))",
                "rmse": "~100 mV",
                "color": "#fee2e2",
                "border": "#dc2626",
                "R0": 0, "R1": 0, "C1": 1e9, "hys": False,
            },
            {
                "title": "Step 2: + 등가 직렬 저항 R₀",
                "desc": "순간 전압 강하 추가. 전류 인가 시 즉각적인 전압 변화 모델링.",
                "eq": "v[k] = OCV(z[k]) − R₀·i[k]",
                "rmse": "~50 mV",
                "color": "#fef9c3",
                "border": "#d97706",
                "R0": 0.0082, "R1": 0, "C1": 1e9, "hys": False,
            },
            {
                "title": "Step 3: + RC 확산 전압",
                "desc": "지수 감쇠하는 분극 전압 추가. 시정수 τ=R₁C₁의 느린 동적 거동.",
                "eq": "v[k] = OCV(z[k]) − R₁·i_R1[k] − R₀·i[k]",
                "rmse": "~10 mV",
                "color": "#f0fdf4",
                "border": "#16a34a",
                "R0": 0.0082, "R1": 0.0158, "C1": 38000, "hys": False,
            },
            {
                "title": "Step 4: + 히스테리시스 (ESC 완성)",
                "desc": "충방전 경로 의존성 추가. 특히 LFP에서 중요. ESC 완성.",
                "eq": "v[k] = OCV(z[k],T[k]) + M₀·s[k] + M·h[k] − R₁·i_R1[k] − R₀·i[k]",
                "rmse": "5.37 mV ✓",
                "color": "#e0f2fe",
                "border": "#1a5fa8",
                "R0": 0.0082, "R1": 0.0158, "C1": 38000, "hys": True,
            },
        ]

        selected_esc = st.radio(
            "단계 선택",
            [s["title"] for s in esc_steps],
            label_visibility="collapsed"
        )
        esc_data = next(s for s in esc_steps if s["title"] == selected_esc)

        col_esc, col_esc_chart = st.columns([1, 1.5])

        with col_esc:
            st.markdown(f"""
            <div style="background:{esc_data['color']};border-left:4px solid {esc_data['border']};
                        border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:12px;">
                <div style="font-weight:700;color:{esc_data['border']};margin-bottom:6px;">{esc_data['title']}</div>
                <div style="font-size:13px;color:#475569;line-height:1.6;">{esc_data['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**수식:**")
            st.code(esc_data["eq"], language=None)
            st.metric("예상 RMSE", esc_data["rmse"])

            st.markdown("**모델 포함 요소:**")
            components = [
                ("✅" if esc_data["R0"] > 0 else "❌", "등가 직렬 저항 R₀"),
                ("✅" if esc_data["R1"] > 0 else "❌", "RC 확산 전압"),
                ("✅" if esc_data["hys"] else "❌", "히스테리시스"),
            ]
            for icon, name in components:
                st.markdown(f"{icon} {name}")

        with col_esc_chart:
            # Simulate this step
            t_sim = list(range(81))
            R0_s, R1_s, C1_s = esc_data["R0"], esc_data["R1"], esc_data["C1"]
            I_s = 5.0
            ocv_base = 4.1
            irc_s = 0.0
            v_sim, ocv_sim = [], []
            for tt in t_sim:
                ocv_sim.append(ocv_base)
                if tt < 5:
                    v_sim.append(ocv_base)
                    irc_s = 0.0
                else:
                    if C1_s > 1e6:
                        irc_s = I_s
                    else:
                        F = exp(-1 / (R1_s * C1_s))
                        irc_s = F * irc_s + (1 - F) * I_s
                    vt = ocv_base - R1_s * irc_s - R0_s * I_s
                    if esc_data["hys"] and tt >= 5:
                        vt += 0.015  # simplified hysteresis offset
                    v_sim.append(vt)

            fig_esc = go.Figure()
            fig_esc.add_trace(go.Scatter(x=t_sim, y=ocv_sim, name="OCV (기준)",
                                         line=dict(color="#dc2626", width=1.5, dash="dash")))
            fig_esc.add_trace(go.Scatter(x=t_sim, y=v_sim, name="모델 출력",
                                         line=dict(color=esc_data["border"], width=2.5),
                                         fill="tonexty", fillcolor=esc_data["color"]+"80"))
            fig_esc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=10, t=30, b=30), height=260,
                xaxis_title="시간 (s)", yaxis_title="전압 (V)",
                legend=dict(orientation="h", y=-0.2),
                title=f"단계별 전압 응답 (I=5A)",
            )
            st.plotly_chart(fig_esc, use_container_width=True)

# ──────────────────────────────────────────────
# PAGE: 파라미터 계산기
# ──────────────────────────────────────────────
elif page == "🧮 파라미터 계산기":
    st.markdown("## 🧮 파라미터 계산기")

    col_calc, col_sim = st.columns(2)

    # ── RC 파라미터 계산기 ──
    with col_calc:
        st.markdown("### ⚡ RC 파라미터 계산기")
        st.markdown("교재 실험값(Δi=5A)을 기본값으로 설정했습니다.")

        with st.form("calc_form"):
            c1, c2 = st.columns(2)
            with c1:
                R1_c = st.number_input("R₁ 분극 저항 (mΩ)", 0.1, 1000.0, 15.8, 0.1)
                R0_c = st.number_input("R₀ 직렬 저항 (mΩ)", 0.1, 1000.0, 8.2, 0.1)
            with c2:
                C1_c = st.number_input("C₁ 분극 커패시턴스 (F)", 1.0, 1000000.0, 38000.0, 100.0)
                di_c = st.number_input("전류 Δi (A)", 0.1, 1000.0, 5.0, 0.5)
            submitted = st.form_submit_button("🔢 계산", type="primary", use_container_width=True)

        if submitted:
            R1_si = R1_c / 1000
            R0_si = R0_c / 1000
            C1_si = C1_c
            tau = R1_si * C1_si
            tau4 = 4 * tau
            dv0 = R0_si * di_c * 1000
            dvinf = (R0_si + R1_si) * di_c * 1000
            F1 = exp(-1 / tau) if tau > 0 else 0

            st.markdown("---")
            st.markdown("#### 📊 계산 결과")
            rc1, rc2 = st.columns(2)
            rc1.metric("시정수 τ = R₁×C₁", f"{tau:.1f} s ({tau/60:.1f}분)")
            rc2.metric("4τ (98% 수렴)", f"{tau4:.1f} s ({tau4/60:.1f}분)")
            rc1.metric("순간 강하 ΔV₀", f"{dv0:.2f} mV")
            rc2.metric("정상상태 강하 ΔV∞", f"{dvinf:.2f} mV")
            st.metric("속도계수 F₁ = exp(−1s/τ)", f"{F1:.6f}")

            st.markdown("**📐 상세 계산:**")
            st.code(f"""τ = R₁ × C₁ = {R1_c}mΩ × {C1_c:.0f}F = {tau:.2f} s
F₁ = exp(−1/{tau:.2f}) = {F1:.6f}
ΔV₀ = R₀ × Δi = {R0_c}×10⁻³ × {di_c} = {dv0:.2f} mV
ΔV∞ = (R₀+R₁) × Δi = ({R0_c}+{R1_c})×10⁻³ × {di_c} = {dvinf:.2f} mV""", language=None)

            st.markdown(f"""
            <div class="{'success-box' if abs(tau-600)<100 else 'info-box'}">
                💡 교재 기준값: τ=600s | ΔV₀=41mV | ΔV∞=120mV<br>
                현재 계산값과 {'거의 일치합니다 ✓' if abs(tau-600)<100 else '차이가 있습니다.'}
            </div>
            """, unsafe_allow_html=True)

    # ── 전압 응답 시뮬레이터 ──
    with col_sim:
        st.markdown("### 📊 전압 응답 시뮬레이터")
        st.markdown("파라미터를 바꾸면 그래프가 실시간으로 업데이트됩니다.")

        s_I = st.slider("방전 전류 I (A)", 1.0, 100.0, 20.0, 1.0)
        s_R0 = st.slider("R₀ (mΩ)", 1.0, 50.0, 8.2, 0.1)
        s_R1 = st.slider("R₁ (mΩ)", 1.0, 50.0, 15.8, 0.1)
        s_C1 = st.slider("C₁ (kF)", 1.0, 100.0, 38.0, 1.0)

        ocv = 4.1
        t_s = list(range(81))
        R0_s = s_R0 / 1000
        R1_s = s_R1 / 1000
        C1_s = s_C1 * 1000
        irc_s = 0.0
        v_s, ocv_s = [], []
        for tt in t_s:
            ocv_s.append(ocv)
            if tt < 5:
                v_s.append(ocv); irc_s = 0.0
            else:
                F = exp(-1 / (R1_s * C1_s))
                irc_s = F * irc_s + (1 - F) * s_I
                v_s.append(ocv - R1_s * irc_s - R0_s * s_I)

        tau_s = R1_s * C1_s
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=t_s, y=ocv_s, name="OCV 기준선",
                                   line=dict(color="#dc2626", width=1.5, dash="dash")))
        fig_s.add_trace(go.Scatter(x=t_s, y=v_s, name="단자 전압 V(t)",
                                   fill="tonexty", fillcolor="rgba(26,95,168,0.07)",
                                   line=dict(color="#1a5fa8", width=2.5)))
        fig_s.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=30, r=10, t=40, b=30), height=280,
            xaxis_title="시간 (s)", yaxis_title="전압 (V)",
            legend=dict(orientation="h", y=-0.2),
            title=f"I={s_I}A, R₀={s_R0}mΩ, τ={tau_s:.0f}s",
        )
        st.plotly_chart(fig_s, use_container_width=True)

        vdrop_total = (R0_s + R1_s) * s_I * 1000
        st.markdown(f"""
        <div class="info-box">
            ⚡ 방전 시 총 전압 강하: <strong>{vdrop_total:.1f} mV</strong>
            (R₀: {R0_s*s_I*1000:.1f}mV + R₁: {R1_s*s_I*1000:.1f}mV)<br>
            ⏱️ 시정수 τ = {tau_s:.0f}s | 4τ = {4*tau_s:.0f}s ({4*tau_s/60:.1f}분에 98% 수렴)
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAGE: 퀴즈
# ──────────────────────────────────────────────
elif page == "📝 이해도 퀴즈":
    st.markdown("## 📝 이해도 퀴즈")
    st.markdown("**10문제** · 4지선다 · 정답 해설 포함")

    QUIZ = [
        {
            "q": "개방회로 전압(OCV)을 측정할 때 전류를 0에 가깝게 유지해야 하는 이유는?",
            "opts": ["배터리가 폭발할 수 있어서", "R₀·i 강하와 RC 분극 없이 순수 평형 전압을 측정하기 위해", "온도 측정 정확도를 위해", "쿨롱 효율을 높이기 위해"],
            "ans": 1,
            "exp": "OCV는 순수한 전기화학적 평형 전압입니다. 전류가 흐르면 R₀·i 강하와 RC 분극이 추가되어 실제 OCV와 달라집니다. C/30 이하 전류에서는 이런 추가 전압이 무시할 정도로 작아집니다.",
            "formula": "v = OCV(z)  |  i → 0 이면 ε → 0",
        },
        {
            "q": "이산시간 SoC 점화식에서 쿨롱 효율(η)의 일반적 값은?",
            "opts": ["약 70~80%", "약 85~90%", "약 95~98%", "약 99~99.9%"],
            "ans": 3,
            "exp": "리튬이온 배터리의 쿨롱 효율은 99~99.9%로 매우 높습니다. 대부분의 BMS에서 η=1로 단순화합니다.",
            "formula": "z[k+1] = z[k] − (Δt/Q)·η·i[k]  →  η ≈ 0.999~1",
        },
        {
            "q": "R₀(등가 직렬 저항)를 펄스 응답으로 추출할 때 사용하는 공식은?",
            "opts": ["R₀ = ΔV∞/Δi (정상상태)", "R₀ = |ΔV₀/Δi| (순간 강하)", "R₀ = τ/(R₁C₁)", "R₀ = −ln(F₁)·Δt"],
            "ans": 1,
            "exp": "커패시터(C₁)의 전압은 순간적으로 변하지 않습니다. 따라서 전류 인가/차단 직후의 순간 전압 강하 ΔV₀는 오로지 R₀에 의한 것입니다.",
            "formula": "R₀ = |ΔV₀/Δi|  (예: 41mV÷5A = 8.2mΩ)",
        },
        {
            "q": "ZOH 이산화 속도계수 F₁의 물리적 의미는?",
            "opts": ["샘플링 주기와 시정수의 비율", "한 샘플 후 잔류하는 RC 전류의 비율 (0<F₁<1)", "전류 이득", "전압 분배 비율"],
            "ans": 1,
            "exp": "F₁=exp(−Δt/R₁C₁)은 한 샘플 주기 후 RC 전류가 얼마나 남는지를 나타냅니다. τ→∞이면 F₁→1(변하지 않음), τ→0이면 F₁→0(즉각 반응).",
            "formula": "i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]  |  F₁=exp(−Δt/τ)",
        },
        {
            "q": "히스테리시스 전압과 확산 전압(RC)의 가장 큰 차이는?",
            "opts": ["히스테리시스가 항상 더 크다", "히스테리시스는 시간이 지나도 소멸하지 않고 SoC 변화에만 의존한다", "확산 전압이 측정하기 더 어렵다", "히스테리시스는 NMC에서 크게 나타난다"],
            "ans": 1,
            "exp": "RC 확산 전압은 전류를 끊으면 시간이 지나 0으로 소멸합니다. 반면 히스테리시스 전압은 시간에 무관하고 오직 SoC가 변할 때만 변합니다.",
            "formula": "V_hys[k] = M₀·s[k] + M·h[k]  (시간 t에 직접 의존 없음)",
        },
        {
            "q": "교재 펄스 테스트(Δi=5A)에서 RC 시정수 τ=R₁C₁의 값은?",
            "opts": ["약 60초 (1분)", "약 600초 (10분)", "약 2400초 (40분)", "약 6000초 (100분)"],
            "ans": 1,
            "exp": "R₁≈15.8mΩ, C₁≈38kF이므로 τ=0.0158×38000≈600.4초(약 10분). 4τ≈2400초(40분)에서 98% 수렴합니다.",
            "formula": "τ = R₁×C₁ = 15.8×10⁻³ × 38×10³ ≈ 600 s  |  4τ≈2400 s",
        },
        {
            "q": "ESC 모델을 '자가 교정(Self-Correcting)'이라 부르는 이유는?",
            "opts": ["파라미터가 온라인으로 자동 업데이트되어서", "전류=0 휴지 시 전압이 자동으로 OCV+히스테리시스 평형값으로 수렴해서", "오류 발생 시 자동으로 재시작해서", "온도 변화에 자동 대응해서"],
            "ans": 1,
            "exp": "셀이 쉴 때(i=0) RC 전류가 0으로 수렴하고, 히스테리시스는 현재 값 유지. 따라서 모델 전압이 자발적으로 OCV+히스테리시스 평형값으로 수렴합니다.",
            "formula": "i→0 시: v[k]→OCV(z,T)+M₀·s[k]+M·h[k]  (자동 평형)",
        },
        {
            "q": "와버그 임피던스가 나이키스트 플롯에서 45° 직선으로 나타나는 이유는?",
            "opts": ["전극 저항이 주파수에 무관하기 때문", "Z_W=A_W/√(jω)에서 실수부와 허수부가 동일하기 때문", "커패시턴스가 매우 크기 때문", "전해질 저항이 0이기 때문"],
            "ans": 1,
            "exp": "Z_W=A_W/√(jω)를 분해하면 Re(Z_W)=Im(Z_W)가 됩니다. 복소 평면에서 실수부=허수부인 점의 궤적은 정확히 45° 직선입니다.",
            "formula": "Z_W=A_W/√(jω)  →  |Z_re|=|Z_im|  →  위상각=45°",
        },
        {
            "q": "OCV 4-스크립트 테스트에서 Script 2와 4를 25°C에서 수행하는 이유는?",
            "opts": ["장비 안전을 위해", "저/고온 후 잔류 용량을 뽑아 SoC 기준점(0% 또는 100%)을 정확히 확인하기 위해", "25°C에서만 OCV를 측정할 수 있어서", "챔버 에너지 절약을 위해"],
            "ans": 1,
            "exp": "저온이나 고온에서는 전압 컷오프가 실제 완방전/완충과 다를 수 있습니다. 25°C에서 C/30으로 잔류 용량을 확인해야 SoC 기준점을 정확히 설정할 수 있습니다.",
            "formula": "Script1(방전)→Script2(25°C 확인)→Script3(충전)→Script4(25°C 확인)",
        },
        {
            "q": "ESC 모델의 근본적 한계는?",
            "opts": ["연산량이 너무 많아 실시간 불가능", "현상론적 블랙박스로 노화·덴드라이트 등 화학적 현상을 예측할 수 없다", "OCV 측정이 불가능하다", "RC 파라미터 추출이 불가능하다"],
            "ans": 1,
            "exp": "ESC는 과거 데이터에 피팅된 현상론적(black-box) 모델로, 단기 전압-전류 예측에는 우수하지만 SEI 성장, 리튬 덴드라이트, 장기 노화 예측 등은 불가능합니다.",
            "formula": "차세대: ECM+DFN+LSTM 하이브리드 → 목표 RMSE≤2mV",
        },
    ]

    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_answered = False
        st.session_state.quiz_done = False

    if st.button("🔄 퀴즈 다시 시작", use_container_width=False):
        st.session_state.quiz_idx = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_answered = False
        st.session_state.quiz_done = False
        st.rerun()

    if st.session_state.quiz_done:
        score = st.session_state.quiz_score
        total = len(QUIZ)
        pct = int(score / total * 100)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e8f1fb,#f0f9ff);border:1px solid #bae6fd;
                    border-radius:14px;padding:32px;text-align:center;margin:20px 0;">
            <div style="font-size:48px;margin-bottom:12px;">🎉</div>
            <div style="font-size:42px;font-weight:700;color:#1a5fa8;font-family:monospace;">{score} / {total}</div>
            <div style="font-size:18px;color:#475569;margin-top:8px;">
                {('🏆 완벽! 배터리 모델링 마스터!' if pct>=90 else '👍 훌륭합니다! 조금만 더 복습하면 완벽.' if pct>=70 else '📚 절반 이상! 수식 모음을 다시 확인하세요.' if pct>=50 else '💡 다시 도전! 섹션 카드를 먼저 읽어보세요.')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("다시 풀기 ↺", type="primary"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_answered = False
            st.session_state.quiz_done = False
            st.rerun()
    else:
        idx = st.session_state.quiz_idx
        q = QUIZ[idx]

        # Progress
        progress_val = idx / len(QUIZ)
        st.progress(progress_val, text=f"문제 {idx+1} / {len(QUIZ)}  |  현재 점수: {st.session_state.quiz_score}점")
        st.markdown("")

        st.markdown(f"### Q{idx+1}. {q['q']}")

        if not st.session_state.quiz_answered:
            for i, opt in enumerate(q["opts"]):
                label = f"{chr(65+i)}. {opt}"
                if st.button(label, key=f"opt_{idx}_{i}", use_container_width=True):
                    st.session_state.quiz_answered = True
                    st.session_state.selected = i
                    if i == q["ans"]:
                        st.session_state.quiz_score += 1
                    st.rerun()
        else:
            sel = st.session_state.selected
            for i, opt in enumerate(q["opts"]):
                label = f"{chr(65+i)}. {opt}"
                if i == q["ans"]:
                    st.success(f"✅ {label}")
                elif i == sel and i != q["ans"]:
                    st.error(f"❌ {label}")
                else:
                    st.markdown(f"<div style='padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;color:#94a3b8;margin:4px 0;'>{label}</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="info-box">
                <strong>💡 해설:</strong> {q['exp']}
                <div style="margin-top:8px;background:#0f172a;padding:8px 12px;border-radius:6px;font-family:monospace;font-size:12px;color:#7dd3fc;">{q['formula']}</div>
            </div>
            """, unsafe_allow_html=True)

            col_next, col_skip = st.columns([1, 1])
            with col_next:
                if st.button("다음 문제 →", type="primary", use_container_width=True):
                    st.session_state.quiz_idx += 1
                    st.session_state.quiz_answered = False
                    if st.session_state.quiz_idx >= len(QUIZ):
                        st.session_state.quiz_done = True
                    st.rerun()
            with col_skip:
                if idx < len(QUIZ) - 1:
                    if st.button("건너뛰기", use_container_width=True):
                        st.session_state.quiz_idx += 1
                        st.session_state.quiz_answered = False
                        st.rerun()
