"""
ECM 등가회로 모델 연구포털 v4
Battery Management Systems · Chapter 02 · Plett (2015)
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import requests
import base64, io, math, re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter

st.set_page_config(
    page_title="ECM 연구포털 — 등가회로 모델",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _init():
    d = {
        "page":"home","dark":False,"lang":"ko",
        "bookmarks":[],"progress":{},"memo":"",
        "notices":[
            {"type":"공지","title":"ECM 연구포털 v4 오픈","body":"새 UI와 인터랙티브 실습이 추가되었습니다.","date":"2026-04-16"},
            {"type":"업데이트","title":"AI 그래프 탭 추가","body":"주제별 학습에서 Plotly 그래프를 클릭하면 바로 볼 수 있습니다.","date":"2026-04-15"},
            {"type":"Q&A","title":"ESC 모델 MATLAB 코드 위치","body":"mocha-java.uccs.edu/BMS1/ 에서 다운로드 가능합니다.","date":"2026-04-14"},
        ],
        "quiz_idx":0,"quiz_score":0,"quiz_answered":False,
        "quiz_done":False,"quiz_selected":-1,
        "selected_topic":None,
        "news_cache":None,"paper_cache":None,
    }
    for k,v in d.items():
        if k not in st.session_state:
            st.session_state[k]=v

_init()
S=st.session_state

BLUE="#60a5fa" if S.dark else "#1a5fa8"
NAVY="#93c5fd" if S.dark else "#0e3a6e"
BG="#0f172a" if S.dark else "#f8fafc"
CARD="#1e293b" if S.dark else "#ffffff"
TX="#e2e8f0" if S.dark else "#1e293b"
TX2="#94a3b8" if S.dark else "#475569"
BD="#334155" if S.dark else "#e2e8f0"

def _b64(img):
    buf=io.BytesIO(); img.save(buf,format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data
def make_hero():
    w,h=1200,380; img=Image.new("RGB",(w,h)); draw=ImageDraw.Draw(img)
    for y in range(h):
        t=y/h; r=int(14+t*8); g=int(58+t*22); b=int(110+t*28)
        draw.line([(0,y),(w,y)],fill=(r,g,b))
    for x in range(0,w,60): draw.line([(x,0),(x,h)],fill=(255,255,255,15))
    for y2 in range(0,h,60): draw.line([(0,y2),(w,y2)],fill=(255,255,255,15))
    for pts in [[(800,80),(950,80)],[(950,80),(950,180)],[(950,180),(1100,180)],
                [(780,220),(900,220)],[(900,220),(900,300)],[(900,300),(1050,300)]]:
        draw.line(pts,fill=(125,211,252,55),width=2)
    for cx,cy in [(950,80),(950,180),(900,220),(900,300)]:
        draw.ellipse([cx-5,cy-5,cx+5,cy+5],fill=(125,211,252,100))
    return _b64(img.filter(ImageFilter.GaussianBlur(1)))

@st.cache_data
def make_thumb(idx,c1,c2):
    w,h=400,180; img=Image.new("RGB",(w,h)); draw=ImageDraw.Draw(img)
    for y in range(h):
        t=y/h; r=int(c1[0]+t*(c2[0]-c1[0])); g=int(c1[1]+t*(c2[1]-c1[1])); b=int(c1[2]+t*(c2[2]-c1[2]))
        draw.line([(0,y),(w,y)],fill=(r,g,b))
    draw.rectangle([40,55,160,125],outline=(255,255,255,80),width=2)
    draw.line([(160,90),(220,90)],fill=(255,255,255,80),width=2)
    draw.line([(40,90),(0,90)],fill=(255,255,255,80),width=2)
    return _b64(img)

@st.cache_data
def make_logo():
    sz=40; img=Image.new("RGBA",(sz,sz),(0,0,0,0)); draw=ImageDraw.Draw(img)
    draw.rounded_rectangle([0,0,sz-1,sz-1],radius=9,fill=(26,95,168))
    draw.ellipse([14,14,26,26],outline="white",width=2)
    draw.line([(6,20),(14,20)],fill="white",width=2); draw.line([(26,20),(34,20)],fill="white",width=2)
    draw.line([(20,6),(20,14)],fill="white",width=2); draw.line([(20,26),(20,34)],fill="white",width=2)
    return _b64(img)

LOGO=make_logo(); HERO=make_hero()
TC=[((14,58,110),(8,145,178)),((30,80,60),(16,163,74)),((100,30,60),(220,38,38)),
    ((80,50,10),(217,119,6)),((50,20,80),(124,58,237)),((10,70,90),(8,145,178)),
    ((20,60,100),(37,99,235)),((60,20,100),(124,58,237)),((100,40,10),(234,88,12)),
    ((10,80,50),(16,163,74)),((80,10,50),(219,39,119)),((40,60,10),(101,163,13)),
    ((10,40,100),(59,130,246)),((60,60,10),(202,138,4))]

OCV_T=[3.0,3.35,3.55,3.65,3.72,3.78,3.85,3.92,4.0,4.1,4.2]
def get_ocv(z):
    z=max(0.0,min(1.0,z)); i=min(int(z*10),9); f=z*10-i
    return OCV_T[i]+f*(OCV_T[i+1]-OCV_T[i])

TOPICS=[
{"id":"t01","num":"01","title":"개방회로 전압 (OCV)","tags":["OCV","LUT","GITT"],"desc":"무부하 평형 전압. SoC 추정의 핵심 기준값.",
 "kps":[{"i":"⚡","t":"정의","d":"전류 i=0 상태의 단자 전압. 순수 전기화학적 평형 전압."},
        {"i":"📈","t":"SoC 의존성","d":"OCV(z,T)는 2차원 함수. NMC:S형. LFP:극도로 평탄."},
        {"i":"🔬","t":"측정","d":"C/30 저속 방전(60h+) 또는 GITT 기법으로 취득."},
        {"i":"🌡️","t":"온도 보정","d":"OCV(z,T)=OCV₀(z)+T·OCVrel(z). 행렬 최소제곱으로 결정."}],
 "body":"OCV는 배터리에 전류가 흐르지 않는 완전한 평형 상태에서의 단자 전압입니다. NMC(단조 S형)와 LFP(평탄) 배터리에서 형태가 크게 다릅니다.",
 "eqs":[{"t":"이상 전압원 모델","c":"v(t) = OCV(z(t))  // i=0 가정"},
        {"t":"온도 보정 모델","c":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)"}],
 "vars":[["z","SoC (0~1)"],["T","셀 온도 [°C]"],["OCV₀","0°C 기준 곡선 [V]"]],
 "comp":{"h":["항목","NMC","LFP"],"r":[["OCV 형태","단조 S곡선","극평탄(3.33V)"],["히스테리시스","<10mV","50~100mV"],["SoC 추정","보통","어려움"]]},
 "refs":[("Plett 2004 Part I","10.1016/j.jpowsour.2004.02.032")]},

{"id":"t02","num":"02","title":"충전 상태 의존성 (SoC)","tags":["SoC","쿨롱 효율","ZOH"],"desc":"잔존 전하량. 쿨롱 카운팅과 이산시간 점화식.",
 "kps":[{"i":"🔢","t":"정의","d":"z∈[0,1]. 완방전=0, 완충=1."},{"i":"⚗️","t":"쿨롱 효율","d":"리튬이온: 99~99.9%."},
        {"i":"💻","t":"이산화","d":"연속 ODE → Δt로 이산화. MCU 실시간 연산."},{"i":"📊","t":"정확도","d":"쿨롱 카운팅:±2~5%. EKF+ESC:±0.5~1.5%."}],
 "body":"SoC는 BMS에서 가장 중요한 상태 변수입니다. 쿨롱 카운팅만으로는 오차가 누적되므로 EKF와 결합한 ESC 모델로 자가 교정합니다.",
 "eqs":[{"t":"연속시간 상태방정식","c":"ż(t) = −η(t)·i(t) / Q"},
        {"t":"이산시간 점화식 (식 2.4)","c":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"}],
 "vars":[["z","SoC (0~1)"],["η","쿨롱 효율 (~1)"],["Q","총 용량 [Ah]"],["Δt","샘플링 주기 [s]"]],
 "comp":{"h":["방법","RMSE","누적"],"r":[["쿨롱 카운팅","±2~5%","있음"],["OCV 맵핑","±1~3%","없음"],["EKF+ESC","±0.5~1.5%","교정"]]},
 "refs":[("Zheng 2018","10.1016/j.jpowsour.2017.11.044")]},

{"id":"t03","num":"03","title":"등가 직렬 저항 (R₀)","tags":["ESR","R₀","온도"],"desc":"순간 전압 강하. 저온에서 3~5배 증가.",
 "kps":[{"i":"🔌","t":"구성","d":"전해질+집전체+SEI 저항. 순간 전압 강하 원인."},
        {"i":"❄️","t":"온도 의존","d":"0°C에서 25°C 대비 3~5배. 겨울철 EV 출력 저하 주원인."},
        {"i":"📐","t":"측정","d":"R₀=|ΔV₀/Δi|. 교재: 41mV÷5A=8.2mΩ."},
        {"i":"📉","t":"노화","d":"노화 시 R₀ 증가 → SoH 지표로 활용."}],
 "body":"R₀는 전류 인가/차단 직후 즉각적으로 나타나는 전압 강하의 원인입니다. 아레니우스 법칙에 따라 온도가 내려가면 지수함수적으로 증가합니다.",
 "eqs":[{"t":"단자 전압","c":"v(t) = OCV(z(t)) − i(t)·R₀"},
        {"t":"R₀ 추출","c":"R₀ = |ΔV₀/Δi|  // 교재: 8.2 mΩ"}],
 "vars":[["R₀","등가 직렬 저항 [Ω]"],["ΔV₀","순간 전압 강하 [V]"],["Δi","전류 변화 [A]"]],
 "comp":{"h":["온도","R₀ 배수","현상"],"r":[["−30°C","~5배","시동 불가"],["0°C","~3배","주행거리 급감"],["25°C","기준","정상"],["45°C","~0.8배","성능 향상"]]},
 "refs":[("Hu 2012","10.1016/j.jpowsour.2011.10.013")]},

{"id":"t04","num":"04","title":"확산 전압 (RC 회로)","tags":["RC","ZOH","시정수"],"desc":"리튬 이온 농도 구배에 의한 느린 동적 전압.",
 "kps":[{"i":"🌊","t":"물리적 원인","d":"전극 내 리튬 이온 농도 구배. 분 단위의 느린 시간 상수."},
        {"i":"💡","t":"손전등 비유","d":"방전된 손전등을 끄면 2분 후 다시 켜짐 → 확산 전압 해소."},
        {"i":"⚙️","t":"RC 모델링","d":"R₁-C₁ 병렬 서브회로. τ=R₁C₁. 교재:≈600s(10분)."},
        {"i":"💻","t":"ZOH 이산화","d":"F₁=exp(-Δt/τ). 정확한 이산화."}],
 "body":"확산 전압은 R₀의 즉각적 강하와 달리 지수함수적으로 서서히 변합니다. ZOH 이산화는 샘플링 구간 내 입력 일정 가정으로 연속 ODE를 정확히 이산화합니다.",
 "eqs":[{"t":"연속시간 ODE","c":"d(i_R1)/dt = −(1/R₁C₁)·i_R1 + (1/R₁C₁)·i"},
        {"t":"ZOH 이산화 (식 2.8)","c":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)"},
        {"t":"단자 전압","c":"v[k] = OCV(z[k]) − R₁·i_R1[k] − R₀·i[k]"}],
 "vars":[["i_R1","RC 저항 전류 [A]"],["F₁","속도계수 exp(−Δt/τ)"],["R₁","분극 저항 (15.8mΩ)"],["C₁","분극 커패시턴스 (38kF)"],["τ","시정수 R₁C₁ (≈600s)"]],
 "comp":{"h":["모델","RC쌍","RMSE"],"r":[["1RC(ESC)","1","5~15mV"],["2RC","2","3~8mV"],["FO-ECM","분수차","2~5mV"],["DFN","없음","<2mV"]]},
 "refs":[("Seaman 2014","10.1016/j.jpowsour.2013.11.037")]},

{"id":"t05","num":"05","title":"대략적인 파라미터 값","tags":["HPPC","펄스","추출"],"desc":"R₀=8.2mΩ, R₁=15.8mΩ, C₁≈38kF — 펄스 응답 추출.",
 "kps":[{"i":"⚡","t":"R₀ 추출","d":"순간 강하. R₀=|ΔV₀/Δi|=8.2mΩ"},{"i":"📈","t":"R₁ 추출","d":"정상상태 강하. R₁=|ΔV∞/Δi|−R₀=15.8mΩ"},
        {"i":"⏱️","t":"C₁ 추출","d":"시간 상수 역산. C₁≈38kF, τ≈600s"},{"i":"🔄","t":"반복 정제","d":"최소제곱법으로 파라미터 최적화."}],
 "body":"파라미터 추출은 3단계: (1)순간 강하로 R₀, (2)정상상태로 R₁, (3)시간 상수로 C₁. 교재 실험: Δi=5A 펄스.",
 "eqs":[{"t":"파라미터 추출","c":"R₀=|ΔV₀/Δi|=8.2mΩ\nR₁=|ΔV∞/Δi|−R₀=15.8mΩ\nτ=R₁×C₁≈600s  →  C₁≈38kF"}],
 "vars":[["ΔV₀","순간 강하 [V]"],["ΔV∞","정상상태 강하 [V]"],["Δt_rec","98% 회복 시간≈4τ"]],
 "comp":{"h":["파라미터","값","온도 의존"],"r":[["R₀","8.2mΩ","강함"],["R₁","15.8mΩ","있음"],["C₁","38kF","있음"],["τ","600s","있음"]]},
 "refs":[("He 2011","10.3390/en4040582")]},

{"id":"t06","num":"06","title":"와버그 임피던스","tags":["EIS","나이키스트","45°"],"desc":"고체 확산의 주파수 표현. 나이키스트 45° 직선.",
 "kps":[{"i":"📡","t":"EIS","d":"주파수를 바꿔가며 교류 전압 인가→전류 응답→임피던스 측정."},
        {"i":"📐","t":"45° 특성","d":"Z_W=A_W/√(jω). 실수부=허수부→위상각 45°."},
        {"i":"🔬","t":"나이키스트","d":"고주파:R₀. 중주파:RC 반원. 저주파:45° 직선."},
        {"i":"⚡","t":"랜들스 회로","d":"Rₛ+(Cdl//(Rct+Z_W))—표준 전기화학 등가회로."}],
 "body":"저주파 영역의 45° 직선이 와버그 임피던스입니다. Z_W=A_W/√(jω)에서 실수부=허수부이므로 위상각=45°. 고체 전극 내 리튬 이온의 고체상 확산을 나타냅니다.",
 "eqs":[{"t":"와버그 임피던스","c":"Z_W(jω) = A_W / √(jω)\n위상각 = 45°"}],
 "vars":[["Z_W","와버그 임피던스 [Ω]"],["A_W","와버그 계수 [Ω/√s]"],["ω","각주파수 [rad/s]"]],
 "comp":{"h":["주파수","위치","현상"],"r":[["고주파(kHz)","실수축 교점","전해질 저항 R₀"],["중주파(Hz)","반원","RC 분극"],["저주파(mHz)","45° 직선","와버그 확산"]]},
 "refs":[("Randles 1947","10.1039/df9470100011")]},

{"id":"t07","num":"07","title":"히스테리시스 전압","tags":["히스테리시스","LFP","이력"],"desc":"충전/방전 경로에 따라 OCV가 달라지는 이력 현상.",
 "kps":[{"i":"🔄","t":"정의","d":"같은 SoC에서 충전/방전 후 OCV가 다름. 시간 무관, SoC 변화에만 의존."},
        {"i":"🔋","t":"LFP에서 큼","d":"LFP:50~100mV. NMC:<10mV."},
        {"i":"📐","t":"두 종류","d":"① 동적 h[k]: SoC 변화에 따라 지수 감쇠. ② 순간 s[k]: 전류 방향에 즉각 반응."},
        {"i":"⏱️","t":"RC와 차이","d":"RC는 시간이 지나면 소멸. 히스테리시스는 SoC 변화 없으면 유지."}],
 "body":"히스테리시스는 배터리의 상변환(Phase Transition) 특성에서 기인합니다. ESC 모델은 동적+순간 히스테리시스를 분리 모델링합니다.",
 "eqs":[{"t":"동적 히스테리시스","c":"h[k+1] = exp(−|η·i·γ·Δt/Q|)·h[k]\n        − (1−exp(···))·sgn(i[k])\nγ ≈ 90"},
        {"t":"히스테리시스 전압","c":"V_hys[k] = M₀·s[k] + M·h[k]"}],
 "vars":[["γ","감쇠 상수(≈90)"],["M","동적 크기"],["M₀","순간 크기"],["h[k]","상태(−1~1)"],["s[k]","부호(±1)"]],
 "comp":{"h":["특성","히스테리시스","RC 확산"],"r":[["시간 의존","없음","있음(소멸)"],["LFP 크기","50~100mV","수십mV"],["NMC 크기","<10mV","수십mV"]]},
 "refs":[("Dreyer 2010","10.1038/nmat2718")]},

{"id":"t08","num":"08","title":"향상된 자가 교정 셀 모델 (ESC)","tags":["ESC","상태공간","EKF"],"desc":"모든 요소를 통합한 최종 완성형 배터리 모델.",
 "kps":[{"i":"🎯","t":"통합 구조","d":"상태벡터 x=[z,i_R,h]ᵀ. SoC·RC전류·히스테리시스 통합."},
        {"i":"🔄","t":"자가 교정","d":"i=0 휴지 시 RC→0. 전압이 OCV+히스테리시스로 자동 수렴."},
        {"i":"📊","t":"검증 성능","d":"25Ah NMC, UDDS 10h: RMSE=5.37mV ✓"},
        {"i":"🤖","t":"EKF 결합","d":"ESC+EKF → 실시간 SoC 자가 교정 추정."}],
 "body":"ESC는 2장의 모든 내용을 통합합니다. '자가 교정'은 셀이 쉴 때(i=0) RC가 0으로 수렴해 모델 전압이 자동으로 평형값으로 돌아오는 특성입니다.",
 "eqs":[{"t":"ESC 상태방정식","c":"x[k+1] = A[k]·x[k] + B[k]·u[k]\n// x=[z,i_R,h]ᵀ, A=diag(1,F₁,A_H)"},
        {"t":"ESC 출력방정식","c":"v[k] = OCV(z[k],T[k]) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]"}],
 "vars":[["x","상태벡터 [z,i_R,h]ᵀ"],["A_RC","exp(−Δt/R₁C₁)"],["A_H","exp(−|η·i·γ·Δt/Q|)"],["RMSE","5.37mV (교재)"]],
 "comp":{"h":["모델","RMSE","특징"],"r":[["OCV만","~100mV","최단순"],["+R₀","~50mV","순간강하"],["1RC ESC","~10mV","실용적"],["2RC ESC","~5mV","고정확"],["DFN+ML","<2mV","최고"]]},
 "refs":[("Plett 2004 II","10.1016/j.jpowsour.2004.02.033")]},

{"id":"t09","num":"09","title":"셀 데이터 수집 실험실 장비","tags":["Arbin","환경챔버","장비"],"desc":"Arbin BT2043 12채널 + 환경 챔버 −45°C~190°C.",
 "kps":[{"i":"🔬","t":"Arbin BT2043","d":"12채널 독립 테스트. 켈빈 4선식. ±20A/0~5V."},
        {"i":"🌡️","t":"환경 챔버","d":"−45°C~190°C 정밀 제어. 모든 테스트는 챔버 내 수행."},
        {"i":"📊","t":"데이터 수집","d":"전압·전류·온도·시간 동기 기록."},
        {"i":"🔋","t":"셀 준비","d":"25Ah NMC 파우치 셀. 초기 용량 측정 후 실험 시작."}],
 "body":"배터리 파라미터가 온도에 아레니우스 방정식에 따라 지수함수적으로 의존하므로 모든 테스트는 정밀 제어된 환경 챔버 내에서 진행합니다.",
 "eqs":[{"t":"아레니우스 의존성","c":"R(T) ∝ exp(Ea / (k_B·T))"}],
 "vars":[["Arbin","12ch, ±20A, 0~5V"],["챔버","−45°C~190°C, 8ft³"]],
 "comp":{"h":["장비","사양","용도"],"r":[["Arbin BT2043","12ch독립,±20A","충방전"],["환경 챔버","−45~190°C","온도 제어"]]},
 "refs":[("Plett 2015 pp.65-67","")]},

{"id":"t10","num":"10","title":"OCV 관계 실험실 테스트","tags":["4-스크립트","C/30","GITT"],"desc":"4개 스크립트로 OCV(z,T) 룩업 테이블 완성.",
 "kps":[{"i":"1️⃣","t":"Script 1","d":"테스트 온도 T에서 C/30으로 v_min까지 방전."},
        {"i":"2️⃣","t":"Script 2","d":"25°C에서 C/30으로 SoC=0% 기준점 확인."},
        {"i":"3️⃣","t":"Script 3","d":"테스트 온도 T에서 C/30으로 v_max까지 충전."},
        {"i":"4️⃣","t":"Script 4","d":"25°C에서 SoC=100% 기준점 확인."}],
 "body":"C/30 극저속 전류에서는 R₀·i≈0이므로 측정 전압이 실제 OCV에 매우 근접합니다.",
 "eqs":[{"t":"온도 보정 OCV","c":"[OCV₀; OCVrel] = [1,T₁;1,T₂;…]⁺ · OCV_meas"}],
 "vars":[["OCV₀","0°C 기준 OCV 곡선"],["OCVrel","°C당 OCV 변화율"]],
 "comp":{"h":["절차","온도","목적"],"r":[["Script 1","테스트 T","방전 OCV"],["Script 2","25°C","기준점 확인"],["Script 3","테스트 T","충전 OCV"],["Script 4","25°C","기준점 확인"]]},
 "refs":[("Weppner 1977","10.1149/1.2133152")]},

{"id":"t11","num":"11","title":"동적 관계 실험실 테스트","tags":["UDDS","시스템식별","γ"],"desc":"UDDS 프로파일로 RC·히스테리시스 γ 파라미터 추출.",
 "kps":[{"i":"🚗","t":"UDDS 프로파일","d":"도심 주행 패턴 모사 전류 프로파일."},
        {"i":"🔍","t":"γ 최적화","d":"γ=1~250 탐색 → RMSE 최소점 선택. 교재 최적: γ≈90."},
        {"i":"📊","t":"부분공간 식별","d":"OCV 제거 후 잔류 전압으로 시스템 식별."},
        {"i":"🔄","t":"3-스크립트","d":"Script 1:OCV참조. Script 2:방전. Script 3:충전."}],
 "body":"동적 테스트는 실제 주행 패턴과 유사한 전류 프로파일로 동적 파라미터를 추출합니다. γ≈90에서 RMSE가 최소입니다.",
 "eqs":[{"t":"잔류 전압 (OCV 제거)","c":"ṽ[k] = v[k] − OCV(z[k],T[k])"}],
 "vars":[["ṽ","OCV 제거 잔류 전압"],["γ","히스테리시스 감쇠(≈90)"]],
 "comp":{"h":["절차","내용"],"r":[["Script 1","완충 후 OCV 측정"],["Script 2","UDDS 방전"],["Script 3","UDDS 충전"]]},
 "refs":[("Seaman 2014","10.1016/j.jpowsour.2013.11.037")]},

{"id":"t12","num":"12","title":"모델링 결과 예시","tags":["RMSE","UDDS","NMC"],"desc":"25Ah NMC UDDS 10시간 검증 — RMSE 5.37mV.",
 "kps":[{"i":"✅","t":"RMSE 5.37mV","d":"25Ah NMC, UDDS 10h. 교재 목표 충족."},
        {"i":"🌡️","t":"온도별","d":"R₀: 기하급수적 감소. RC 시정수: 비단조적 증가."},
        {"i":"📉","t":"히스테리시스","d":"온도 증가 시 히스테리시스 크기 감소."},
        {"i":"⚠️","t":"비단조 시정수","d":"τ가 온도 증가에 따라 비단조적으로 증가 — 예상 밖."}],
 "body":"최종 검증에서 RMSE 5.37mV를 달성했습니다. RC 시정수의 비단조적 증가는 전해질 점도·이온 이동도·전극 구조의 복잡한 상호작용 때문으로 분석됩니다.",
 "eqs":[{"t":"RMSE 정의","c":"RMSE = √(1/N·Σ(v_meas[k]−v_model[k])²)\n// 교재: 5.37mV (25Ah NMC, UDDS 10h)"}],
 "vars":[["RMSE","평균 제곱근 오차 [V]"],["UDDS","도심 주행 사이클"]],
 "comp":{"h":["모델","RMSE","SoC 오차"],"r":[["OCV만","~100mV","±10%"],["ESR","~50mV","±5%"],["1RC ESC","~10mV","±1~2%"],["DFN+ML","<2mV","±0.3%"]]},
 "refs":[("Lee 2014","10.1016/j.jpowsour.2013.12.127")]},

{"id":"t13","num":"13","title":"결론 및 향후 방향","tags":["한계","DFN","ML"],"desc":"ESC 한계와 물리 기반·ML 하이브리드 차세대 방향.",
 "kps":[{"i":"⚠️","t":"ESC 한계","d":"노화 예측 불가. 덴드라이트 예측 불가. 화학적 현상 해석 불가."},
        {"i":"🔬","t":"물리 기반 DFN","d":"Doyle-Fuller-Newman. 전극 내부 물리 현상 기술. 높은 계산 비용."},
        {"i":"🤖","t":"ML 하이브리드","d":"ECM+LSTM. 목표 RMSE≤2mV."},
        {"i":"🔋","t":"차세대 BMS","d":"SoH 추정, 최적 충전, 덴드라이트 조기 감지."}],
 "body":"ESC는 단기 전압-전류 예측에 탁월하지만 노화 예측·덴드라이트 임계점 예측은 불가능합니다. 차세대는 DFN+ML 하이브리드로 목표 RMSE≤2mV를 목표로 합니다.",
 "eqs":[{"t":"하이브리드 목표","c":"v = f_ECM(x_k) + f_LSTM(h_k,i_k)\n목표: RMSE≤2mV, SoC±0.3%"}],
 "vars":[["DFN","Doyle-Fuller-Newman 모델"],["SoH","State of Health"],["RUL","Remaining Useful Life"]],
 "comp":{"h":["모델","RMSE","노화 예측","계산 비용"],"r":[["ESC","~10mV","불가","낮음"],["DFN","~3mV","가능","매우 높음"],["ECM+ML","~2mV","부분","높음"]]},
 "refs":[("Ng 2020","10.1038/s42256-020-0156-x")]},

{"id":"t14","num":"14","title":"MATLAB ESC 모델 툴박스","tags":["simCell","processOCV","MATLAB"],"desc":"simCell.m, processOCV.m — ESCtoolbox 핵심 함수.",
 "kps":[{"i":"💻","t":"simCell.m","d":"ESC 시뮬레이션. 전류 프로파일 → 모델 전압 출력."},
        {"i":"📊","t":"processOCV.m","d":"OCV 실험 데이터 처리. OCV₀, OCVrel 계산."},
        {"i":"🔧","t":"processDynamic.m","d":"동적 데이터 처리. R₀,R₁,C₁,γ,M,M₀ 추출."},
        {"i":"📁","t":"model 구조체","d":"모든 파라미터를 MATLAB struct로 저장."}],
 "body":"ESCtoolbox는 mocha-java.uccs.edu/BMS1/에서 무료 다운로드. MATLAB R2010a 이상에서 작동합니다.",
 "eqs":[{"t":"simCell 사용 예시","c":"vest=simCell(current,25,dt,model,1,[0;0],0);\n// model.R0Param, RCParam, GParam..."}],
 "vars":[["simCell","ESC 시뮬레이션 함수"],["processOCV","OCV 처리"],["processDynamic","동적 처리"],["model","파라미터 구조체"]],
 "comp":{"h":["함수","입력","출력"],"r":[["processOCV","OCV 데이터","OCV₀,OCVrel"],["processDynamic","동적 데이터","R₀,R₁,C₁,γ,M,M₀"],["simCell","전류+model","전압 시뮬레이션"]]},
 "refs":[("Plett 2015 pp.82-87","")]},
]

EQUATIONS=[
{"num":"식 2.1","cls":"blue","title":"SoC 연속시간","code":"ż(t) = −η(t)·i(t) / Q","desc":"충전 상태 시간 변화율.",
 "vars":[["ż","SoC 도함수"],["η","쿨롱 효율(~1)"],["Q","용량 [Ah]"]]},
{"num":"식 2.4","cls":"teal","title":"SoC 이산시간","code":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]","desc":"MCU 구현용 점화식.",
 "vars":[["z[k]","k번째 SoC"],["Δt","샘플링 주기"]]},
{"num":"식 2.8","cls":"green","title":"RC 이산화 (ZOH)","code":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)","desc":"분극 전압의 정확한 이산화.",
 "vars":[["i_R1","RC 저항 전류"],["F₁","속도계수"]]},
{"num":"ESC 출력","cls":"amber","title":"ESC 단자 전압","code":"v[k] = OCV(z,T) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]","desc":"최종 완성형 ESC 출력.",
 "vars":[["OCV","개방회로 전압"],["M₀·s","순간 히스테리시스"],["M·h","동적 히스테리시스"]]},
{"num":"히스테리시스","cls":"purple","title":"동적 히스테리시스","code":"h[k+1] = exp(−|η·i·γ·Δt/Q|)·h[k]\n       − (1−exp(···))·sgn(i[k])","desc":"SoC 변화에 따라 지수 감쇠. γ≈90.",
 "vars":[["γ","감쇠 상수(≈90)"],["h","상태(−1~1)"]]},
{"num":"OCV 온도","cls":"red","title":"OCV 온도 보정","code":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)","desc":"0°C 기준 + 온도 계수 선형 보정.",
 "vars":[["OCV₀","0°C 기준 곡선"],["OCVrel","°C당 변화율"]]},
]

QUIZ_Q=[
{"q":"OCV를 측정할 때 전류를 0에 가깝게 유지해야 하는 이유는?","opts":["배터리 폭발 위험","R₀·i 강하와 RC 분극 없이 순수 평형 전압 측정","온도 측정 정확도","쿨롱 효율 향상"],"ans":1,"exp":"OCV는 순수 평형 전압입니다. 전류가 흐르면 R₀·i 강하와 RC 분극이 추가됩니다.","f":"v=OCV(z)+ε | i→0이면 ε→0"},
{"q":"이산시간 SoC 점화식에서 쿨롱 효율(η)의 일반적인 값은?","opts":["~70~80%","~85~90%","~95~98%","~99~99.9%"],"ans":3,"exp":"리튬이온 배터리의 쿨롱 효율은 99~99.9%로 매우 높습니다.","f":"z[k+1]=z[k]−(Δt/Q)·η·i[k] | η≈0.999~1"},
{"q":"R₀를 펄스 응답으로 추출하는 공식은?","opts":["R₀=ΔV∞/Δi (정상상태)","R₀=|ΔV₀/Δi| (순간 강하)","R₀=τ/(R₁C₁)","R₀=−ln(F₁)·Δt"],"ans":1,"exp":"커패시터는 순간 변하지 않으므로 순간 강하는 순수 R₀에 의한 것입니다.","f":"R₀=|ΔV₀/Δi| (예: 41mV÷5A=8.2mΩ)"},
{"q":"ZOH 속도계수 F₁의 물리적 의미는?","opts":["샘플링/시정수 비율","한 샘플 후 잔류 RC 전류 비율(0<F₁<1)","전류 이득","전압 분배 비율"],"ans":1,"exp":"F₁=exp(-Δt/τ)는 한 샘플 주기 후 RC 전류가 얼마나 남는지를 나타냅니다.","f":"i_R1[k+1]=F₁·i_R1[k]+(1−F₁)·i[k]"},
{"q":"히스테리시스와 RC 확산 전압의 핵심 차이는?","opts":["히스테리시스가 항상 더 크다","히스테리시스는 시간이 지나도 소멸하지 않고 SoC 변화에만 의존","RC가 측정 더 어렵다","히스테리시스는 NMC에서 더 크다"],"ans":1,"exp":"RC 확산은 시간이 지나 소멸. 히스테리시스는 SoC 변화 시에만 변합니다.","f":"V_hys=M₀·s[k]+M·h[k] (시간 t에 직접 의존 없음)"},
{"q":"교재 실험(Δi=5A)에서 RC 시정수 τ는?","opts":["~60s (1분)","~600s (10분)","~2400s (40분)","~6000s (100분)"],"ans":1,"exp":"R₁=15.8mΩ, C₁=38kF → τ=0.0158×38000≈600s (약 10분).","f":"τ=R₁×C₁=15.8e-3×38000≈600s | 4τ≈2400s"},
{"q":"ESC를 '자가 교정'이라 부르는 이유는?","opts":["파라미터가 자동 업데이트","i=0 휴지 시 전압이 OCV+히스테리시스로 자동 수렴","오류 시 재시작","온도 자동 대응"],"ans":1,"exp":"셀이 쉴 때 RC가 0으로 수렴해 모델 전압이 자동으로 평형값으로 돌아옵니다.","f":"i→0: v[k]→OCV(z,T)+M₀·s+M·h"},
{"q":"와버그 임피던스가 나이키스트에서 45°인 이유는?","opts":["전극 저항이 주파수 무관","Z_W=A_W/√(jω)에서 실수부=허수부","커패시턴스가 매우 큼","전해질 저항=0"],"ans":1,"exp":"Z_W=A_W/√(jω) → Re=Im → 위상각=45°.","f":"Z_W=A_W/√(jω) | |Z_re|=|Z_im| | 위상=45°"},
{"q":"OCV 4-스크립트에서 Script 2·4를 25°C에서 수행하는 이유는?","opts":["장비 안전","잔류 용량을 뽑아 SoC 기준점(0%/100%) 정확히 설정","25°C에서만 측정 가능","챔버 에너지 절약"],"ans":1,"exp":"저/고온에서 전압 컷오프와 실제 완방전/완충이 다를 수 있어 25°C에서 확인합니다.","f":"Script1→Script2(25°C확인)→Script3→Script4(25°C확인)"},
{"q":"ESC 모델의 근본적 한계는?","opts":["연산량 과다","현상론적 블랙박스로 노화·덴드라이트 화학적 현상 예측 불가","OCV 측정 불가","RC 추출 불가"],"ans":1,"exp":"ESC는 현상론적 모델로 단기 예측에는 탁월하나 SEI 성장·장기 노화 예측은 불가합니다.","f":"차세대: ECM+DFN+LSTM 하이브리드 → 목표 RMSE≤2mV"},
]

SEARCH_DB=[
{"t":"eq","k":"OCV SoC 개방회로","title":"개방회로 전압 OCV","d":"v=OCV(z,T)","tid":"t01"},
{"t":"eq","k":"SoC 쿨롱 충전상태","title":"SoC 이산시간 점화식","d":"z[k+1]=z[k]−(Δt/Q)·η·i","tid":"t02"},
{"t":"eq","k":"R₀ ESR 직렬저항","title":"등가 직렬 저항","d":"R₀=|ΔV₀/Δi|=8.2mΩ","tid":"t03"},
{"t":"eq","k":"RC 확산 ZOH","title":"RC 이산화 (ZOH)","d":"i_R1[k+1]=F₁·i_R1[k]+(1−F₁)·i","tid":"t04"},
{"t":"eq","k":"히스테리시스 LFP","title":"히스테리시스 전압","d":"V_hys=M₀·s+M·h","tid":"t07"},
{"t":"eq","k":"ESC 완성 칼만","title":"ESC 출력 방정식","d":"v=OCV+M₀s+Mh−R₁i_R−R₀i","tid":"t08"},
{"t":"eq","k":"와버그 EIS","title":"와버그 임피던스","d":"Z_W=A_W/√(jω)","tid":"t06"},
{"t":"concept","k":"파라미터 추출 HPPC","title":"파라미터 추출","d":"R₀=8.2mΩ, R₁=15.8mΩ, C₁=38kF","tid":"t05"},
{"t":"concept","k":"MATLAB simCell","title":"MATLAB 툴박스","d":"simCell,processOCV,processDynamic","tid":"t14"},
{"t":"concept","k":"쿨롱 효율 η","title":"쿨롱 효율","d":"방전/충전 비율=99~99.9%","tid":"t02"},
{"t":"concept","k":"시정수 τ RC","title":"RC 시정수","d":"τ=R₁C₁=600s, 4τ=2400s(98%)","tid":"t04"},
{"t":"concept","k":"UDDS 검증 결과","title":"UDDS 검증","d":"25Ah NMC UDDS 10h RMSE=5.37mV","tid":"t12"},
]

# ── CSS ──
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Roboto+Mono:wght@400;500&display=swap');
html,body,[class*="css"],.stApp{{font-family:'Noto Sans KR',sans-serif!important;background:{BG}!important;color:{TX}!important;}}
#MainMenu,footer,.stDeployButton,[data-testid="stToolbar"],[data-testid="stHeader"]{{display:none!important;}}
.hero-wrap{{position:relative;overflow:hidden;border-radius:12px;margin-bottom:20px;}}
.hero-ov{{position:absolute;inset:0;background:linear-gradient(135deg,rgba(14,58,110,.92) 0%,rgba(26,95,168,.82) 55%,rgba(8,145,178,.72) 100%);}}
.hero-grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.04)1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04)1px,transparent 1px);background-size:60px 60px;}}
.hero-body{{position:absolute;inset:0;z-index:3;display:flex;flex-direction:column;justify-content:center;padding:40px;}}
.hero-badge{{display:inline-flex;align-items:center;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:3px 12px;font-size:11px;color:rgba(255,255,255,.9);font-weight:600;margin-bottom:14px;}}
.hero-title{{font-size:clamp(22px,3.5vw,40px);font-weight:900;color:#fff;line-height:1.2;margin-bottom:8px;}}
.hero-title em{{color:#7dd3fc;font-style:normal;}}
.hero-sub{{font-size:14px;color:rgba(255,255,255,.78);line-height:1.8;max-width:520px;margin-bottom:20px;}}
.hero-stat{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);border-radius:10px;padding:12px 16px;text-align:center;}}
.hero-stat-num{{font-size:24px;font-weight:700;color:#fff;font-family:'Roboto Mono',monospace;}}
.hero-stat-lbl{{font-size:10px;color:rgba(255,255,255,.65);margin-top:2px;}}
.sh{{display:flex;align-items:center;gap:8px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid {BD};}}
.sh-bar{{width:4px;height:20px;background:{BLUE};border-radius:2px;}}
.sh-title{{font-size:16px;font-weight:700;color:{NAVY};}}
.sh-tag{{background:{"#1e3a5f" if S.dark else "#e8f1fb"};color:{BLUE};font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:6px;}}
.tc{{background:{CARD};border:1px solid {BD};border-radius:10px;overflow:hidden;cursor:pointer;transition:all .18s;margin-bottom:10px;}}
.tc:hover{{border-color:{BLUE};box-shadow:0 4px 18px rgba(26,95,168,.12);transform:translateY(-2px);}}
.kp{{background:{"#0f172a" if S.dark else "#f0f9ff"};border:1px solid {"#334155" if S.dark else "#bae6fd"};border-left:3px solid {BLUE};border-radius:0 8px 8px 0;padding:12px;margin-bottom:8px;}}
.eq-box{{background:#0f172a;border-radius:8px;padding:14px 16px;font-family:'Roboto Mono',monospace;font-size:12px;color:#7dd3fc;line-height:2;border-left:3px solid {BLUE};overflow-x:auto;margin:8px 0;}}
.eq-card{{background:{CARD};border:1px solid {BD};border-radius:10px;padding:16px;position:relative;overflow:hidden;margin-bottom:14px;}}
.eq-card::before{{content:'';position:absolute;top:0;left:0;width:4px;height:100%;border-radius:2px 0 0 2px;}}
.eq-card.blue::before{{background:{BLUE};}}.eq-card.teal::before{{background:#0891b2;}}.eq-card.green::before{{background:#16a34a;}}
.eq-card.amber::before{{background:#d97706;}}.eq-card.purple::before{{background:#7c3aed;}}.eq-card.red::before{{background:#dc2626;}}
.nc{{background:{CARD};border:1px solid {BD};border-radius:8px;padding:11px 13px;margin-bottom:7px;transition:border-color .15s;}}
.nc:hover{{border-color:{BLUE};}}
.nc-src{{font-size:10px;font-weight:700;color:{BLUE};background:{"#1e3a5f" if S.dark else "#e8f1fb"};padding:2px 8px;border-radius:20px;display:inline-block;margin-bottom:5px;}}
.stButton>button{{background:{BLUE}!important;color:#fff!important;border:none!important;border-radius:6px!important;font-family:'Noto Sans KR',sans-serif!important;font-weight:600!important;}}
.stButton>button:hover{{background:#2172c4!important;}}
[data-testid="metric-container"]{{background:{"#1e293b" if S.dark else "#f8fafc"}!important;border:1px solid {BD}!important;border-radius:8px!important;border-left:3px solid {BLUE}!important;padding:12px!important;}}
[data-testid="stExpander"]{{border:1px solid {BD}!important;border-radius:8px!important;}}
.pb-wrap{{height:7px;background:{BD};border-radius:4px;overflow:hidden;}}
.pb-fill{{height:100%;background:linear-gradient(90deg,{BLUE},#0891b2);border-radius:4px;transition:width .4s;}}
</style>
""",unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(f'<div style="background:{NAVY};padding:12px 14px;border-radius:10px;margin-bottom:12px;"><div style="font-size:13px;font-weight:700;color:#fff;">🧮 ECM 계산기</div><div style="font-size:10px;color:rgba(255,255,255,.6);margin-top:2px;">RC 파라미터 즉시 계산</div></div>',unsafe_allow_html=True)
    with st.expander("⚡ RC 파라미터 계산",expanded=True):
        r1=st.number_input("R₁ 분극 저항 (mΩ)",0.1,1000.0,15.8,0.1,key="sb_r1")
        c1=st.number_input("C₁ 커패시턴스 (F)",1.0,1e6,38000.0,100.0,key="sb_c1")
        r0=st.number_input("R₀ 직렬 저항 (mΩ)",0.1,1000.0,8.2,0.1,key="sb_r0")
        di=st.number_input("전류 Δi (A)",0.1,1000.0,5.0,0.5,key="sb_di")
        if st.button("🔢 계산하기",key="calc_go",use_container_width=True):
            tau=(r1/1000)*c1; dv0=r0*di; dvI=(r0+r1)*di; f1=math.exp(-1/tau)
            st.markdown(f'<div style="background:{"#1e3a5f" if S.dark else "#e8f1fb"};border-radius:8px;padding:10px;font-size:12px;"><div style="font-family:\'Roboto Mono\',monospace;color:{BLUE};">τ={tau:.1f}s ({tau/60:.1f}분)<br>4τ={4*tau:.0f}s<br>ΔV₀={dv0:.2f}mV<br>ΔV∞={dvI:.2f}mV<br>F₁={f1:.6f}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f'<div style="font-size:12px;font-weight:700;color:{NAVY};margin-bottom:6px;">📝 메모장</div>',unsafe_allow_html=True)
    memo=st.text_area("메모",value=S.memo,height=110,key="memo_a",label_visibility="collapsed")
    m1,m2=st.columns(2)
    with m1:
        if st.button("💾 저장",key="ms",use_container_width=True): S.memo=memo; st.success("저장됨!")
    with m2:
        if st.button("🗑 초기화",key="mc",use_container_width=True): S.memo=""; st.rerun()
    st.markdown("---")
    done=sum(1 for v in S.progress.values() if v)
    st.markdown(f'<div style="font-size:12px;font-weight:700;color:{TX};margin-bottom:6px;">📈 학습 진도 <span style="color:{BLUE};">{done}/{len(TOPICS)}</span></div><div class="pb-wrap"><div class="pb-fill" style="width:{done/len(TOPICS)*100:.0f}%;"></div></div><div style="font-size:10px;color:{TX2};margin-top:4px;">섹션 카드를 열면 자동 저장됩니다</div>',unsafe_allow_html=True)
    dcols=st.columns(7)
    for di2,tp in enumerate(TOPICS):
        with dcols[di2%7]:
            c="#1a5fa8" if S.progress.get(tp["id"],False) else BD
            st.markdown(f'<div style="height:5px;border-radius:2px;background:{c};" title="{tp["title"]}"></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("[📦 ESCtoolbox](http://mocha-java.uccs.edu/BMS1/)  \n[📄 Plett 2004](https://doi.org/10.1016/j.jpowsour.2004.02.032)")

# ── NAV ──
NAV=[("home","🏠 홈"),("topics","📖 주제별 학습"),("equations","🔢 핵심 수식"),("quiz","📝 퀴즈"),("bookmarks","🔖 북마크"),("notices","📢 공지사항")]
nc=st.columns(len(NAV)+3)
for ci,(k,v) in enumerate(NAV):
    with nc[ci]:
        if st.button(v,key=f"nav_{k}",use_container_width=True): S.page=k; st.rerun()
with nc[-3]:
    if st.button("🌙 다크" if not S.dark else "☀️ 라이트",key="dm",use_container_width=True): S.dark=not S.dark; st.rerun()
with nc[-2]:
    if st.button("🌐 EN" if S.lang=="ko" else "🌐 KO",key="lng",use_container_width=True): S.lang="en" if S.lang=="ko" else "ko"; st.rerun()
with nc[-1]:
    if st.button("🖨 PDF",key="pdf",use_container_width=True): st.info("브라우저 Ctrl+P(Cmd+P)로 PDF 저장하세요.")
st.markdown("<div style='height:4px;'></div>",unsafe_allow_html=True)

def sh(title,tag=""):
    tag_h=f'<span class="sh-tag">{tag}</span>' if tag else ""
    st.markdown(f'<div class="sh"><div class="sh-bar"></div><div class="sh-title">{title}{tag_h}</div></div>',unsafe_allow_html=True)

def refresh_news():
    try:
        import xml.etree.ElementTree as ET
        r=requests.get("https://news.google.com/rss/search?q=battery+management+system+BMS&hl=ko&gl=KR&ceid=KR:ko",timeout=5)
        root=ET.fromstring(r.content); items=root.findall(".//item")[:5]; news=[]
        for it in items:
            title=re.sub(r'<[^>]+>','',it.find("title").text or "")
            link=it.find("link").text or "#"
            pub=it.find("pubDate").text or ""
            src=it.find("{https://news.google.com/rss}source"); src=src.text if src is not None else "Google News"
            if " - " in title: parts=title.rsplit(" - ",1); title,src=parts[0].strip(),parts[1].strip()
            try:
                from email.utils import parsedate
                dt=datetime(*parsedate(pub)[:6]); ds=dt.strftime("%Y. %m. %d.")
            except: ds=pub[:16]
            news.append({"title":title,"source":src,"date":ds,"url":link})
        return news
    except:
        return [{"title":"EV Battery Management Systems: Powering the Heart of Electric Mobility","source":"Bisinfotech","date":"2025. 10. 21.","url":"#"},
                {"title":"BMS functional verification: the safety-first approach","source":"Charged EVs","date":"2023. 10. 18.","url":"#"},
                {"title":"Power HIL test platform unveiled by Chroma","source":"Electronics360","date":"2024. 6. 25.","url":"#"},
                {"title":"Demand for Battery Management System in UK — Market Report 2036","source":"Future Market Insights","date":"2026. 1. 19.","url":"#"}]

def refresh_papers():
    try:
        import xml.etree.ElementTree as ET
        ns={"a":"http://www.w3.org/2005/Atom"}
        r=requests.get("https://export.arxiv.org/api/query?search_query=all:battery+equivalent+circuit+model&start=0&max_results=4&sortBy=submittedDate&sortOrder=descending",timeout=5)
        root=ET.fromstring(r.content); papers=[]
        for e in root.findall("a:entry",ns):
            t=e.find("a:title",ns).text.strip().replace("\n"," ")
            l=e.find("a:id",ns).text
            p=e.find("a:published",ns).text[:10]
            au=[a.find("a:name",ns).text for a in e.findall("a:author",ns)]
            ab=e.find("a:summary",ns).text.strip()[:120]+"…"
            papers.append({"title":t,"authors":", ".join(au[:2]),"date":p,"url":l,"abstract":ab})
        return papers
    except:
        return [{"title":"Enhanced Self-Correcting Battery Model with EKF","authors":"Zhang et al.","date":"2025-02","url":"#","abstract":"ESC 모델과 EKF를 결합한 SoC 추정 연구..."},
                {"title":"LSTM-ECM Hybrid Model for Battery State Estimation","authors":"Liu et al.","date":"2024-11","url":"#","abstract":"LSTM과 등가회로 모델의 하이브리드 접근..."},
                {"title":"Temperature-Dependent RC Model for Li-ion","authors":"Kim et al.","date":"2024-08","url":"#","abstract":"온도 의존 RC 파라미터 추출 방법론..."}]

# ═══ HOME ═══
if S.page=="home":
    st.markdown(f'<div class="hero-wrap"><img src="data:image/png;base64,{HERO}" style="width:100%;height:340px;object-fit:cover;display:block;"><div class="hero-ov"></div><div class="hero-grid"></div><div class="hero-body"><div class="hero-badge">📚 Plett(2015) BMS Vol.1 · Chapter 02</div><div class="hero-title">배터리 <em>등가회로 모델</em><br>학술 연구 포털</div><div class="hero-sub">OCV·ESR·확산전압·히스테리시스를 통합한 ESC 모델까지 — 핵심 개념·수식·인터랙티브 실습을 한눈에.</div><div style="display:flex;gap:10px;flex-wrap:wrap;"><div class="hero-stat"><div class="hero-stat-num">14</div><div class="hero-stat-lbl">주제 섹션</div></div><div class="hero-stat"><div class="hero-stat-num">5.37<span style="font-size:12px">mV</span></div><div class="hero-stat-lbl">RMSE</div></div><div class="hero-stat"><div class="hero-stat-num">99.9<span style="font-size:12px">%</span></div><div class="hero-stat-lbl">쿨롱 효율</div></div><div class="hero-stat"><div class="hero-stat-num">10</div><div class="hero-stat-lbl">퀴즈 문제</div></div></div></div></div>',unsafe_allow_html=True)

    sh("🔍 자료 검색")
    sc1,sc2=st.columns([1,5])
    with sc1: sp_cat=st.selectbox("분류",["전체","수식","개념","참고문헌"],label_visibility="collapsed",key="sp_cat")
    with sc2: sp_q=st.text_input("검색어",placeholder="검색어 입력 (예: OCV, 쿨롱 효율, RC 시정수...)",label_visibility="collapsed",key="sp_q")
    tags2=["OCV","SoC","등가 직렬 저항","확산 전압","히스테리시스","칼만 필터","와버그 임피던스","MATLAB","ESC 모델"]
    st.markdown(" ".join([f'<span style="display:inline-block;background:{"#1e3a5f" if S.dark else "#e8f1fb"};color:{BLUE};border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;cursor:pointer;margin:2px;border:1px solid {"#264e7f" if S.dark else "#c8ddf5"};">{t}</span>' for t in tags2]),unsafe_allow_html=True)
    if sp_q:
        q_low=sp_q.lower()
        hits=[d for d in SEARCH_DB if q_low in d["k"].lower() or q_low in d["title"].lower() or q_low in d["d"].lower()]
        if sp_cat!="전체":
            tm={"수식":"eq","개념":"concept","참고문헌":"ref"}
            hits=[h for h in hits if h["t"]==tm.get(sp_cat,"")]
        if hits:
            st.markdown(f"**'{sp_q}' 검색 결과 {len(hits)}건**")
            for h in hits:
                if st.button(f"📌 {h['title']} — {h['d']}",key=f"sr_{h['title']}",use_container_width=True):
                    S.selected_topic=h.get("tid"); S.page="topics"; st.rerun()
        else: st.info("검색 결과가 없습니다.")

    st.markdown("---")
    sh("📋 배터리 등가회로를 결정하는 핵심 기술")
    qm=st.columns(7)
    qm_items=[("📖","주제별 학습","topics"),("🔢","핵심 수식","equations"),("📝","이해도 퀴즈","quiz"),("🔖","북마크","bookmarks"),("📢","공지사항","notices"),("🧮","계산기","calc"),("🖨","PDF 저장","pdf")]
    for ci,(ico,lbl,act) in enumerate(qm_items):
        with qm[ci]:
            if st.button(f"{ico}\n{lbl}",key=f"qm_{act}",use_container_width=True):
                if act in("home","topics","equations","quiz","bookmarks","notices"): S.page=act; st.rerun()
                elif act=="calc": st.info("왼쪽 사이드바의 ECM 계산기를 이용하세요.")
                elif act=="pdf": st.info("브라우저 Ctrl+P(Cmd+P)로 PDF 저장하세요.")

    st.markdown("---")
    sh("📖 주제별 학습 미리보기","14 Topics")
    fc=st.columns(4)
    for ci,tp in enumerate(TOPICS[:4]):
        thumb=make_thumb(ci,TC[ci][0],TC[ci][1])
        with fc[ci]:
            st.markdown(f'<div class="tc"><img src="data:image/png;base64,{thumb}" style="width:100%;height:100px;object-fit:cover;"><div style="padding:8px 10px;"><div style="font-size:10px;color:{BLUE};font-weight:700;">SECTION {tp["num"]}</div><div style="font-size:13px;font-weight:700;color:{TX};">{tp["title"]}</div><div style="font-size:11px;color:{TX2};">{tp["desc"]}</div></div></div>',unsafe_allow_html=True)
            if st.button("자세히 보기 →",key=f"ft_{tp['id']}",use_container_width=True):
                S.selected_topic=tp["id"]; S.page="topics"; st.rerun()
    if st.button("전체 14개 주제 보기 ▼",use_container_width=True,key="all_t"):
        S.page="topics"; st.rerun()

    st.markdown("---")
    sh("📰 배터리 뉴스 · SCI 논문 · 관련 자료")
    bt=st.radio("",["📰 배터리 뉴스","📄 SCI 논문","🔗 관련 자료"],horizontal=True,key="bt",label_visibility="collapsed")
    if bt=="📰 배터리 뉴스":
        cr,_=st.columns([1,5])
        with cr:
            if st.button("🔄 강제 갱신",key="nr"): S.news_cache=None
        if S.news_cache is None:
            with st.spinner("뉴스 불러오는 중..."): S.news_cache=refresh_news()
        nl=S.news_cache
        st.markdown(f'<div style="font-size:10px;color:{TX2};margin-bottom:10px;">GOOGLE NEWS RSS · Ch.16 — 진단 ({len(nl)}) · <span style="color:#22c55e;">● 캐시 유효</span></div>',unsafe_allow_html=True)
        nnc=st.columns(min(4,len(nl)))
        for ni,news in enumerate(nl[:4]):
            with nnc[ni]:
                thumb_n=make_thumb(ni%14,TC[ni%14][0],TC[ni%14][1])
                st.markdown(f'<div class="nc"><img src="data:image/png;base64,{thumb_n}" style="width:100%;height:100px;object-fit:cover;border-radius:5px;margin-bottom:7px;"><div class="nc-src">{news["source"]}</div><div style="font-size:13px;font-weight:700;color:{TX};line-height:1.5;margin-bottom:4px;">{news["title"][:65]}{"..." if len(news["title"])>65 else ""}</div><div style="font-size:10px;color:{TX2};">{news["date"]}</div><a href="{news["url"]}" target="_blank" style="font-size:11px;color:{BLUE};font-weight:600;">원문 보기 ↗</a></div>',unsafe_allow_html=True)
    elif bt=="📄 SCI 논문":
        cr2,_=st.columns([1,5])
        with cr2:
            if st.button("🔄 강제 갱신",key="pr"): S.paper_cache=None
        if S.paper_cache is None:
            with st.spinner("논문 불러오는 중..."): S.paper_cache=refresh_papers()
        for p in S.paper_cache:
            with st.expander(f"📄 {p['title'][:55]}..."):
                st.markdown(f"**저자:** {p['authors']}  \n**날짜:** {p['date']}  \n**요약:** {p['abstract']}")
                if p["url"]!="#": st.markdown(f"[🔗 arXiv 원문]({p['url']})")
    else:
        rel=[("📦","MATLAB ESCtoolbox","mocha-java.uccs.edu/BMS1/","Plett 교수 제공 코드","http://mocha-java.uccs.edu/BMS1/"),
             ("📄","Plett 2004 Part I","DOI: 10.1016/j.jpowsour.2004.02.032","EKF for BMS Part I","https://doi.org/10.1016/j.jpowsour.2004.02.032"),
             ("📄","Hu 2012","DOI: 10.1016/j.jpowsour.2011.10.013","ECM 비교 연구","https://doi.org/10.1016/j.jpowsour.2011.10.013"),
             ("📄","Dreyer 2010","DOI: 10.1038/nmat2718","히스테리시스 열역학 원인","https://doi.org/10.1038/nmat2718"),
             ("📘","BMS Vol.1","ISBN: 978-1-60807-650-3","Artech House 2015","https://www.artechhouse.com"),
             ("📄","Plett 2004 Part II","DOI: 10.1016/j.jpowsour.2004.02.033","EKF for BMS Part II","https://doi.org/10.1016/j.jpowsour.2004.02.033")]
        rc=st.columns(3)
        for ri,(ico,ttl,sub,desc,url) in enumerate(rel):
            with rc[ri%3]:
                st.markdown(f'<div class="nc"><div style="font-size:22px;margin-bottom:5px;">{ico}</div><div style="font-size:13px;font-weight:700;color:{TX};margin-bottom:2px;">{ttl}</div><div style="font-size:11px;color:{BLUE};font-family:\'Roboto Mono\',monospace;margin-bottom:3px;">{sub}</div><div style="font-size:12px;color:{TX2};">{desc}</div><a href="{url}" target="_blank" style="font-size:11px;color:{BLUE};font-weight:600;">바로가기 ↗</a></div>',unsafe_allow_html=True)

# ═══ TOPICS ═══
elif S.page=="topics":
    sh("주제별 학습","14 Topics")
    tnames=[f"Section {tp['num']}: {tp['title']}" for tp in TOPICS]
    sel_idx=0
    if S.selected_topic:
        for ti,tp in enumerate(TOPICS):
            if tp["id"]==S.selected_topic: sel_idx=ti; break
    sname=st.selectbox("섹션 선택",tnames,index=sel_idx,key="tsel")
    si=tnames.index(sname); tp=TOPICS[si]; S.progress[tp["id"]]=True
    thumb=make_thumb(si,TC[si][0],TC[si][1])
    tag_h=" ".join([f'<span style="font-size:10px;padding:2px 6px;border-radius:20px;background:{"#1e3a5f" if S.dark else "#e8f1fb"};color:{BLUE};display:inline-block;margin:1px;">{t}</span>' for t in tp["tags"]])
    bm_lbl="★ 저장됨" if tp["id"] in S.bookmarks else "☆ 북마크"
    ch,cb=st.columns([5,1])
    with ch:
        st.markdown(f'<div style="position:relative;border-radius:10px;overflow:hidden;margin-bottom:14px;"><img src="data:image/png;base64,{thumb}" style="width:100%;height:140px;object-fit:cover;display:block;"><div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(14,58,110,.85),rgba(26,95,168,.65));display:flex;flex-direction:column;justify-content:flex-end;padding:16px;"><div style="font-size:10px;letter-spacing:.12em;color:#7dd3fc;margin-bottom:5px;">SECTION {tp["num"]}</div><div style="font-size:20px;font-weight:900;color:#fff;margin-bottom:5px;">{tp["title"]}</div><div>{tag_h}</div></div></div>',unsafe_allow_html=True)
    with cb:
        if st.button(bm_lbl,key=f"bm_{tp['id']}",use_container_width=True):
            if tp["id"] in S.bookmarks: S.bookmarks.remove(tp["id"])
            else: S.bookmarks.append(tp["id"])
            st.rerun()

    tabs=st.tabs(["📖 개념 설명","🔢 핵심 수식","📊 AI 그래프","📋 비교 분석","📄 참고문헌"])
    with tabs[0]:
        st.markdown("#### 🎯 핵심 포인트")
        kc=st.columns(2)
        for ki,kp in enumerate(tp["kps"]):
            with kc[ki%2]:
                st.markdown(f'<div class="kp"><div style="font-size:20px;margin-bottom:3px;">{kp["i"]}</div><div style="font-size:12px;font-weight:700;color:{BLUE};margin-bottom:3px;">{kp["t"]}</div><div style="font-size:12px;color:{TX2};line-height:1.6;">{kp["d"]}</div></div>',unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 📝 상세 내용")
        st.markdown(tp["body"])
    with tabs[1]:
        for eq in tp["eqs"]:
            st.markdown(f'**{eq["t"]}**')
            st.markdown(f'<div class="eq-box">{eq["c"].replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
        if tp.get("vars"):
            st.markdown("#### 📐 기호 정의")
            st.dataframe(pd.DataFrame(tp["vars"],columns=["기호","의미"]),use_container_width=True,hide_index=True)
    with tabs[2]:
        dbg="#1e293b" if S.dark else "rgba(0,0,0,0)"
        gc="rgba(51,65,85,.5)" if S.dark else "rgba(226,232,240,.8)"
        tc2="#94a3b8" if S.dark else "#475569"
        lb=dict(paper_bgcolor=dbg,plot_bgcolor=dbg,font=dict(family="Noto Sans KR",color=tc2),
                margin=dict(l=40,r=20,t=40,b=40),height=290,legend=dict(orientation="h",y=-0.2),
                xaxis=dict(gridcolor=gc,color=tc2),yaxis=dict(gridcolor=gc,color=tc2))
        fig=None; tid=tp["id"]
        sx=[i/10 for i in range(11)]
        if tid=="t01":
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=sx,y=[3.0,3.40,3.65,3.75,3.82,3.89,3.97,4.05,4.12,4.18,4.20],name="NMC",line=dict(color="#1a5fa8",width=2.5)))
            fig.add_trace(go.Scatter(x=sx,y=[2.8,3.20,3.30,3.32,3.33,3.33,3.34,3.35,3.36,3.50,3.65],name="LFP",line=dict(color="#16a34a",width=2.5,dash="dash")))
            fig.update_layout(**lb,title="OCV vs SoC (NMC/LFP)",xaxis_title="SoC",yaxis_title="OCV (V)")
        elif tid=="t02":
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(range(11)),y=[0,0.3,0.7,1.2,1.8,2.5,3.0,3.8,4.5,5.0,5.8],name="쿨롱 카운팅",line=dict(color="#dc2626",width=2.5)))
            fig.add_trace(go.Scatter(x=list(range(11)),y=[0,0.2,0.3,0.3,0.4,0.5,0.5,0.6,0.7,0.8,0.9],name="EKF+ESC",line=dict(color="#1a5fa8",width=2.5)))
            fig.update_layout(**lb,title="SoC 추정 오차 비교",xaxis_title="시간 →",yaxis_title="SoC 오차 (%)")
        elif tid=="t03":
            temp=[-30,-20,-10,0,10,20,25,30,35,40,45]; r0v=[42,35,25,18,13,10,8.2,7.5,7.0,6.8,6.5]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=temp,y=r0v,name="R₀",fill="tozeroy",fillcolor="rgba(220,38,38,.1)",line=dict(color="#dc2626",width=2.5)))
            fig.add_shape(type="line",x0=25,x1=25,y0=0,y1=42,line=dict(color="#1a5fa8",dash="dash"))
            fig.update_layout(**lb,title="R₀ vs 온도 (아레니우스)",xaxis_title="온도 (°C)",yaxis_title="R₀ (mΩ)")
        elif tid=="t04":
            t_rc=list(range(81)); R1v2,C1v2,R0v2,Iv2=0.0158,38000,0.0082,5.0; irc2=0.0; vo2=[]; oc2=[]
            for tt in t_rc:
                oc2.append(4.1)
                if tt<5: vo2.append(4.1); irc2=0.0
                else:
                    F=math.exp(-1/(R1v2*C1v2)); irc2=F*irc2+(1-F)*Iv2; vo2.append(4.1-R1v2*irc2-R0v2*Iv2)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=t_rc,y=oc2,name="OCV",line=dict(color="#dc2626",dash="dash",width=1.5)))
            fig.add_trace(go.Scatter(x=t_rc,y=vo2,name="V(t)",fill="tonexty",fillcolor="rgba(26,95,168,.08)",line=dict(color="#1a5fa8",width=2.5)))
            fig.update_layout(**lb,title="RC 확산 전압 응답 (I=5A)",xaxis_title="시간 (s)",yaxis_title="전압 (V)")
        elif tid=="t06":
            omega=np.logspace(4,-4,400); R0n,R1n,C1n,Aw=0.0082,0.0158,38000,0.002; rez,imz=[],[]
            for w in omega:
                jw=complex(0,w); Z=R0n+R1n/(1+jw*R1n*C1n)+Aw/(complex(0,1)**0.5*w**0.5)
                rez.append(Z.real*1000); imz.append(-Z.imag*1000)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=rez,y=imz,mode="lines",name="임피던스",line=dict(color="#1a5fa8",width=2.5)))
            fig.update_layout(**lb,title="나이키스트 플롯 (EIS)",xaxis_title="Re(Z) mΩ",yaxis_title="-Im(Z) mΩ")
        elif tid=="t07":
            soc_h=np.linspace(0,1,11)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(soc_h),y=[2.8,3.3,3.34,3.35,3.36,3.37,3.38,3.40,3.45,3.5,3.65],name="충전 OCV",line=dict(color="#1a5fa8",width=2.5)))
            fig.add_trace(go.Scatter(x=list(soc_h),y=[2.8,3.2,3.27,3.28,3.29,3.30,3.31,3.33,3.38,3.44,3.60],name="방전 OCV",line=dict(color="#16a34a",width=2.5,dash="dash")))
            fig.update_layout(**lb,title="히스테리시스 루프 (LFP)",xaxis_title="SoC",yaxis_title="OCV (V)")
        elif tid=="t08":
            meas=[3.82,3.74,3.69,3.75,3.71,3.66,3.70,3.73,3.68,3.65,3.70]
            modl=[3.822,3.742,3.692,3.752,3.712,3.662,3.702,3.732,3.682,3.652,3.702]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(range(11)),y=meas,name="실측",mode="lines+markers",line=dict(color="#475569",dash="dot",width=2),marker=dict(size=5)))
            fig.add_trace(go.Scatter(x=list(range(11)),y=modl,name="ESC",line=dict(color="#1a5fa8",width=2.5)))
            fig.add_annotation(x=5,y=3.69,text="RMSE=5.37mV ✓",bgcolor="#dcfce7",bordercolor="#86efac",font=dict(color="#166534",size=11))
            fig.update_layout(**lb,title="ESC 검증: 모델 vs 실측 (UDDS)",xaxis_title="시간 →",yaxis_title="V (V)")
        if fig: st.plotly_chart(fig,use_container_width=True)
        else: st.info("이 섹션의 그래프는 수식 모음 탭에서 시뮬레이터로 확인하세요.")
    with tabs[3]:
        comp=tp.get("comp")
        if comp: st.dataframe(pd.DataFrame(comp["r"],columns=comp["h"]),use_container_width=True,hide_index=True)
    with tabs[4]:
        for lbl,doi in tp.get("refs",[]):
            doi_url=f"https://doi.org/{doi}" if doi else ""
            st.markdown(f'<div style="background:{"#1e3a5f" if S.dark else "#e8f1fb"};border-left:4px solid {BLUE};border-radius:0 8px 8px 0;padding:12px 14px;margin-bottom:10px;"><div style="font-size:10px;font-weight:700;color:{BLUE};margin-bottom:4px;">{lbl}</div>{"<a href="+chr(39)+doi_url+chr(39)+" target="+chr(39)+"_blank"+chr(39)+" style="+chr(39)+"font-family:monospace;font-size:11px;color:"+BLUE+";"+chr(39)+">DOI: "+doi+"</a>" if doi else ""}</div>',unsafe_allow_html=True)
    p_prev,p_next=st.columns(2)
    with p_prev:
        if si>0 and st.button(f"← {TOPICS[si-1]['title']}",use_container_width=True,key="prev_t"):
            S.selected_topic=TOPICS[si-1]["id"]; st.rerun()
    with p_next:
        if si<len(TOPICS)-1 and st.button(f"{TOPICS[si+1]['title']} →",use_container_width=True,key="next_t"):
            S.selected_topic=TOPICS[si+1]["id"]; st.rerun()
    with st.expander("🗂 전체 14개 주제 목록"):
        ac=st.columns(4)
        for ti,t in enumerate(TOPICS):
            with ac[ti%4]:
                done2=S.progress.get(t["id"],False)
                if st.button(f"{'✅' if done2 else '⬜'} {t['num']}. {t['title']}",key=f"all_{t['id']}",use_container_width=True):
                    S.selected_topic=t["id"]; st.rerun()

# ═══ EQUATIONS ═══
elif S.page=="equations":
    sh("핵심 수식","6 equations")
    cc={"blue":"#1a5fa8","teal":"#0891b2","green":"#16a34a","amber":"#d97706","purple":"#7c3aed","red":"#dc2626"}
    ec=st.columns(2)
    for ei,eq in enumerate(EQUATIONS):
        col=cc.get(eq["cls"],BLUE)
        vs="".join([f'<div style="display:flex;gap:6px;font-size:11px;margin-bottom:2px;"><span style="font-family:\'Roboto Mono\',monospace;font-weight:700;color:{col};min-width:60px;">{v[0]}</span><span style="color:{TX2};">{v[1]}</span></div>' for v in eq["vars"]])
        with ec[ei%2]:
            st.markdown(f'<div class="eq-card {eq["cls"]}"><div style="font-size:10px;font-weight:700;color:{col};letter-spacing:.08em;margin-bottom:4px;">{eq["num"]}</div><div style="font-size:14px;font-weight:700;color:{NAVY};margin-bottom:7px;">{eq["title"]}</div><div class="eq-box">{eq["code"].replace(chr(10),"<br>")}</div><div style="font-size:12px;color:{TX2};margin:6px 0;">{eq["desc"]}</div><div style="border-top:1px solid {BD};padding-top:6px;margin-top:5px;">{vs}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    sh("📊 전압 응답 시뮬레이터")
    sc1_e,sc2_e=st.columns([1,1.5])
    with sc1_e:
        sI=st.slider("I (A)",1.0,100.0,20.0,1.0,key="eI")
        sR0=st.slider("R₀ (mΩ)",1.0,50.0,8.2,0.1,key="eR0")
        sR1=st.slider("R₁ (mΩ)",1.0,50.0,15.8,0.1,key="eR1")
        sC1=st.slider("C₁ (kF)",1.0,100.0,38.0,1.0,key="eC1")
        tau_e=(sR1/1000)*(sC1*1000); st.info(f"τ={tau_e:.0f}s | 4τ={4*tau_e:.0f}s ({4*tau_e/60:.1f}분)")
    with sc2_e:
        ts=list(range(81)); irc_e=0.0; vs_e=[]; oc_e=[]
        for tt in ts:
            oc_e.append(4.1)
            if tt<5: vs_e.append(4.1); irc_e=0.0
            else:
                F=math.exp(-1/((sR1/1000)*(sC1*1000))); irc_e=F*irc_e+(1-F)*sI
                vs_e.append(4.1-(sR1/1000)*irc_e-(sR0/1000)*sI)
        dbg2="#1e293b" if S.dark else "rgba(0,0,0,0)"; gc2="rgba(51,65,85,.4)" if S.dark else "rgba(226,232,240,.8)"
        fg=go.Figure()
        fg.add_trace(go.Scatter(x=ts,y=oc_e,name="OCV",line=dict(color="#dc2626",dash="dash",width=1.5)))
        fg.add_trace(go.Scatter(x=ts,y=vs_e,name="V(t)",fill="tonexty",fillcolor="rgba(26,95,168,.07)",line=dict(color=BLUE,width=2.5)))
        fg.update_layout(paper_bgcolor=dbg2,plot_bgcolor=dbg2,font=dict(color=TX2),
                         margin=dict(l=40,r=20,t=40,b=40),height=280,
                         title=f"V(t) | I={sI}A R₀={sR0}mΩ τ={tau_e:.0f}s",
                         xaxis_title="시간(s)",yaxis_title="전압(V)",
                         xaxis=dict(gridcolor=gc2,color=TX2),yaxis=dict(gridcolor=gc2,color=TX2),
                         legend=dict(orientation="h",y=-0.25))
        st.plotly_chart(fg,use_container_width=True)

# ═══ QUIZ ═══
elif S.page=="quiz":
    sh("이해도 퀴즈","10 Questions")
    r_col,_=st.columns([1,5])
    with r_col:
        if st.button("🔄 다시 시작",key="qr"): S.quiz_idx=0; S.quiz_score=0; S.quiz_answered=False; S.quiz_done=False; st.rerun()
    if S.quiz_done:
        pct=int(S.quiz_score/len(QUIZ_Q)*100)
        msg=("🏆 완벽! 배터리 모델링 마스터!" if pct==100 else "👍 훌륭합니다!" if pct>=70 else "📚 조금 더 복습해보세요.")
        st.markdown(f'<div style="background:{"#1e3a5f" if S.dark else "#e8f1fb"};border:1px solid {"#264e7f" if S.dark else "#bae6fd"};border-radius:12px;padding:32px;text-align:center;"><div style="font-size:48px;margin-bottom:12px;">🎉</div><div style="font-size:44px;font-weight:900;color:{BLUE};font-family:\'Roboto Mono\',monospace;">{S.quiz_score} / {len(QUIZ_Q)}</div><div style="font-size:16px;color:{TX2};margin:10px 0;">{msg}</div></div>',unsafe_allow_html=True)
    else:
        idx=S.quiz_idx; q=QUIZ_Q[idx]
        st.progress(idx/len(QUIZ_Q),text=f"문제 {idx+1}/{len(QUIZ_Q)} · 점수: {S.quiz_score}점")
        st.markdown(f"### Q{idx+1}. {q['q']}")
        if not S.quiz_answered:
            for oi,opt in enumerate(q["opts"]):
                if st.button(f"{chr(65+oi)}. {opt}",key=f"qo{idx}_{oi}",use_container_width=True):
                    S.quiz_answered=True; S.quiz_selected=oi
                    if oi==q["ans"]: S.quiz_score+=1
                    st.rerun()
            if st.button("⏭ 건너뛰기",key=f"sk{idx}"): S.quiz_answered=True; S.quiz_selected=-1; st.rerun()
        else:
            sel=S.quiz_selected
            for oi,opt in enumerate(q["opts"]):
                lb2=f"{chr(65+oi)}. {opt}"
                if oi==q["ans"]: st.success(f"✅ {lb2}")
                elif oi==sel: st.error(f"❌ {lb2}")
                else: st.markdown(f'<div style="padding:9px 12px;border:1px solid {BD};border-radius:6px;color:{TX2};margin:3px 0;">{lb2}</div>',unsafe_allow_html=True)
            st.markdown(f'<div style="background:{"#1e3a5f" if S.dark else "#e8f1fb"};border-left:3px solid {BLUE};border-radius:0 8px 8px 0;padding:12px;margin:10px 0;"><strong>💡 해설:</strong> {q["exp"]}<div class="eq-box" style="margin-top:8px;">{q["f"]}</div></div>',unsafe_allow_html=True)
            if st.button("다음 문제 →",type="primary",use_container_width=True,key=f"nx{idx}"):
                S.quiz_idx+=1; S.quiz_answered=False
                if S.quiz_idx>=len(QUIZ_Q): S.quiz_done=True
                st.rerun()

# ═══ BOOKMARKS ═══
elif S.page=="bookmarks":
    sh("북마크",f"{len(S.bookmarks)}건")
    if not S.bookmarks:
        st.info("북마크한 항목이 없습니다. 주제별 학습 페이지에서 ☆ 버튼을 눌러 북마크를 추가하세요.")
    else:
        for bm_id in S.bookmarks:
            tp_bm=next((t for t in TOPICS if t["id"]==bm_id),None)
            if tp_bm:
                b1,b2,b3=st.columns([4,1,1])
                with b1: st.markdown(f"**Section {tp_bm['num']}: {tp_bm['title']}** — {tp_bm['desc']}")
                with b2:
                    if st.button("열기",key=f"bo_{bm_id}",use_container_width=True): S.selected_topic=bm_id; S.page="topics"; st.rerun()
                with b3:
                    if st.button("삭제 ✕",key=f"bd_{bm_id}",use_container_width=True): S.bookmarks.remove(bm_id); st.rerun()
                st.markdown(f'<hr style="border-color:{BD};margin:6px 0;">',unsafe_allow_html=True)

# ═══ NOTICES ═══
elif S.page=="notices":
    sh("공지사항")
    ntab=st.radio("",["공지사항","업데이트","Q&A"],horizontal=True,key="ntab_r",label_visibility="collapsed")
    st.markdown("---")
    for n in S.notices:
        nt=n["type"]
        if ntab=="공지사항" and nt!="공지": continue
        if ntab=="업데이트" and nt!="업데이트": continue
        if ntab=="Q&A" and nt!="Q&A": continue
        tc3="#1d4ed8" if nt=="공지" else ("#166534" if nt=="업데이트" else "#92400e")
        bc3="#dbeafe" if nt=="공지" else ("#dcfce7" if nt=="업데이트" else "#fef3c7")
        st.markdown(f'<div style="background:{CARD};border:1px solid {BD};border-radius:8px;padding:12px 14px;margin-bottom:7px;"><span style="font-size:10px;font-weight:700;padding:2px 7px;border-radius:20px;display:inline-block;margin-bottom:5px;background:{bc3};color:{tc3};">{n["type"]}</span><div style="font-size:14px;font-weight:700;color:{TX};margin-bottom:4px;">{n["title"]}</div><div style="font-size:13px;color:{TX2};margin-bottom:5px;">{n["body"]}</div><div style="font-size:11px;color:{TX2};">{n["date"]}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ✍️ 새 공지 작성")
    with st.form("nf"):
        ns=st.selectbox("분류",["공지","업데이트","Q&A"],key="nt_s")
        nt_title=st.text_input("제목",key="nt_t")
        nt_body=st.text_area("내용",key="nt_b")
        if st.form_submit_button("✅ 게시",use_container_width=True):
            if nt_title and nt_body:
                S.notices.insert(0,{"type":ns,"title":nt_title,"body":nt_body,"date":datetime.now().strftime("%Y-%m-%d")})
                st.success("공지가 게시되었습니다!"); st.rerun()
