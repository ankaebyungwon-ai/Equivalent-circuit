"""
BatteryIQ — 배터리 건강 추정 연구 포털
군산대학교 기계공학부 | Gregory Plett · Ch 2-04
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import requests
import base64
import io
from math import exp
from PIL import Image, ImageDraw, ImageFilter

st.set_page_config(
    page_title="BatteryIQ — 배터리 건강 추정 연구 포털",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────
# IMAGE HELPERS
# ────────────────────────────────────────
def _b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data
def hero_img(w=1600, h=680):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r, g, b = int(8+t*6), int(18+t*14), int(28+t*22)
        draw.line([(0,y),(w,y)], fill=(r,g,b))
    for x in range(0, w, 80):
        draw.line([(x,0),(x,h)], fill=(45,212,191,12))
    for y2 in range(0, h, 80):
        draw.line([(0,y2),(w,y2)], fill=(45,212,191,12))
    img = img.filter(ImageFilter.GaussianBlur(1))
    return _b64(img)

@st.cache_data
def card_img(c1, c2, w=800, h=500):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y/h
        draw.line([(0,y),(w,y)], fill=tuple(int(c1[i]+t*(c2[i]-c1[i])) for i in range(3)))
    return _b64(img)

@st.cache_data
def logo_img(sz=64):
    img = Image.new("RGBA", (sz, sz), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0,0,sz-1,sz-1], radius=14, fill=(45,212,191))
    bx,by,bw,bh = 14,20,28,20
    draw.rectangle([bx,by,bx+bw,by+bh], outline=(255,255,255), width=3)
    draw.rectangle([bx+bw,by+6,bx+bw+5,by+bh-6], fill=(255,255,255))
    draw.rectangle([bx+3,by+3,bx+int(bw*.7),by+bh-3], fill=(255,255,255))
    return _b64(img)

LOGO = logo_img()
HERO = hero_img()

# ────────────────────────────────────────
# CSS
# ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Roboto+Mono:wght@400;500&display=swap');
html,body,[class*="css"],.stApp{font-family:'Noto Sans KR',sans-serif!important;background:#fff;}
#MainMenu,footer,.stDeployButton,[data-testid="stToolbar"],[data-testid="stHeader"]{display:none!important;}

/* NAV */
.nav{position:fixed;top:0;left:0;right:0;z-index:9999;background:rgba(255,255,255,0.97);
     backdrop-filter:blur(12px);border-bottom:1px solid rgba(0,0,0,0.06);
     display:flex;align-items:center;justify-content:space-between;padding:0 56px;height:68px;}
.nav-logo{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:700;color:#0f172a;}
.nav-links{display:flex;gap:40px;}
.nav-links a{font-size:14px;font-weight:500;color:#475569;text-decoration:none;transition:color .15s;}
.nav-links a:hover{color:#0f172a;}
.nav-right{display:flex;align-items:center;gap:16px;font-size:12px;color:#94a3b8;}
.nav-sep{width:1px;height:20px;background:#e2e8f0;}

/* HERO */
.hero-wrap{position:relative;overflow:hidden;min-height:640px;display:flex;align-items:center;}
.hero-overlay{position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(7,16,19,.92) 0%,rgba(12,30,42,.85) 40%,rgba(14,45,62,.75) 100%);}
.hero-grid{position:absolute;inset:0;
  background-image:linear-gradient(rgba(45,212,191,.04)1px,transparent 1px),
                   linear-gradient(90deg,rgba(45,212,191,.04)1px,transparent 1px);
  background-size:80px 80px;}
.hero-content{position:relative;z-index:2;padding:100px 80px;}
.hero-eyebrow{font-size:11px;letter-spacing:.2em;color:#2dd4bf;text-transform:uppercase;
              display:flex;align-items:center;gap:12px;margin-bottom:28px;}
.hero-eyebrow::before{content:'';display:inline-block;width:40px;height:1px;background:#2dd4bf;}
.hero-title{font-size:72px;font-weight:900;line-height:1.0;color:#fff;margin-bottom:20px;}
.hero-em{color:#2dd4bf;}
.hero-sub{font-size:15px;color:rgba(255,255,255,.5);line-height:1.75;max-width:460px;}
.hero-scroll{position:absolute;bottom:36px;right:56px;color:rgba(255,255,255,.25);
             font-size:10px;letter-spacing:.2em;writing-mode:vertical-rl;
             display:flex;align-items:center;gap:8px;}
.hero-scroll::after{content:'';display:inline-block;width:1px;height:56px;background:rgba(255,255,255,.12);}

/* SECTIONS */
.eyebrow{font-size:11px;letter-spacing:.16em;color:#2dd4bf;text-transform:uppercase;
         display:flex;align-items:center;gap:10px;margin-bottom:28px;}
.eyebrow::before{content:'';display:inline-block;width:28px;height:1px;background:#2dd4bf;}
.t-xl{font-size:52px;font-weight:900;color:#0f172a;line-height:1.08;margin-bottom:12px;}
.t-lg{font-size:38px;font-weight:900;color:#0f172a;line-height:1.1;margin-bottom:16px;}
.body-txt{font-size:15px;color:#475569;line-height:1.75;}

/* WHY */
.why-num{font-size:30px;font-weight:900;color:#2dd4bf;opacity:.45;min-width:44px;
         font-family:'Roboto Mono',monospace;line-height:1;}
.why-title{font-size:16px;font-weight:700;color:#0f172a;margin-bottom:5px;}
.why-body{font-size:13px;color:#64748b;line-height:1.65;}

/* STATS BAR */
.stats-bar{background:#0f172a;padding:60px 80px;
           display:grid;grid-template-columns:repeat(4,1fr);gap:40px;}
.stat-num{font-size:52px;font-weight:900;color:#2dd4bf;font-family:'Roboto Mono',monospace;line-height:1;}
.stat-lbl{font-size:11px;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:6px;}

/* TOPIC CARD */
.tc{position:relative;overflow:hidden;cursor:pointer;height:320px;}
.tc:hover .tc-img{transform:scale(1.04);}
.tc-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
        opacity:.72;transition:transform .4s;}
.tc-fade{position:absolute;inset:0;
         background:linear-gradient(to top,rgba(0,0,0,.88) 0%,rgba(0,0,0,.25) 50%,transparent 100%);}
.tc-body{position:absolute;bottom:0;left:0;right:0;padding:28px 32px;}
.tc-eye{font-size:9px;letter-spacing:.2em;color:#2dd4bf;font-weight:700;margin-bottom:8px;}
.tc-t{font-size:22px;font-weight:800;color:#fff;line-height:1.2;margin-bottom:4px;}
.tc-sub{font-size:12px;color:rgba(255,255,255,.45);margin-bottom:14px;}
.tc-more{font-size:12px;color:#2dd4bf;font-weight:600;letter-spacing:.04em;}

/* NEWS */
.nc-date{font-size:11px;color:#2dd4bf;margin-bottom:8px;font-weight:600;}
.nc-title{font-size:14px;font-weight:700;color:#0f172a;line-height:1.5;margin-bottom:5px;}
.nc-src{font-size:11px;color:#94a3b8;}

/* TOPIC DETAIL */
.kp-card{background:#f8fafc;border:1px solid #e2e8f0;border-left:3px solid #2dd4bf;
         border-radius:0 10px 10px 0;padding:16px;margin-bottom:10px;}
.kp-ico{font-size:22px;margin-bottom:5px;}
.kp-t{font-size:13px;font-weight:700;color:#0f172a;margin-bottom:3px;}
.kp-d{font-size:12px;color:#475569;line-height:1.6;}

/* EQ BOX */
.eq-box{background:#0f172a;border-radius:10px;padding:18px 22px;
        font-family:'Roboto Mono',monospace;font-size:13px;color:#7dd3fc;
        line-height:2.1;border-left:3px solid #2dd4bf;overflow-x:auto;margin:10px 0;}

/* FOOTER */
.ft{background:#0f172a;padding:40px 80px;
    display:flex;justify-content:space-between;align-items:center;}
.ft-logo{font-size:16px;font-weight:700;color:#fff;}
.ft-links a{font-size:12px;color:rgba(255,255,255,.35);text-decoration:none;margin-left:20px;}
.ft-copy{font-size:11px;color:rgba(255,255,255,.25);}

/* STREAMLIT OVERRIDES */
.stButton>button{background:#2dd4bf!important;color:#0f172a!important;
  font-weight:700!important;border:none!important;border-radius:6px!important;
  font-family:'Noto Sans KR',sans-serif!important;}
.stButton>button:hover{background:#0d9488!important;color:#fff!important;}
[data-testid="metric-container"]{background:#f8fafc!important;
  border:1px solid #e2e8f0!important;border-radius:8px!important;
  border-left:3px solid #2dd4bf!important;padding:14px!important;}
[data-baseweb="tab"][aria-selected="true"]{color:#2dd4bf!important;}
[data-baseweb="tab-highlight"]{background-color:#2dd4bf!important;}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────
# TOPIC DATA
# ────────────────────────────────────────
TOPICS = [
    {"id":"t01","num":"TOPIC 01","title":"배터리 건강 추정의 필요성","sub":"안전한 배터리 운용의 시작","c1":(12,22,38),"c2":(20,45,70)},
    {"id":"t02","num":"TOPIC 02","title":"SoH 정의와 측정 방법","sub":"용량 기반 vs 저항 기반","c1":(10,22,48),"c2":(15,42,80)},
    {"id":"t03","num":"TOPIC 03","title":"등가회로 모델 (ECM)","sub":"1RC·2RC·ESC 모델 비교","c1":(15,35,30),"c2":(25,60,50)},
    {"id":"t04","num":"TOPIC 04","title":"쿨롱 카운팅 & SoC 추정","sub":"이산시간 점화식 구현","c1":(38,22,12),"c2":(65,42,18)},
    {"id":"t05","num":"TOPIC 05","title":"확장 칼만 필터 (EKF)","sub":"노이즈 속 최적 상태 추정","c1":(28,12,48),"c2":(52,22,80)},
    {"id":"t06","num":"TOPIC 06","title":"노화 메커니즘과 SEI","sub":"리튬 석출·용량 감소 원인","c1":(42,10,10),"c2":(75,18,18)},
    {"id":"t07","num":"TOPIC 07","title":"칼만 필터 파라미터 추정","sub":"노이즈 속 최적 추정","c1":(10,32,38),"c2":(14,56,68)},
    {"id":"t08","num":"TOPIC 08","title":"EIS와 와버그 임피던스","sub":"주파수 영역 특성 분석","c1":(32,18,42),"c2":(58,32,72)},
    {"id":"t09","num":"TOPIC 09","title":"히스테리시스 모델링","sub":"경로 의존적 전압 거동","c1":(12,38,22),"c2":(22,66,42)},
    {"id":"t10","num":"TOPIC 10","title":"UDDS 검증 실험","sub":"실차 주행 사이클 적용","c1":(38,28,8),"c2":(68,52,14)},
    {"id":"t11","num":"TOPIC 11","title":"온도 의존성 파라미터","sub":"아레니우스 방정식 적용","c1":(8,18,42),"c2":(12,32,75)},
    {"id":"t12","num":"TOPIC 12","title":"ML 하이브리드 모델","sub":"LSTM + ECM 결합","c1":(38,8,28),"c2":(72,14,52)},
]

DETAIL = {
"t01":{
    "title":"배터리 건강 추정의 필요성","tags":["SoH","안전성","RUL"],
    "kps":[
        {"i":"⚡","t":"안전성 확보","d":"과충전·과방전을 실시간으로 방지하여 배터리 열폭주 등 위험 상황을 사전에 예방합니다."},
        {"i":"🔮","t":"수명 예측 (RUL)","d":"잔여 유용 수명을 정확히 예측하여 배터리 교체 시점을 최적화하고 유지보수 비용을 절감합니다."},
        {"i":"📈","t":"성능 최적화","d":"실시간 SoH 데이터를 활용한 에너지 관리 전략으로 EV 주행거리와 충전 효율을 극대화합니다."},
        {"i":"💰","t":"경제적 가치","d":"배터리 2차 활용(2nd Life) 시장에서 정확한 SoH 정보는 재판매 가격과 직결됩니다."},
    ],
    "body":"""
**SoH(State of Health)** 는 배터리의 현재 상태를 초기 상태 대비 비율로 나타내는 핵심 지표입니다.

일반적으로 SoH가 **80% 이하**로 떨어지면 EV 배터리를 교체해야 합니다. 정확한 SoH 추정은 안전·경제·환경 세 가지 이유에서 필수적입니다.

1. **안전**: 열화된 배터리는 급격한 용량 감소와 열폭주 위험이 증가합니다
2. **경제**: 조기 교체는 비용 낭비, 지연 교체는 안전 위험입니다
3. **환경**: 정확한 수명 예측으로 폐배터리 재활용 효율을 높입니다
    """,
    "eqs":[{"t":"SoH 용량 기반 정의","c":"SoH_C = Q_max(t) / Q_max(t=0) × 100%\n\n// Q_max: 현재 최대 방전 용량 [Ah]\n// 신품: SoH=100% | 교체 기준: SoH=80%","d":"가장 직관적인 SoH 정의."}],
    "refs":[("Plett 2015","Plett, G.L. (2015). Battery Management Systems, Vol.II. Artech House.","")],
},
"t03":{
    "title":"등가회로 모델 (ECM)","tags":["ECM","1RC","ESC","ZOH"],
    "kps":[
        {"i":"⚡","t":"R₀ — 직렬 저항","d":"전해질+집전체+SEI 저항. 순간 전압 강하. 교재: 8.2mΩ (Δi=5A 펄스)."},
        {"i":"🌊","t":"RC — 확산 전압","d":"리튬 이온 농도 구배. ZOH 이산화로 MCU 구현. τ=R₁C₁≈600s (교재값)."},
        {"i":"🔄","t":"히스테리시스","d":"충방전 경로 의존성. LFP에서 50~100mV. 동적+순간 2종으로 모델링."},
        {"i":"🎯","t":"ESC 완성 모델","d":"OCV+R₀+RC+히스테리시스 통합. UDDS 10h 검증: RMSE=5.37mV."},
    ],
    "body":"""
등가회로 모델(ECM)은 배터리의 전기적 특성을 전기 소자 조합으로 표현합니다.

**단계별 모델 완성:**
- Step 1: v = OCV(z) → 오차 ~100mV
- Step 2: v = OCV(z) − R₀·i → 오차 ~50mV
- Step 3: v = OCV(z) − R₁·i_R1 − R₀·i → 오차 ~10mV
- Step 4: ESC 완성 (+ 히스테리시스) → **오차 5.37mV** ✓
    """,
    "eqs":[
        {"t":"ZOH 이산화 RC 점화식 (식 2.8)","c":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt / R₁C₁)\n\n// 교재값: R₁=15.8mΩ, C₁=38kF → τ=600s","d":"ZOH 이산화로 얻은 RC 점화식."},
        {"t":"ESC 최종 출력 방정식","c":"v[k] = OCV(z[k],T[k]) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]","d":"모든 요소를 통합한 ESC 최종 출력."},
    ],
    "refs":[("Plett 2004","Plett, G.L. (2004). J. Power Sources, 134. DOI: 10.1016/j.jpowsour.2004.02.032","10.1016/j.jpowsour.2004.02.032")],
},
"t05":{
    "title":"확장 칼만 필터 (EKF)","tags":["EKF","칼만 필터","SoC","노이즈"],
    "kps":[
        {"i":"📡","t":"상태 추정","d":"측정 노이즈 속에서 SoC를 최적으로 추정. 예측+업데이트 2단계 반복."},
        {"i":"🔄","t":"자가 교정","d":"전압 측정값과 모델 예측의 차이(혁신)로 SoC를 지속적으로 교정."},
        {"i":"📊","t":"칼만 이득 K","d":"모델 불확실성 vs 측정 불확실성의 균형으로 최적 업데이트 비율 결정."},
        {"i":"⚡","t":"ESC+EKF","d":"ESC 상태방정식 + EKF = 실시간 SoC·파라미터 동시 추정 시스템."},
    ],
    "body":"""
확장 칼만 필터(EKF)는 비선형 시스템에서 최적 상태 추정을 수행합니다.

**EKF 2단계 반복:**
1. **예측**: 이전 상태로 현재 상태와 불확실성(P) 예측
2. **업데이트**: 실제 측정값으로 예측 보정 (칼만 이득 K 사용)

칼만 이득 K=0이면 모델만, K=1이면 측정값만 신뢰합니다.
    """,
    "eqs":[
        {"t":"EKF 예측 단계","c":"x̂[k|k-1] = f(x̂[k-1], u[k-1])  // 상태 예측\nP[k|k-1] = A·P[k-1]·Aᵀ + Q     // 오차 공분산","d":"EKF 예측 단계."},
        {"t":"EKF 업데이트 단계","c":"K[k] = P[k|k-1]·Cᵀ·(C·P[k|k-1]·Cᵀ + R)⁻¹\nx̂[k] = x̂[k|k-1] + K[k]·(y[k] − ŷ[k|k-1])\nP[k] = (I − K[k]·C)·P[k|k-1]","d":"칼만 이득으로 상태 업데이트."},
    ],
    "refs":[("Plett 2004 II","Plett, G.L. (2004). J. Power Sources, 134(2), 262–276.","10.1016/j.jpowsour.2004.02.033")],
},
"t07":{
    "title":"칼만 필터 파라미터 추정","tags":["칼만 필터","Q","R","튜닝"],
    "kps":[
        {"i":"🎯","t":"Q — 프로세스 노이즈","d":"모델 불확실성. 크면 측정값 더 신뢰. 작으면 모델 더 신뢰."},
        {"i":"📡","t":"R — 측정 노이즈","d":"센서 불확실성. 전압 측정 노이즈 분산. 보통 (1~10mV)² 수준."},
        {"i":"🔢","t":"초기 공분산 P₀","d":"초기 불확실성. 너무 작으면 초기 수렴 실패. 대각 행렬로 설정."},
        {"i":"⚙️","t":"튜닝 전략","d":"오프라인 실험 데이터로 Q, R을 최적화. RMSE 기반 파라미터 탐색."},
    ],
    "body":"""
칼만 필터 파라미터(Q, R, P₀)는 필터 성능을 결정하는 핵심 요소입니다.

**튜닝 원칙:**
- **Q가 크면**: 측정값을 더 신뢰 → 빠른 응답, 노이즈에 민감
- **Q가 작으면**: 모델을 더 신뢰 → 부드러운 추정, 수렴 느림
- **R**은 실제 센서 노이즈 분산으로 직접 설정 가능

실용적 접근: 먼저 R을 실험으로 결정하고, Q를 반복 튜닝합니다.
    """,
    "eqs":[{"t":"노이즈 공분산 설정 (교재 권장)","c":"Q = diag([1e-8, 1e-6, 1e-6])  // 프로세스 노이즈\nR = 1e-6                       // 측정 노이즈 (1mV)²\nP₀= diag([1e-4, 1e-4, 1e-4])  // 초기 불확실성","d":"노이즈 공분산 행렬 설정."}],
    "refs":[("Welch 1995","Welch, G., & Bishop, G. (1995). An Introduction to the Kalman Filter. UNC-Chapel Hill.","")],
},
}

NEWS = [
    {"date":"Wed, 22 Oct","title":"전기차 배터리의 안전성과 수명을 예측하고 진단하는 AI 플랫폼을 개발하는 '퀀텀하이텍'","src":"KR 모바일한경","c1":(15,25,45),"c2":(8,12,28)},
    {"date":"Sun, 05 Apr","title":"[포커스] LG엔솔, 소프트웨어·서비스 중심 기업으로의 전략적 전환...왜?","src":"KR 투데이에너지","c1":(25,40,25),"c2":(12,28,12)},
    {"date":"Fri, 03 Apr","title":"LG에너지솔루션, 배터리 기업 최초 글로벌 車 SW 오픈 마켓 '에스디버스' 합류","src":"KR 핀테크경제신문","c1":(12,20,42),"c2":(6,10,28)},
    {"date":"Wed, 15 Jan","title":"[2025년 딥테크 강소기업 탐방]〈4〉 휴컨 - 전자신문","src":"KR 전자신문","c1":(32,18,45),"c2":(18,8,30)},
]

# OCV helper
OCV_T = [3.0,3.35,3.55,3.65,3.72,3.78,3.85,3.92,4.0,4.1,4.2]
def ocv(z):
    z = max(0.0, min(1.0, z))
    i = min(int(z*10), 9); f = z*10-i
    return OCV_T[i]+f*(OCV_T[i+1]-OCV_T[i])

def dk(**kw):
    b = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,23,35,.95)",
             font=dict(family="Noto Sans KR",color="#94a3b8"),
             margin=dict(l=40,r=20,t=40,b=40),
             xaxis=dict(gridcolor="rgba(45,212,191,.08)",zerolinecolor="rgba(45,212,191,.15)",color="#475569"),
             yaxis=dict(gridcolor="rgba(45,212,191,.08)",zerolinecolor="rgba(45,212,191,.15)",color="#475569"),
             legend=dict(orientation="h",y=-0.22,font=dict(size=11)))
    b.update(kw); return b

# ────────────────────────────────────────
# ROUTING
# ────────────────────────────────────────
qp = st.query_params
page = qp.get("page","home")
tid  = qp.get("topic","")

# ────────────────────────────────────────
# NAVBAR
# ────────────────────────────────────────
st.markdown(f"""
<div class="nav">
  <div class="nav-logo">
    <img src="data:image/png;base64,{LOGO}" style="width:34px;height:34px;border-radius:9px;">
    <span>BatteryIQ</span>
  </div>
  <div class="nav-links">
    <a href="?page=home">연구 개요</a>
    <a href="?page=tech">핵심 기술</a>
    <a href="?page=news">뉴스룸</a>
    <a href="?page=topics">24개 주제</a>
  </div>
  <div class="nav-right">
    <span>Gregory Plett · Ch 2-04</span>
    <div class="nav-sep"></div>
    <span>🔖 0건 &nbsp;📌 0편</span>
  </div>
</div>
<div style="height:68px;"></div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# HOME
# ════════════════════════════════════════
if page == "home":

    # HERO
    st.markdown(f"""
    <div class="hero-wrap">
      <img src="data:image/png;base64,{HERO}"
           style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;">
      <div class="hero-overlay"></div>
      <div class="hero-grid"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">Battery Management Systems · Chapter 2-04</div>
        <div class="hero-title">배터리<br><span class="hero-em">건강 추정</span><br>연구 포털</div>
        <div class="hero-sub">Battery State of Health(SOH) 추정은 전기차와 에너지 저장 시스템의<br>안전한 운용과 수명 예측을 위한 핵심 기술입니다.</div>
      </div>
      <div class="hero-scroll">SCROLL</div>
    </div>
    """, unsafe_allow_html=True)

    # WHY SECTION
    st.markdown("<div style='padding:80px 80px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">왜 배터리 건강 추정인가</div>', unsafe_allow_html=True)
    col_img, col_why = st.columns([1, 1.1], gap="large")
    with col_img:
        why_img = card_img((10,22,35),(5,12,22))
        st.markdown(f"""
        <div style="border-radius:6px;overflow:hidden;height:420px;position:relative;">
          <img src="data:image/png;base64,{why_img}"
               style="width:100%;height:100%;object-fit:cover;opacity:.7;">
          <div style="position:absolute;inset:0;
            background:linear-gradient(135deg,rgba(10,25,40,.6),rgba(5,15,25,.4));">
          </div>
          <div style="position:absolute;bottom:24px;left:24px;right:24px;">
            <div style="font-size:10px;letter-spacing:.18em;color:#2dd4bf;text-transform:uppercase;margin-bottom:6px;">
              Battery Lab · Gunsan University
            </div>
            <div style="width:48px;height:2px;background:rgba(45,212,191,.35);"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_why:
        st.markdown('<div class="t-lg">배터리 수명과 안전을<br>결정하는 핵심 기술</div>', unsafe_allow_html=True)
        for n, title, body in [
            ("01","안전성 확보","과충전·과방전을 실시간으로 방지하여 배터리 열폭주 등 위험 상황을 사전에 예방합니다."),
            ("02","수명 예측 (RUL)","잔여 유용 수명을 정확히 예측하여 배터리 교체 시점을 최적화하고 유지보수 비용을 절감합니다."),
            ("03","성능 최적화","실시간 SoH 데이터를 활용한 에너지 관리 전략으로 EV 주행거리와 충전 효율을 극대화합니다."),
        ]:
            st.markdown(f"""
            <div style="display:flex;gap:20px;margin-bottom:28px;">
              <div class="why-num">{n}</div>
              <div>
                <div class="why-title">{title}</div>
                <div class="why-body">{body}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # STATS BAR
    st.markdown("""
    <div class="stats-bar">
      <div><div class="stat-num">24</div><div class="stat-lbl">Research Topics</div></div>
      <div><div class="stat-num">5.37<span style="font-size:26px">mV</span></div><div class="stat-lbl">Model RMSE · UDDS</div></div>
      <div><div class="stat-num">99.9<span style="font-size:26px">%</span></div><div class="stat-lbl">Coulombic Efficiency</div></div>
      <div><div class="stat-num">10</div><div class="stat-lbl">Quiz Questions</div></div>
    </div>
    """, unsafe_allow_html=True)

    # TOPIC GRID (4 featured)
    st.markdown("""
    <div style="padding:72px 80px 0;background:#f8fafc;">
      <div style="display:grid;grid-template-columns:1fr 1.6fr;gap:60px;margin-bottom:48px;align-items:start;">
        <div>
          <div class="t-xl">배터리 건강 추정<br>핵심 기술</div>
        </div>
        <div style="font-size:14px;color:#64748b;line-height:1.75;padding-top:64px;">
          칼만 필터부터 EV 시뮬레이션까지 — 6가지 핵심 기술을 탐색하세요.<br>
          패널을 클릭하면 관련 뉴스와 논문을 바로 확인할 수 있습니다.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 2×2 topic cards
    feat = TOPICS[:4]
    c1h, c2h = st.columns(2, gap="small")
    for ci, tp in enumerate(feat):
        img_b = card_img(tp["c1"], tp["c2"])
        col = c1h if ci % 2 == 0 else c2h
        with col:
            btn_key = f"hbtn_{tp['id']}"
            clicked = st.button(f"자세히 보기 →", key=btn_key, use_container_width=True)
            if clicked:
                st.query_params["page"] = "topics"
                st.query_params["topic"] = tp["id"]
                st.rerun()
            st.markdown(f"""
            <div class="tc" style="margin-top:-44px;margin-bottom:4px;pointer-events:none;">
              <img class="tc-img" src="data:image/png;base64,{img_b}">
              <div class="tc-fade"></div>
              <div class="tc-body">
                <div class="tc-eye">{tp['num']}</div>
                <div class="tc-t">{tp['title']}</div>
                <div class="tc-sub">{tp['sub']}</div>
                <div class="tc-more">자세히 보기 →</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # NEWSROOM SECTION
    st.markdown("""
    <div style="padding:80px 80px 0;background:#fff;">
      <div class="eyebrow">최신 뉴스</div>
      <div class="t-xl" style="margin-bottom:48px;">뉴스룸</div>
    </div>
    """, unsafe_allow_html=True)

    nc = st.columns(4, gap="medium")
    for ni, news in enumerate(NEWS):
        nb = card_img(news["c1"], news["c2"])
        with nc[ni]:
            st.markdown(f"""
            <div style="cursor:pointer;">
              <div style="border-radius:5px;overflow:hidden;aspect-ratio:4/3;margin-bottom:14px;">
                <img src="data:image/png;base64,{nb}" style="width:100%;height:100%;object-fit:cover;opacity:.85;">
              </div>
              <div class="nc-date">{news['date']}</div>
              <div class="nc-title">{news['title']}</div>
              <div class="nc-src">{news['src']}</div>
            </div>
            """, unsafe_allow_html=True)

    # FOOTER
    st.markdown("""
    <div style="height:60px;"></div>
    <div class="ft">
      <div class="ft-logo">🔋 BatteryIQ</div>
      <div>
        <a href="?page=home" class="ft-links">연구 개요</a>
        <a href="?page=tech" class="ft-links">핵심 기술</a>
        <a href="?page=topics" class="ft-links">24개 주제</a>
      </div>
      <div class="ft-copy">© 2026 BatteryIQ · 군산대학교 기계공학부 · Gregory Plett Ch.2-04</div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════
# TOPICS
# ════════════════════════════════════════
elif page == "topics":

    if tid and tid in DETAIL:
        # ── DETAIL VIEW ──
        d = DETAIL[tid]
        tm = next((t for t in TOPICS if t["id"]==tid), TOPICS[0])

        st.markdown(f"""
        <div style="background:#0f172a;padding:64px 80px 44px;">
          <div style="font-size:11px;letter-spacing:.2em;color:#2dd4bf;margin-bottom:16px;">
            <a href="?page=topics" style="color:#2dd4bf;text-decoration:none;">← 전체 주제로</a>
          </div>
          <div style="font-size:10px;letter-spacing:.18em;color:#2dd4bf;text-transform:uppercase;margin-bottom:10px;">{tm['num']}</div>
          <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.0;margin-bottom:14px;">{d['title']}</div>
          <div style="display:flex;gap:8px;">
            {''.join([f'<span style="background:rgba(45,212,191,.15);color:#2dd4bf;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;">{t}</span>' for t in d['tags']])}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← 전체 주제로 돌아가기"):
            st.query_params["page"] = "topics"
            if "topic" in st.query_params:
                del st.query_params["topic"]
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📖 개념 설명", "🔢 핵심 수식", "📄 참고문헌"])

        with tab1:
            st.markdown("#### 🎯 핵심 포인트")
            kc = st.columns(2)
            for ki, kp in enumerate(d["kps"]):
                with kc[ki%2]:
                    st.markdown(f"""
                    <div class="kp-card">
                      <div class="kp-ico">{kp['i']}</div>
                      <div class="kp-t">{kp['t']}</div>
                      <div class="kp-d">{kp['d']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("#### 📝 상세 내용")
            st.markdown(d["body"])

        with tab2:
            for eq in d["eqs"]:
                st.markdown(f"**{eq['t']}**")
                st.markdown(f"""<div class="eq-box">{eq['c'].replace(chr(10),'<br>')}</div>""", unsafe_allow_html=True)
                st.caption(f"▶ {eq['d']}")
                st.markdown("")

        with tab3:
            for lb, txt, doi in d["refs"]:
                st.markdown(f"""
                <div style="background:#f8fafc;border:1px solid #e2e8f0;
                  border-left:3px solid #2dd4bf;border-radius:0 8px 8px 0;
                  padding:14px;margin-bottom:10px;">
                  <div style="font-size:10px;font-weight:700;color:#2dd4bf;margin-bottom:4px;">{lb}</div>
                  <div style="font-size:13px;color:#475569;line-height:1.7;">{txt}</div>
                  {"<a href='https://doi.org/"+doi+"' target='_blank' style='font-size:11px;color:#2dd4bf;font-family:monospace;'>DOI: "+doi+"</a>" if doi else ""}
                </div>
                """, unsafe_allow_html=True)

    else:
        # ── GRID VIEW ──
        st.markdown("""
        <div style="padding:56px 0 32px;">
          <div class="eyebrow">배터리 건강 추정</div>
          <div class="t-xl">24개 연구 주제</div>
          <div style="font-size:14px;color:#64748b;margin-bottom:36px;">Gregory Plett · Battery Management Systems · Chapter 2-04</div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2, gap="small")
        for i, tp in enumerate(TOPICS):
            img_b = card_img(tp["c1"], tp["c2"])
            with cols[i%2]:
                if st.button("자세히 보기", key=f"tpb_{tp['id']}", use_container_width=True):
                    st.query_params["page"] = "topics"
                    st.query_params["topic"] = tp["id"]
                    st.rerun()
                st.markdown(f"""
                <div class="tc" style="height:240px;margin-top:-44px;margin-bottom:4px;pointer-events:none;">
                  <img class="tc-img" src="data:image/png;base64,{img_b}">
                  <div class="tc-fade"></div>
                  <div class="tc-body">
                    <div class="tc-eye">{tp['num']}</div>
                    <div class="tc-t" style="font-size:20px;">{tp['title']}</div>
                    <div class="tc-sub">{tp['sub']}</div>
                    <div class="tc-more">자세히 보기 →</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════
# TECH (핵심 기술 + 인터랙티브 실습)
# ════════════════════════════════════════
elif page == "tech":

    st.markdown("""
    <div style="background:#0f172a;padding:64px 0 44px;">
      <div class="eyebrow" style="margin-left:0;">핵심 기술</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.0;margin-bottom:12px;">인터랙티브 실습</div>
      <div style="font-size:14px;color:rgba(255,255,255,.45);">슬라이더와 그래프로 배터리 모델을 직접 체험해보세요.</div>
    </div>
    """, unsafe_allow_html=True)

    tb1, tb2, tb3, tb4 = st.tabs(["🔋 SoC 시뮬레이터","📡 나이키스트 플롯","⚡ ESC 단계별","🧮 파라미터 계산기"])

    # SoC 시뮬레이터
    with tb1:
        st.markdown("### 🔋 SoC 실시간 시뮬레이터")
        cc1, cc2 = st.columns([1,1.6])
        with cc1:
            Iv   = st.slider("방전 전류 I (A)", 1.0, 50.0, 10.0, 0.5)
            z0v  = st.slider("초기 SoC (%)", 10, 100, 80, 1) / 100
            Qv   = st.slider("총 용량 Q (Ah)", 1.0, 100.0, 25.0, 1.0)
            R0v  = st.slider("R₀ (mΩ)", 1.0, 30.0, 8.2, 0.1) / 1000
            R1v  = st.slider("R₁ (mΩ)", 1.0, 30.0, 15.8, 0.1) / 1000
            C1v  = st.slider("C₁ (kF)", 1.0, 100.0, 38.0, 1.0) * 1000
        with cc2:
            tau_v = R1v * C1v
            ts = list(range(121))
            zs, vs, ocs = [], [], []
            z_cur, irc_cur = z0v, 0.0
            for tt in ts:
                z_cur = max(0.0, z_cur - (1/3600)*Iv/Qv)
                ov = ocv(z_cur)
                zs.append(z_cur); ocs.append(ov)
                if tt < 5: vs.append(ov); irc_cur=0.0
                else:
                    F = exp(-1/tau_v) if tau_v>0 else 0
                    irc_cur = F*irc_cur + (1-F)*Iv
                    vs.append(ov - R1v*irc_cur - R0v*Iv)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts,y=ocs,name="OCV",line=dict(color="#475569",width=1.5,dash="dot")))
            fig.add_trace(go.Scatter(x=ts,y=vs,name="V(t)",fill="tonexty",
                                     fillcolor="rgba(45,212,191,.08)",
                                     line=dict(color="#2dd4bf",width=2.5)))
            fig.update_layout(**dk(title=f"V(t) | I={Iv}A · τ={tau_v:.0f}s",
                                   xaxis_title="시간(s)",yaxis_title="전압(V)",height=300))
            st.plotly_chart(fig, use_container_width=True)
            cur_soc = int(zs[-1]*100); cur_v = vs[-1]
            ma,mb,mc = st.columns(3)
            ma.metric("최종 SoC", f"{cur_soc}%")
            mb.metric("단자 전압", f"{cur_v:.3f} V")
            mc.metric("시정수 τ", f"{tau_v:.0f} s")
            col_s = "#2dd4bf" if cur_soc>50 else "#f59e0b" if cur_soc>20 else "#ef4444"
            st.markdown(f"""
            <div style="background:#0f172a;border-radius:8px;padding:10px 14px;margin-top:6px;">
              <div style="font-size:11px;color:#475569;margin-bottom:5px;">SoC 잔량</div>
              <div style="background:#1e293b;border-radius:4px;height:22px;overflow:hidden;">
                <div style="background:{col_s};width:{cur_soc}%;height:100%;border-radius:4px;"></div>
              </div>
              <div style="text-align:center;font-size:13px;font-weight:700;color:{col_s};margin-top:3px;">{cur_soc}%</div>
            </div>
            """, unsafe_allow_html=True)

    # 나이키스트
    with tb2:
        st.markdown("### 📡 나이키스트 플롯 단계별 학습")
        nyq = {
            "① 고주파 (kHz) — 전해질 저항 R₀":
                {"d":"수백 kHz 이상에서 실수축과 교차하는 점이 R₀입니다.","e":"Z(ω→∞) = R₀ = 8.2 mΩ","r":(0,100),"c":"#ef4444"},
            "② 중주파 (Hz) — RC 분극 반원":
                {"d":"수 Hz ~ kHz 구간에서 반원 형태. 반원 지름 = R₁.","e":"Z_RC(ω) = R₁/(1+jω·R₁C₁)","r":(100,300),"c":"#f59e0b"},
            "③ 저주파 (mHz) — 와버그 확산 (45°)":
                {"d":"수십 mHz 이하에서 45° 직선. 고체 확산 와버그 임피던스.","e":"Z_W = A_W/√(jω) → 위상각=45°","r":(300,500),"c":"#2dd4bf"},
        }
        sel = st.radio("구간 선택", list(nyq.keys()), label_visibility="collapsed")
        sd = nyq[sel]
        cna, cnb = st.columns([1.5,1])
        with cna:
            omega = np.logspace(4,-4,500)
            R0n,R1n,C1n,Aw = 0.0082,0.0158,38000,0.002
            re_z,im_z = [],[]
            for w in omega:
                jw = complex(0,w)
                Z = R0n + R1n/(1+jw*R1n*C1n) + Aw/(complex(0,1)**0.5*w**0.5)
                re_z.append(Z.real*1000); im_z.append(-Z.imag*1000)
            rng = sd["r"]
            fnq = go.Figure()
            fnq.add_trace(go.Scatter(x=re_z,y=im_z,mode="lines",
                                     line=dict(color="rgba(71,85,105,.45)",width=1.5),name="전체"))
            fnq.add_trace(go.Scatter(x=re_z[rng[0]:rng[1]],y=im_z[rng[0]:rng[1]],mode="lines",
                                     line=dict(color=sd["c"],width=4.5),name="선택 구간"))
            fnq.update_layout(**dk(title="나이키스트 플롯 (EIS)",
                                   xaxis_title="Re(Z) mΩ",yaxis_title="-Im(Z) mΩ",height=300))
            st.plotly_chart(fnq, use_container_width=True)
        with cnb:
            st.markdown(f"**{sel}**")
            st.markdown(f"""
            <div style="background:#0f172a;border-left:3px solid {sd['c']};
              border-radius:0 8px 8px 0;padding:14px;margin:8px 0;font-size:13px;color:#94a3b8;">
              {sd['d']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""<div class="eq-box">{sd['e']}</div>""", unsafe_allow_html=True)

    # ESC 단계별
    with tb3:
        st.markdown("### ⚡ ESC 모델 단계별 구성")
        steps = [
            {"t":"Step 1: v = OCV(z)","d":"이상적 전압원만.","rmse":"~100 mV","R0":0,"R1":0,"C1":1e9,"c":"#ef4444"},
            {"t":"Step 2: + R₀","d":"직렬 저항 추가. 순간 강하 모델링.","rmse":"~50 mV","R0":0.0082,"R1":0,"C1":1e9,"c":"#f59e0b"},
            {"t":"Step 3: + RC 확산","d":"지수 감쇠 분극 전압 추가.","rmse":"~10 mV","R0":0.0082,"R1":0.0158,"C1":38000,"c":"#60a5fa"},
            {"t":"Step 4: ESC 완성 (+ 히스테리시스)","d":"모든 요소 통합. 최종 완성 모델.","rmse":"5.37 mV ✓","R0":0.0082,"R1":0.0158,"C1":38000,"c":"#2dd4bf"},
        ]
        sel_s = st.radio("단계 선택", [s["t"] for s in steps], label_visibility="collapsed")
        sd_s = next(s for s in steps if s["t"]==sel_s)
        ces1, ces2 = st.columns([1,1.5])
        with ces1:
            st.markdown(f"""
            <div style="background:#0f172a;border-left:3px solid {sd_s['c']};
              border-radius:0 10px 10px 0;padding:16px;margin-bottom:12px;">
              <div style="font-weight:700;color:{sd_s['c']};margin-bottom:6px;font-size:13px;">{sd_s['t']}</div>
              <div style="font-size:13px;color:#94a3b8;line-height:1.6;">{sd_s['d']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("예상 RMSE", sd_s["rmse"])
            for ico,nm in [("✅" if sd_s["R0"]>0 else "❌","R₀ 등가 직렬 저항"),
                           ("✅" if sd_s["R1"]>0 else "❌","RC 확산 전압"),
                           ("✅" if "완성" in sd_s["t"] else "❌","히스테리시스")]:
                st.markdown(f"{ico} {nm}")
        with ces2:
            te = list(range(81)); ie=0.0; Ie=5.0; ve=[]; oe=[]
            for tt in te:
                oe.append(4.1)
                if tt<5: ve.append(4.1); ie=0.0
                else:
                    if sd_s["C1"]>1e6: ie=Ie
                    else:
                        F=exp(-1/(sd_s["R1"]*sd_s["C1"]))
                        ie=F*ie+(1-F)*Ie
                    vt=4.1-sd_s["R1"]*ie-sd_s["R0"]*Ie
                    if "완성" in sd_s["t"]: vt+=0.015
                    ve.append(vt)
            fes=go.Figure()
            fes.add_trace(go.Scatter(x=te,y=oe,name="OCV",line=dict(color="#475569",dash="dot",width=1.5)))
            fes.add_trace(go.Scatter(x=te,y=ve,name="V(t)",fill="tonexty",
                                     fillcolor=sd_s["c"]+"22",
                                     line=dict(color=sd_s["c"],width=2.5)))
            fes.update_layout(**dk(title=f"{sd_s['rmse']} — I=5A",
                                   xaxis_title="시간(s)",yaxis_title="전압(V)",height=280))
            st.plotly_chart(fes, use_container_width=True)

    # 파라미터 계산기
    with tb4:
        st.markdown("### 🧮 파라미터 계산기")
        cp1, cp2 = st.columns(2)
        with cp1:
            st.markdown("#### RC 파라미터 계산")
            with st.form("pf2"):
                pa,pb = st.columns(2)
                with pa:
                    R1c = st.number_input("R₁ (mΩ)",0.1,1000.0,15.8,0.1)
                    R0c = st.number_input("R₀ (mΩ)",0.1,1000.0,8.2,0.1)
                with pb:
                    C1c = st.number_input("C₁ (F)",1.0,1e6,38000.0,100.0)
                    dic = st.number_input("Δi (A)",0.1,1000.0,5.0,0.5)
                sub2 = st.form_submit_button("🔢 계산", use_container_width=True)
            if sub2:
                tau_c = (R1c/1000)*C1c
                ma2,mb2 = st.columns(2)
                ma2.metric("시정수 τ", f"{tau_c:.1f} s")
                mb2.metric("4τ (98%)", f"{4*tau_c:.0f} s")
                ma2.metric("순간 강하 ΔV₀", f"{R0c*dic:.1f} mV")
                mb2.metric("정상상태 ΔV∞", f"{(R0c+R1c)*dic:.1f} mV")
                st.metric("속도계수 F₁", f"{exp(-1/tau_c):.6f}")
                st.markdown(f"""<div class="eq-box">τ = {R1c}mΩ × {C1c:.0f}F = {tau_c:.2f} s<br>F₁ = exp(-1/{tau_c:.2f}) = {exp(-1/tau_c):.6f}<br>ΔV₀ = {R0c}mΩ × {dic}A = {R0c*dic:.2f} mV</div>""", unsafe_allow_html=True)
        with cp2:
            st.markdown("#### 전압 응답 시뮬레이터")
            sI2=st.slider("I (A)",1.0,100.0,20.0,1.0,key="si2")
            sR02=st.slider("R₀ (mΩ)",1.0,50.0,8.2,0.1,key="sr02")
            sR12=st.slider("R₁ (mΩ)",1.0,50.0,15.8,0.1,key="sr12")
            sC12=st.slider("C₁ (kF)",1.0,100.0,38.0,1.0,key="sc12")
            ts2=list(range(81)); ir2=0.0
            R02s,R12s,C12s=sR02/1000,sR12/1000,sC12*1000
            vs2,os2=[],[]
            for tt in ts2:
                os2.append(4.1)
                if tt<5: vs2.append(4.1); ir2=0.0
                else:
                    F=exp(-1/(R12s*C12s))
                    ir2=F*ir2+(1-F)*sI2
                    vs2.append(4.1-R12s*ir2-R02s*sI2)
            fs2=go.Figure()
            fs2.add_trace(go.Scatter(x=ts2,y=os2,name="OCV",line=dict(color="#475569",dash="dot",width=1.5)))
            fs2.add_trace(go.Scatter(x=ts2,y=vs2,name="V(t)",fill="tonexty",
                                     fillcolor="rgba(45,212,191,.08)",line=dict(color="#2dd4bf",width=2.5)))
            fs2.update_layout(**dk(title=f"τ={R12s*C12s:.0f}s | I={sI2}A",
                                   xaxis_title="시간(s)",yaxis_title="전압(V)",height=250))
            st.plotly_chart(fs2, use_container_width=True)

    # QUIZ
    st.markdown("---")
    st.markdown("### 📝 이해도 퀴즈")
    QUIZ = [
        {"q":"배터리 SoH 80%의 의미는?","opts":["즉시 폐기","EV 배터리 교체 기준 도달","정상 사용 가능","충전 전류를 낮춰야 함"],"ans":1,"exp":"SoH=80%가 일반적인 EV 배터리 교체 기준입니다.","f":"SoH = Q_max(t)/Q_max(0) × 100% → 교체 기준: 80%"},
        {"q":"ZOH 이산화 속도계수 F₁의 의미는?","opts":["샘플링/시정수 비율","한 샘플 후 잔류 RC 전류 비율(0<F₁<1)","전류 이득","전압 분배 비율"],"ans":1,"exp":"F₁=exp(-Δt/R₁C₁)은 한 샘플 주기 후 RC 전류가 얼마나 남는지를 나타냅니다.","f":"F₁ = exp(−Δt/R₁C₁) | 0 < F₁ < 1"},
        {"q":"EKF에서 칼만 이득 K=0의 의미는?","opts":["측정값만 신뢰","모델만 신뢰 (측정값 무시)","균등하게 신뢰","필터 오류"],"ans":1,"exp":"K=0이면 혁신(Innovation)을 전혀 반영하지 않으므로 모델 예측만 사용합니다.","f":"x̂_new = x̂_pred + K·(y−ŷ) → K=0: 측정값 무시"},
        {"q":"교재 실험(Δi=5A) R₀의 값은?","opts":["5.0 mΩ","8.2 mΩ","15.8 mΩ","38 mΩ"],"ans":1,"exp":"|ΔV₀|=41mV, Δi=5A → R₀=41mV/5A=8.2mΩ.","f":"R₀ = |ΔV₀/Δi| = 41mV / 5A = 8.2 mΩ"},
        {"q":"히스테리시스와 RC 확산 전압의 차이는?","opts":["히스테리시스가 항상 더 크다","히스테리시스는 시간이 지나도 소멸하지 않고 SoC 변화에만 의존한다","RC가 측정하기 더 어렵다","히스테리시스는 NMC에서 더 크다"],"ans":1,"exp":"RC 확산은 시간이 지나 0으로 소멸하지만, 히스테리시스는 시간 무관·SoC 변화 시에만 변합니다.","f":"V_hys = M₀·s[k] + M·h[k]  (시간 t에 직접 의존 없음)"},
    ]

    if "q_idx" not in st.session_state:
        st.session_state.q_idx=0; st.session_state.q_sc=0
        st.session_state.q_ans=False; st.session_state.q_done=False

    if st.session_state.q_done:
        sc=st.session_state.q_sc; pct=int(sc/len(QUIZ)*100)
        st.markdown(f"""
        <div style="background:#0f172a;border-radius:12px;padding:32px;text-align:center;">
          <div style="font-size:48px;margin-bottom:12px;">🎉</div>
          <div style="font-size:44px;font-weight:900;color:#2dd4bf;font-family:monospace;">{sc} / {len(QUIZ)}</div>
          <div style="font-size:15px;color:#94a3b8;margin-top:8px;">
            {'🏆 완벽! 배터리 모델링 마스터!' if pct==100 else '👍 훌륭합니다!' if pct>=80 else '📚 조금 더 복습해보세요.'}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("다시 풀기 ↺", type="primary"):
            st.session_state.q_idx=0; st.session_state.q_sc=0
            st.session_state.q_ans=False; st.session_state.q_done=False; st.rerun()
    else:
        idx=st.session_state.q_idx; q=QUIZ[idx]
        st.progress(idx/len(QUIZ), text=f"문제 {idx+1}/{len(QUIZ)} | 점수: {st.session_state.q_sc}")
        st.markdown(f"#### Q{idx+1}. {q['q']}")
        if not st.session_state.q_ans:
            for i,opt in enumerate(q["opts"]):
                if st.button(f"{chr(65+i)}. {opt}", key=f"qb{idx}_{i}", use_container_width=True):
                    st.session_state.q_ans=True; st.session_state.q_sel=i
                    if i==q["ans"]: st.session_state.q_sc+=1
                    st.rerun()
        else:
            sel_q=st.session_state.q_sel
            for i,opt in enumerate(q["opts"]):
                lb=f"{chr(65+i)}. {opt}"
                if i==q["ans"]: st.success(f"✅ {lb}")
                elif i==sel_q: st.error(f"❌ {lb}")
                else: st.markdown(f"<div style='padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;color:#94a3b8;margin:3px 0;'>{lb}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#0f172a;border-left:3px solid #2dd4bf;border-radius:0 8px 8px 0;padding:14px;margin:10px 0;">
              <div style="font-size:13px;color:#94a3b8;">💡 {q['exp']}</div>
              <div class="eq-box" style="margin-top:8px;">{q['f']}</div>
            </div>
            """, unsafe_allow_html=True)
            c_n,c_s=st.columns(2)
            with c_n:
                if st.button("다음 →", type="primary", use_container_width=True):
                    st.session_state.q_idx+=1; st.session_state.q_ans=False
                    if st.session_state.q_idx>=len(QUIZ): st.session_state.q_done=True
                    st.rerun()
            with c_s:
                if idx<len(QUIZ)-1:
                    if st.button("건너뛰기", use_container_width=True):
                        st.session_state.q_idx+=1; st.session_state.q_ans=False; st.rerun()

# ════════════════════════════════════════
# NEWS PAGE
# ════════════════════════════════════════
elif page == "news":
    st.markdown("""
    <div style="padding:56px 0 32px;">
      <div class="eyebrow">최신 뉴스</div>
      <div class="t-xl">뉴스룸</div>
      <div style="font-size:14px;color:#64748b;">배터리·EV·에너지 저장 분야 최신 동향</div>
    </div>
    """, unsafe_allow_html=True)
    nc = st.columns(4, gap="medium")
    for ni,news in enumerate(NEWS):
        nb = card_img(news["c1"],news["c2"])
        with nc[ni]:
            st.markdown(f"""
            <div>
              <div style="border-radius:6px;overflow:hidden;aspect-ratio:4/3;margin-bottom:14px;">
                <img src="data:image/png;base64,{nb}" style="width:100%;height:100%;object-fit:cover;opacity:.85;">
              </div>
              <div class="nc-date">{news['date']}</div>
              <div class="nc-title">{news['title']}</div>
              <div class="nc-src">{news['src']}</div>
            </div>
            """, unsafe_allow_html=True)
