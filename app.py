"""
ECM 등가회로 모델 연구포털
rain0807.streamlit.app 스타일
수정: NAV 링크 작동, 뉴스룸 1:1 비율, 기능 전체 정상화
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np, pandas as pd
import base64, io, math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter

st.set_page_config(
    page_title="ECM 등가회로 모델 연구포털",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE 초기화 ─────────────────────────────────────
def _init():
    defaults = {
        "_ss_page":       "home",
        "_ss_dark":       False,
        "_ss_lang":       "ko",
        "_ss_bookmarks":  [],
        "_ss_progress":   {},
        "_ss_memo":       "",
        "_ss_quiz_idx":   0,
        "_ss_quiz_score": 0,
        "_ss_quiz_ans":   False,
        "_ss_quiz_done":  False,
        "_ss_quiz_sel":   -1,
        "_ss_topic":      "t01",
        "_ss_scroll_to":  "",   # 홈 내 앵커 이동용
        "_ss_notices": [
            {"type":"공지",     "title":"ECM 연구포털 오픈",          "body":"rain0807 스타일 신규 디자인이 적용되었습니다.",            "date":"2026-04-16"},
            {"type":"업데이트", "title":"나이키스트 플롯 추가",        "body":"t06 와버그 섹션에서 EIS 나이키스트 플롯을 확인하세요.", "date":"2026-04-15"},
            {"type":"Q&A",      "title":"MATLAB 툴박스 다운로드 방법","body":"http://mocha-java.uccs.edu/BMS1/ 에서 무료로 받으실 수 있습니다.", "date":"2026-04-14"},
        ],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

def gs(k):    return st.session_state[k]
def ss(k, v): st.session_state[k] = v

# ── 색상 ──────────────────────────────────────────────────────
TEAL  = "#2dd4bf"
NAVY  = "#0f172a"
GRAY  = "#475569"
LGRAY = "#94a3b8"
BG    = "#ffffff"
BG2   = "#f8fafc"
BD    = "#e2e8f0"

# ── PIL 이미지 생성 ──────────────────────────────────────────
def _b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data
def make_hero():
    w, h = 1600, 720

    # numpy로 부드러운 2D 그라디언트
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / h
        for x in range(w):
            tx = x / w
            r = int(6  + tx * 6  + t * 5)
            g = int(12 + tx * 8  + t * 10)
            b = int(32 + tx * 20 + t * 18)
            arr[y, x] = [min(255,r), min(255,g), min(255,b)]

    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)

    # 미세 격자 (거의 안 보이는 수준)
    gc = (18, 38, 58)
    for x in range(0, w, 80):
        draw.line([(x, 0), (x, h)], fill=gc, width=1)
    for y2 in range(0, h, 80):
        draw.line([(0, y2), (w, y2)], fill=gc, width=1)

    # 틸 컬러 블렌딩 헬퍼 (반투명 효과)
    teal = (45, 212, 191)
    def blend(yx, teal_color, alpha):
        yc, xc = yx
        yc = max(0, min(h-1, yc)); xc = max(0, min(w-1, xc))
        bg = arr[yc, xc].tolist()
        return tuple(int(bg[i]*(1-alpha) + teal_color[i]*alpha) for i in range(3))

    # 회로 라인 (오른쪽 상단)
    lines = [
        (1000, 90, 1180, 90, 2, 0.55),
        (1180, 90, 1180, 200, 2, 0.55),
        (1180, 200, 1380, 200, 2, 0.55),
        (940, 300, 1100, 300, 1, 0.30),
        (1100, 300, 1100, 420, 1, 0.30),
        (1100, 420, 1300, 420, 1, 0.30),
        (1300, 140, 1480, 140, 1, 0.22),
        (1300, 140, 1300, 330, 1, 0.22),
    ]
    for x0,y0,x1,y1,wd,alpha in lines:
        lc = blend(((y0+y1)//2, (x0+x1)//2), teal, alpha)
        draw.line([(x0,y0),(x1,y1)], fill=lc, width=wd)

    # 노드 점
    for cx,cy,alpha in [(1180,90,0.70),(1180,200,0.70),(1100,300,0.45),(1100,420,0.45)]:
        nc = blend((cy, cx), teal, alpha)
        draw.ellipse([cx-5,cy-5,cx+5,cy+5], fill=nc)

    # 저항 박스
    for rx, ry, alpha in [(1220, 82, 0.50), (1140, 292, 0.30)]:
        bc = blend((ry+7, rx+22), (8, 20, 45), 0.92)
        oc = blend((ry+7, rx+22), teal, alpha)
        draw.rectangle([(rx, ry), (rx+44, ry+14)], fill=bc, outline=oc, width=1)

    return _b64(img.filter(ImageFilter.GaussianBlur(0.6)))

@st.cache_data
def make_why_photo():
    w, h = 760, 500
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y/h
        r = int(185+t*45); g = int(195+t*38); b = int(205+t*30)
        draw.line([(0,y),(w,y)], fill=(r,g,b))
    draw.rounded_rectangle([60,210,700,430], radius=18, fill=(28,38,58), outline=(55,75,115), width=2)
    draw.rounded_rectangle([290,238,680,415], radius=12, fill=(18,28,46), outline=(45,212,191), width=1)
    pts = [(300,380),(340,340),(380,355),(420,310),(460,330),(500,290),(540,305),(580,265),(620,280),(660,260)]
    draw.line(pts, fill=(45,212,191), width=3)
    draw.ellipse([100,280,255,390], outline=(75,95,125), width=3)
    return _b64(img.filter(ImageFilter.GaussianBlur(0.4)))

@st.cache_data
def make_topic_bg(idx):
    palettes = [
        ((12,22,44),(18,40,80)),((8,38,58),(12,60,95)),((38,12,12),(72,22,22)),
        ((12,38,28),(18,68,48)),((38,28,8),(68,52,12)),((18,12,48),(32,22,88)),
        ((8,32,42),(12,58,78)),((32,12,38),(58,22,68)),((8,38,18),(12,68,32)),
        ((42,18,8),(78,32,12)),((12,12,48),(22,22,88)),((38,8,28),(68,15,52)),
        ((8,32,32),(12,62,62)),((32,32,8),(62,62,12)),
    ]
    c1, c2 = palettes[idx % 14]
    w, h = 800, 520
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y/h
        r = int(c1[0]+t*(c2[0]-c1[0])); g = int(c1[1]+t*(c2[1]-c1[1])); bv = int(c1[2]+t*(c2[2]-c1[2]))
        draw.line([(0,y),(w,y)], fill=(r,g,bv))
    draw.rectangle([55,75,175,155], outline=(255,255,255), width=1)
    draw.line([(175,115),(240,115)], fill=(255,255,255), width=2)
    return _b64(img)

@st.cache_data
def make_logo():
    sz = 36
    img = Image.new("RGBA", (sz, sz), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0,0,sz-1,sz-1], radius=9, fill=(45,212,191))
    draw.ellipse([12,12,24,24], outline="white", width=2)
    for pts in [[(4,18),(12,18)],[(24,18),(32,18)],[(18,4),(18,12)],[(18,24),(18,32)]]:
        draw.line(pts, fill="white", width=2)
    return _b64(img)

@st.cache_data
def make_news_img(idx):
    palettes = [((12,22,42),(7,13,26)),((22,42,22),(11,26,11)),((12,18,38),(7,9,22)),((32,18,46),(18,9,28))]
    c1n, c2n = palettes[idx % 4]
    nw, nh = 300, 300   # 1:1 비율
    nimg = Image.new("RGB", (nw, nh))
    ndraw = ImageDraw.Draw(nimg)
    for y in range(nh):
        t = y/nh
        ndraw.line([(0,y),(nw,y)], fill=tuple(int(c1n[k]+t*(c2n[k]-c1n[k])) for k in range(3)))
    # 장식
    ndraw.line([(20,nh//2),(nw-20,nh//2)], fill=(45,212,191), width=1)
    ndraw.ellipse([nw//2-20,nh//2-20,nw//2+20,nh//2+20], outline=(45,212,191), width=2)
    return _b64(nimg)

LOGO = make_logo()
HERO = make_hero()
WHY  = make_why_photo()

# ── TOPICS ────────────────────────────────────────────────────
TOPICS = [
    {"id":"t01","num":"01","title":"개방회로 전압 (OCV)","sub":"무부하 평형 전압의 기초","tags":["OCV","LUT","GITT"],
     "desc":"전류 i=0 상태의 단자 전압. SoC 추정의 핵심 기준값.",
     "kps":[{"i":"⚡","t":"정의","d":"전류 i=0 상태의 단자 전압. 순수 전기화학적 평형 전압."},
            {"i":"📈","t":"SoC 의존성","d":"OCV(z,T): 2차원 함수. NMC:S형. LFP:극평탄(3.33V)."},
            {"i":"🔬","t":"측정","d":"C/30 저속 방전(60h+) 또는 GITT 기법으로 취득."},
            {"i":"🌡️","t":"온도 보정","d":"OCV(z,T)=OCV₀(z)+T·OCVrel(z). 행렬 최소제곱으로 결정."}],
     "eqs":[{"t":"이상 전압원 모델","c":"v(t) = OCV(z(t))  // i=0 가정"},
            {"t":"온도 보정 모델","c":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)"}],
     "comp":{"h":["항목","NMC","LFP"],"r":[["OCV 형태","단조 S곡선","극평탄(3.33V)"],["히스테리시스","<10mV","50~100mV"],["SoC 추정 난이도","보통","어려움"]]},
     "refs":[("Plett 2004 Part I","10.1016/j.jpowsour.2004.02.031")]},

    {"id":"t02","num":"02","title":"충전 상태 의존성 (SoC)","sub":"잔존 전하량 이산화 구현","tags":["SoC","쿨롱 효율","ZOH"],
     "desc":"쿨롱 카운팅과 이산시간 점화식으로 MCU에서 구현.",
     "kps":[{"i":"🔢","t":"정의","d":"z∈[0,1]. 완방전=0, 완충=1."},
            {"i":"⚗️","t":"쿨롱 효율","d":"리튬이온: 99~99.9%."},
            {"i":"💻","t":"이산화","d":"연속 ODE → Δt로 이산화. MCU 실시간 연산."},
            {"i":"📊","t":"정확도","d":"쿨롱 카운팅:±2~5%. EKF+ESC:±0.5~1.5%."}],
     "eqs":[{"t":"연속시간 상태방정식","c":"ż(t) = −η(t)·i(t) / Q"},
            {"t":"이산시간 점화식 (식 2.4)","c":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"}],
     "comp":{"h":["방법","RMSE","오차 누적"],"r":[["쿨롱 카운팅","±2~5%","있음"],["OCV 맵핑","±1~3%","없음(정지)"],["EKF+ESC","±0.5~1.5%","자가 교정"]]},
     "refs":[("Zheng 2018","10.1016/j.jpowsour.2017.11.044")]},

    {"id":"t03","num":"03","title":"등가 직렬 저항 (R₀)","sub":"순간 전압 강하 모델링","tags":["ESR","R₀","온도"],
     "desc":"저온에서 3~5배 증가하는 등가 직렬 저항. R₀=8.2mΩ(교재).",
     "kps":[{"i":"🔌","t":"구성","d":"전해질+집전체+SEI 저항. 순간 전압 강하 원인."},
            {"i":"❄️","t":"온도 의존","d":"0°C에서 25°C 대비 3~5배. 겨울철 EV 출력 저하 주원인."},
            {"i":"📐","t":"측정","d":"R₀=|ΔV₀/Δi|. 교재: 41mV÷5A=8.2mΩ."},
            {"i":"📉","t":"노화","d":"노화 시 R₀ 증가 → SoH 지표로 활용."}],
     "eqs":[{"t":"단자 전압","c":"v(t) = OCV(z(t)) − i(t)·R₀"},
            {"t":"R₀ 추출","c":"R₀ = |ΔV₀/Δi| = 8.2 mΩ (교재: Δi=5A)"}],
     "comp":{"h":["온도","R₀ 배수","현상"],"r":[["−30°C","~5배","시동 불가"],["0°C","~3배","주행거리 급감"],["25°C","기준","정상"],["45°C","~0.8배","성능 소폭 향상"]]},
     "refs":[("Hu 2012","10.1016/j.jpowsour.2011.10.013")]},

    {"id":"t04","num":"04","title":"확산 전압 (RC 회로)","sub":"ZOH 이산화 RC 분극","tags":["RC","ZOH","시정수"],
     "desc":"리튬 이온 농도 구배에 의한 느린 동적 전압. τ≈600s.",
     "kps":[{"i":"🌊","t":"물리적 원인","d":"전극 내 리튬 이온 농도 구배. 분 단위의 느린 시간 상수."},
            {"i":"💡","t":"손전등 비유","d":"방전된 손전등을 끄면 2분 후 다시 켜짐 → 확산 전압 해소."},
            {"i":"⚙️","t":"RC 모델링","d":"R₁-C₁ 병렬 서브회로. τ=R₁C₁. 교재:≈600s(10분)."},
            {"i":"💻","t":"ZOH 이산화","d":"F₁=exp(-Δt/τ). 오일러보다 수치적으로 안정."}],
     "eqs":[{"t":"ZOH 이산화 (식 2.8)","c":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)"},
            {"t":"단자 전압","c":"v[k] = OCV(z[k]) − R₁·i_R1[k] − R₀·i[k]"}],
     "comp":{"h":["모델","RC쌍","RMSE"],"r":[["1RC(ESC)","1","5~15mV"],["2RC","2","3~8mV"],["FO-ECM","분수차","2~5mV"]]},
     "refs":[("Seaman 2014","10.1016/j.jpowsour.2013.11.037")]},

    {"id":"t05","num":"05","title":"대략적인 파라미터 값","sub":"R₀=8.2mΩ R₁=15.8mΩ C₁≈38kF","tags":["HPPC","펄스","추출"],
     "desc":"펄스 응답 실험으로 RC 파라미터를 추출하는 방법.",
     "kps":[{"i":"⚡","t":"R₀ 추출","d":"순간 강하. R₀=|ΔV₀/Δi|=8.2mΩ"},
            {"i":"📈","t":"R₁ 추출","d":"정상상태 강하. R₁=|ΔV∞/Δi|−R₀=15.8mΩ"},
            {"i":"⏱️","t":"C₁ 추출","d":"시간 상수 역산. C₁≈38kF, τ≈600s"},
            {"i":"🔄","t":"반복 정제","d":"최소제곱법으로 파라미터 최적화."}],
     "eqs":[{"t":"파라미터 추출","c":"R₀=|ΔV₀/Δi|=8.2mΩ\nR₁=|ΔV∞/Δi|−R₀=15.8mΩ\nτ=R₁×C₁≈600s  →  C₁≈38kF"}],
     "comp":{"h":["파라미터","값","온도 의존"],"r":[["R₀","8.2mΩ","강함(아레니우스)"],["R₁","15.8mΩ","있음"],["C₁","38kF","있음(비단조)"],["τ","600s","있음"]]},
     "refs":[("He 2011","10.3390/en4040582")]},

    {"id":"t06","num":"06","title":"와버그 임피던스","sub":"나이키스트 플롯 45° 직선","tags":["EIS","나이키스트","45°"],
     "desc":"고체 확산의 주파수 표현. 저주파 영역 45° 직선.",
     "kps":[{"i":"📡","t":"EIS","d":"주파수를 바꿔가며 교류 전압 인가→전류 응답→임피던스 측정."},
            {"i":"📐","t":"45° 특성","d":"Z_W=A_W/√(jω). 실수부=허수부→위상각 45°."},
            {"i":"🔬","t":"나이키스트 구간","d":"고주파:R₀. 중주파:RC 반원. 저주파:45° 직선."},
            {"i":"⚡","t":"랜들스 회로","d":"Rₛ+(Cdl//(Rct+Z_W)) — 표준 전기화학 등가회로."}],
     "eqs":[{"t":"와버그 임피던스","c":"Z_W(jω) = A_W / √(jω)\n위상각 = 45°"}],
     "comp":{"h":["주파수","위치","현상"],"r":[["고주파(kHz)","실수축 교점","전해질 저항 R₀"],["중주파(Hz)","반원","RC 분극"],["저주파(mHz)","45° 직선","와버그 확산"]]},
     "refs":[("Randles 1947","10.1039/df9470100011")]},

    {"id":"t07","num":"07","title":"히스테리시스 전압","sub":"경로 의존적 OCV 이력 현상","tags":["히스테리시스","LFP","이력"],
     "desc":"충전/방전 경로에 따라 OCV가 달라지는 이력 현상. γ≈90.",
     "kps":[{"i":"🔄","t":"정의","d":"같은 SoC에서 충전/방전 후 OCV가 다름. SoC 변화에만 의존."},
            {"i":"🔋","t":"LFP에서 큼","d":"LFP:50~100mV. NMC:<10mV. SoC 추정 오류의 주원인."},
            {"i":"📐","t":"두 종류","d":"① 동적 h[k]: SoC 변화에 따라 지수 감쇠. ② 순간 s[k]: 전류 방향 즉각 반응."},
            {"i":"⏱️","t":"RC와 차이","d":"RC는 시간 경과 시 소멸. 히스테리시스는 SoC 변화 없으면 유지."}],
     "eqs":[{"t":"동적 히스테리시스","c":"h[k+1] = exp(−|η·i·γ·Δt/Q|)·h[k]\n        − (1−exp(···))·sgn(i[k])\nγ ≈ 90"},
            {"t":"히스테리시스 전압","c":"V_hys[k] = M₀·s[k] + M·h[k]"}],
     "comp":{"h":["특성","히스테리시스","RC 확산"],"r":[["시간 의존","없음","있음(소멸)"],["LFP 크기","50~100mV","수십mV"],["NMC 크기","<10mV","수십mV"]]},
     "refs":[("Dreyer 2010","10.1038/nmat2718")]},

    {"id":"t08","num":"08","title":"향상된 자가 교정 셀 모델 (ESC)","sub":"RMSE=5.37mV 검증 완료","tags":["ESC","상태공간","EKF"],
     "desc":"OCV+R₀+RC+히스테리시스를 통합한 최종 완성 모델.",
     "kps":[{"i":"🎯","t":"통합 구조","d":"상태벡터 x=[z,i_R,h]ᵀ. SoC·RC전류·히스테리시스 통합."},
            {"i":"🔄","t":"자가 교정","d":"i=0 휴지 시 RC→0. 전압이 OCV+히스테리시스로 자동 수렴."},
            {"i":"📊","t":"검증 성능","d":"25Ah NMC, UDDS 10h: RMSE=5.37mV ✓"},
            {"i":"🤖","t":"EKF 결합","d":"ESC+EKF → 실시간 SoC 자가 교정 추정."}],
     "eqs":[{"t":"ESC 상태방정식","c":"x[k+1] = A[k]·x[k] + B[k]·u[k]\n// x=[z,i_R,h]ᵀ"},
            {"t":"ESC 출력방정식","c":"v[k] = OCV(z,T) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]"}],
     "comp":{"h":["모델","RMSE","특징"],"r":[["OCV만","~100mV","최단순"],["+R₀","~50mV","순간강하"],["1RC ESC","~10mV","실용적"],["2RC ESC","~5mV","고정확"],["DFN+ML","<2mV","최고"]]},
     "refs":[("Plett 2004 II","10.1016/j.jpowsour.2004.02.033")]},

    {"id":"t09","num":"09","title":"셀 데이터 수집 실험실 장비","sub":"Arbin BT2043 + 환경 챔버","tags":["Arbin","환경챔버","장비"],
     "desc":"12채널 독립 테스트 시스템과 −45°C~190°C 환경 챔버.",
     "kps":[{"i":"🔬","t":"Arbin BT2043","d":"12채널 독립. 켈빈 4선식. ±20A/0~5V."},
            {"i":"🌡️","t":"환경 챔버","d":"−45°C~190°C 정밀 제어. 모든 테스트 챔버 내 수행."},
            {"i":"📊","t":"데이터 수집","d":"전압·전류·온도·시간 동기 기록."},
            {"i":"🔋","t":"셀 준비","d":"25Ah NMC 파우치 셀. 초기 용량 측정 후 실험 시작."}],
     "eqs":[{"t":"아레니우스 의존성","c":"R(T) ∝ exp(Ea / (k_B·T))"}],
     "comp":{"h":["장비","사양","용도"],"r":[["Arbin BT2043","12ch독립,±20A","충방전"],["환경 챔버","−45~190°C","온도 제어"]]},
     "refs":[("Plett 2015 pp.65-67","")]},

    {"id":"t10","num":"10","title":"OCV 관계 실험실 테스트","sub":"4-스크립트 OCV 취득법","tags":["4-스크립트","C/30","GITT"],
     "desc":"C/30 저속 방전으로 OCV(z,T) 룩업 테이블 완성.",
     "kps":[{"i":"1️⃣","t":"Script 1","d":"테스트 온도 T에서 C/30으로 v_min까지 방전."},
            {"i":"2️⃣","t":"Script 2","d":"25°C에서 C/30으로 SoC=0% 기준점 확인."},
            {"i":"3️⃣","t":"Script 3","d":"테스트 온도 T에서 C/30으로 v_max까지 충전."},
            {"i":"4️⃣","t":"Script 4","d":"25°C에서 SoC=100% 기준점 확인."}],
     "eqs":[{"t":"온도 보정 OCV","c":"[OCV₀; OCVrel] = [1,T₁;1,T₂;…]⁺ · OCV_meas"}],
     "comp":{"h":["절차","온도","목적"],"r":[["Script 1","테스트 T","방전 OCV"],["Script 2","25°C","기준점 확인"],["Script 3","테스트 T","충전 OCV"],["Script 4","25°C","기준점 확인"]]},
     "refs":[("Weppner 1977","10.1149/1.2133152")]},

    {"id":"t11","num":"11","title":"동적 관계 실험실 테스트","sub":"UDDS 프로파일 파라미터 추출","tags":["UDDS","시스템식별","γ"],
     "desc":"UDDS 주행 사이클로 RC·히스테리시스 파라미터 추출.",
     "kps":[{"i":"🚗","t":"UDDS 프로파일","d":"도심 주행 패턴 모사 전류 프로파일."},
            {"i":"🔍","t":"γ 최적화","d":"γ=1~250 탐색 → RMSE 최소점. 교재 최적:γ≈90."},
            {"i":"📊","t":"부분공간 식별","d":"OCV 제거 후 잔류 전압으로 시스템 식별."},
            {"i":"🔄","t":"3-스크립트","d":"Script 1:OCV참조. Script 2:방전. Script 3:충전."}],
     "eqs":[{"t":"잔류 전압 (OCV 제거)","c":"ṽ[k] = v[k] − OCV(z[k],T[k])"}],
     "comp":{"h":["절차","내용"],"r":[["Script 1","완충 후 OCV 측정"],["Script 2","UDDS 방전"],["Script 3","UDDS 충전"]]},
     "refs":[("Seaman 2014","10.1016/j.jpowsour.2013.11.037")]},

    {"id":"t12","num":"12","title":"모델링 결과 예시","sub":"25Ah NMC UDDS 10시간 검증","tags":["RMSE","UDDS","NMC"],
     "desc":"RMSE=5.37mV 달성. 온도별 파라미터 특성 분석.",
     "kps":[{"i":"✅","t":"RMSE 5.37mV","d":"25Ah NMC, UDDS 10h. 교재 목표 충족."},
            {"i":"🌡️","t":"온도별","d":"R₀:기하급수적 감소. RC 시정수:비단조적 증가."},
            {"i":"📉","t":"히스테리시스","d":"온도 증가 시 히스테리시스 크기 감소."},
            {"i":"⚠️","t":"비단조 시정수","d":"τ가 온도 증가에 따라 비단조적으로 증가."}],
     "eqs":[{"t":"RMSE","c":"RMSE = √(1/N·Σ(v_meas[k]−v_model[k])²)\n// 교재: 5.37mV (25Ah NMC, UDDS 10h)"}],
     "comp":{"h":["모델","RMSE","SoC 오차"],"r":[["OCV만","~100mV","±10%"],["ESR","~50mV","±5%"],["1RC ESC","~10mV","±1~2%"],["DFN+ML","<2mV","±0.3%"]]},
     "refs":[("Lee 2014","10.1016/j.jpowsour.2013.12.127")]},

    {"id":"t13","num":"13","title":"결론 및 향후 방향","sub":"DFN+ML 하이브리드 차세대","tags":["한계","DFN","ML"],
     "desc":"ESC 한계와 물리 기반·ML 하이브리드 차세대 방향.",
     "kps":[{"i":"⚠️","t":"ESC 한계","d":"노화 예측 불가. 덴드라이트 임계점 예측 불가."},
            {"i":"🔬","t":"물리 기반 DFN","d":"Doyle-Fuller-Newman. 전극 내부 물리 기술. 높은 계산 비용."},
            {"i":"🤖","t":"ML 하이브리드","d":"ECM+LSTM. 목표 RMSE≤2mV."},
            {"i":"🔋","t":"차세대 BMS","d":"SoH 추정, 최적 충전, 덴드라이트 조기 감지."}],
     "eqs":[{"t":"하이브리드 목표","c":"v = f_ECM(x_k) + f_LSTM(h_k,i_k)\n목표: RMSE≤2mV, SoC±0.3%"}],
     "comp":{"h":["모델","RMSE","노화 예측","계산 비용"],"r":[["ESC","~10mV","불가","낮음"],["DFN","~3mV","가능","매우 높음"],["ECM+ML","~2mV","부분","높음"]]},
     "refs":[("Ng 2020","10.1038/s42256-020-0156-x")]},

    {"id":"t14","num":"14","title":"MATLAB ESC 모델 툴박스","sub":"simCell · processOCV · processDynamic","tags":["simCell","processOCV","MATLAB"],
     "desc":"ESCtoolbox 핵심 함수와 사용법. mocha-java.uccs.edu/BMS1/",
     "kps":[{"i":"💻","t":"simCell.m","d":"ESC 시뮬레이션. 전류 프로파일 → 모델 전압 출력."},
            {"i":"📊","t":"processOCV.m","d":"OCV 실험 데이터 처리. OCV₀, OCVrel 계산."},
            {"i":"🔧","t":"processDynamic.m","d":"동적 데이터 처리. R₀,R₁,C₁,γ,M,M₀ 추출."},
            {"i":"📁","t":"model 구조체","d":"모든 파라미터를 MATLAB struct로 저장."}],
     "eqs":[{"t":"simCell 사용 예시","c":"vest=simCell(current,25,dt,model,1,[0;0],0);\n// model.R0Param, RCParam, GParam..."}],
     "comp":{"h":["함수","입력","출력"],"r":[["processOCV","OCV 데이터","OCV₀,OCVrel"],["processDynamic","동적 데이터","R₀,R₁,C₁,γ,M,M₀"],["simCell","전류+model","전압 시뮬레이션"]]},
     "refs":[("Plett 2015 pp.82-87","")]},
]

# ── NEWS ─────────────────────────────────────────────────────
NEWS = [
    {"title":"[수요광장] 배터리 관리 시스템, 보안이 없으면 기능도 없다","source":"KR 전기신문","date":"2026-03-31","url":"https://www.electimes.com"},
    {"title":"[포커스] LG엔솔, 소프트웨어·서비스 중심 기업으로의 전략적 전환","source":"KR 투데이에너지","date":"2026-04-05","url":"https://www.todayenergy.kr"},
    {"title":"제주대 2025 초기창업패키지 — 전기차 배터리 AI 플랫폼 '퀀텀하이텍'","source":"KR 한경매거진","date":"2025-10-22","url":"https://magazine.hankyung.com"},
    {"title":"[2025년 딥테크 강소기업 탐방]〈4〉 휴컨 - 전자신문","source":"KR 전자신문","date":"2025-01-15","url":"https://www.etnews.com"},
]

# ── PAPERS ────────────────────────────────────────────────────
PAPERS = [
    {"idx":"01","tag":"교재","title":"Battery Management Systems, Vol.1: Battery Modeling","authors":"Gregory L. Plett","journal":"Artech House, 2015. ISBN: 978-1-60807-650-3","doi":"","url":"https://www.artechhouse.com","desc":"ESC 등가회로 모델의 표준 교재."},
    {"idx":"02","tag":"핵심 논문","title":"Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 1","authors":"G. L. Plett","journal":"Journal of Power Sources, 134(2), 252–261, 2004","doi":"10.1016/j.jpowsour.2004.02.031","url":"https://doi.org/10.1016/j.jpowsour.2004.02.031","desc":"ESC 모델과 EKF를 결합한 SoC 자가 교정 추정법의 원조 논문."},
    {"idx":"03","tag":"리뷰 논문","title":"A review of lithium-ion battery equivalent circuit models","authors":"X. Hu, S. Li, H. Peng","journal":"Journal of Power Sources, 198, 359–367, 2012","doi":"10.1016/j.jpowsour.2011.10.013","url":"https://doi.org/10.1016/j.jpowsour.2011.10.013","desc":"RC 등가회로 모델들의 비교 검토."},
    {"idx":"04","tag":"EIS 분석","title":"A survey of equivalent circuits for describing the electrical behavior of lithium-ion batteries","authors":"A. Seaman, T.-S. Dao, J. McPhee","journal":"Journal of Power Sources, 252, 395–405, 2014","doi":"10.1016/j.jpowsour.2013.11.037","url":"https://doi.org/10.1016/j.jpowsour.2013.11.037","desc":"EIS 임피던스 분석과 와버그 임피던스를 포함한 등가회로 파라미터 추출법."},
    {"idx":"05","tag":"히스테리시스","title":"The thermodynamic origin of hysteresis in insertion batteries","authors":"W. Dreyer et al.","journal":"Nature Materials, 9(5), 448–453, 2010","doi":"10.1038/nmat2718","url":"https://doi.org/10.1038/nmat2718","desc":"LFP 배터리 히스테리시스의 열역학적 기원."},
]

# ── QUIZ ─────────────────────────────────────────────────────
QUIZ = [
    {"q":"OCV를 측정할 때 전류를 0에 가깝게 유지해야 하는 이유는?","opts":["배터리 폭발 위험","R₀·i 강하와 RC 분극 없이 순수 평형 전압 측정","온도 측정 정확도","쿨롱 효율 향상"],"ans":1,"exp":"OCV는 순수 평형 전압. 전류가 흐르면 R₀·i 강하와 RC 분극이 추가됩니다.","f":"v=OCV(z)+ε | i→0이면 ε→0"},
    {"q":"이산시간 SoC 점화식에서 쿨롱 효율(η)의 일반적인 값은?","opts":["~70~80%","~85~90%","~95~98%","~99~99.9%"],"ans":3,"exp":"리튬이온 배터리의 쿨롱 효율은 99~99.9%로 매우 높습니다.","f":"η ≈ 0.999~1"},
    {"q":"교재 실험(Δi=5A)에서 R₀의 값은?","opts":["5.0 mΩ","8.2 mΩ","15.8 mΩ","38 mΩ"],"ans":1,"exp":"|ΔV₀|=41mV, Δi=5A → R₀=41mV/5A=8.2mΩ.","f":"R₀=|ΔV₀/Δi|=41mV÷5A=8.2mΩ"},
    {"q":"ZOH 속도계수 F₁의 물리적 의미는?","opts":["샘플링/시정수 비율","한 샘플 후 잔류 RC 전류 비율(0<F₁<1)","전류 이득","전압 분배 비율"],"ans":1,"exp":"F₁=exp(-Δt/τ)는 한 샘플 주기 후 RC 전류가 얼마나 남는지 나타냅니다.","f":"F₁=exp(−Δt/R₁C₁)"},
    {"q":"교재 실험에서 RC 시정수 τ는?","opts":["~60s (1분)","~600s (10분)","~2400s (40분)","~6000s (100분)"],"ans":1,"exp":"R₁=15.8mΩ, C₁=38kF → τ=0.0158×38000≈600s.","f":"τ=R₁×C₁≈600s | 4τ≈2400s"},
    {"q":"히스테리시스와 RC 확산 전압의 핵심 차이는?","opts":["히스테리시스가 항상 더 크다","히스테리시스는 시간이 지나도 소멸하지 않고 SoC 변화에만 의존","RC가 측정 더 어렵다","히스테리시스는 NMC에서 더 크다"],"ans":1,"exp":"RC 확산은 시간이 지나 소멸. 히스테리시스는 SoC 변화 시에만 변합니다.","f":"V_hys=M₀·s[k]+M·h[k]"},
    {"q":"ESC를 '자가 교정'이라 부르는 이유는?","opts":["파라미터가 자동 업데이트","i=0 휴지 시 전압이 OCV+히스테리시스로 자동 수렴","오류 시 재시작","온도 자동 대응"],"ans":1,"exp":"셀이 쉴 때 RC가 0으로 수렴해 모델 전압이 자동으로 평형값으로 돌아옵니다.","f":"i→0: v→OCV(z,T)+M₀·s+M·h"},
    {"q":"와버그 임피던스가 나이키스트에서 45°인 이유는?","opts":["전극 저항이 주파수 무관","Z_W=A_W/√(jω)에서 실수부=허수부","커패시턴스가 매우 큼","전해질 저항=0"],"ans":1,"exp":"Z_W=A_W/√(jω) → Re=Im → 위상각=45°.","f":"Z_W=A_W/√(jω) | |Z_re|=|Z_im| → 위상=45°"},
    {"q":"OCV 4-스크립트에서 Script 2·4를 25°C에서 수행하는 이유는?","opts":["장비 안전","잔류 용량으로 SoC 기준점(0%/100%) 정확히 설정","25°C에서만 측정 가능","챔버 에너지 절약"],"ans":1,"exp":"저/고온에서 전압 컷오프와 실제 완방전/완충이 다를 수 있어 25°C에서 확인합니다.","f":"Script1→Script2(25°C)→Script3→Script4(25°C)"},
    {"q":"ESC 모델의 근본적 한계는?","opts":["연산량 과다","현상론적 블랙박스로 노화·덴드라이트 화학적 현상 예측 불가","OCV 측정 불가","RC 추출 불가"],"ans":1,"exp":"ESC는 단기 예측에는 탁월하나 SEI 성장·장기 노화 예측은 불가합니다.","f":"차세대: ECM+DFN+LSTM → 목표 RMSE≤2mV"},
]

# ── CSS ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Roboto+Mono:wght@400;500&display=swap');

html,body,[class*="css"],.stApp {{
    font-family:'Noto Sans KR',sans-serif!important;
    background:{BG}!important; color:{NAVY}!important;
}}
#MainMenu,footer,.stDeployButton,[data-testid="stToolbar"],[data-testid="stHeader"]{{display:none!important;}}

/* NAV */
.rn-nav{{
    position:fixed;top:0;left:0;right:0;z-index:9999;
    background:rgba(255,255,255,.97);
    backdrop-filter:blur(14px);
    border-bottom:1px solid {BD};
    display:flex;align-items:center;justify-content:space-between;
    padding:0 56px;height:68px;
}}
.rn-logo{{display:flex;align-items:center;gap:10px;}}
.rn-logo-name{{font-size:15px;font-weight:700;color:{NAVY};letter-spacing:-.02em;}}
.rn-links{{display:flex;align-items:center;gap:40px;}}
.rn-link{{
    font-size:13px;font-weight:500;color:{GRAY};letter-spacing:.01em;
    cursor:pointer;padding:4px 0;border-bottom:2px solid transparent;
    transition:color .2s,border-color .2s;
}}
.rn-link:hover{{color:{TEAL};border-bottom-color:{TEAL};}}
.rn-right{{display:flex;align-items:center;gap:14px;font-size:12px;color:{LGRAY};}}
.rn-sep{{width:1px;height:18px;background:{BD};}}

/* HERO */
.rn-hero{{
    position:relative;overflow:hidden;
    min-height:100vh;display:flex;align-items:center;
}}
.rn-hero-ov{{
    position:absolute;inset:0;
    background:linear-gradient(135deg,rgba(7,14,24,.94) 0%,rgba(10,20,42,.88) 40%,rgba(12,26,55,.80) 70%,rgba(13,30,62,.72) 100%);
}}
.rn-hero-grid{{
    position:absolute;inset:0;
    background-image:linear-gradient(rgba(45,212,191,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(45,212,191,.04) 1px,transparent 1px);
    background-size:80px 80px;
}}
.rn-hero-body{{position:relative;z-index:2;padding:120px 80px 80px;max-width:720px;}}
.rn-eyebrow{{
    font-size:11px;letter-spacing:.22em;color:{TEAL};text-transform:uppercase;font-weight:500;
    display:flex;align-items:center;gap:14px;margin-bottom:30px;
}}
.rn-eyebrow::before{{content:'';display:inline-block;width:44px;height:1px;background:{TEAL};}}
.rn-h1{{font-size:clamp(52px,7vw,80px);font-weight:900;line-height:1.02;color:#fff;letter-spacing:-.035em;margin-bottom:0;}}
.rn-h1-teal{{color:{TEAL};display:block;}}
.rn-sub{{font-size:15px;color:rgba(255,255,255,.52);margin-top:26px;line-height:1.82;max-width:500px;font-weight:300;}}
.rn-scroll{{
    position:absolute;bottom:44px;right:56px;color:rgba(255,255,255,.22);font-size:10px;
    letter-spacing:.24em;text-transform:uppercase;writing-mode:vertical-rl;display:flex;align-items:center;gap:10px;
}}
.rn-scroll::after{{content:'';display:inline-block;width:1px;height:66px;background:linear-gradient(to bottom,rgba(255,255,255,.18),transparent);}}

/* WHY */
.rn-why{{padding:100px 80px;background:#fff;}}
.rn-why-grid{{display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;}}
.rn-why-img{{border-radius:6px;overflow:hidden;box-shadow:0 28px 60px rgba(0,0,0,.1);}}
.rn-why-title{{font-size:46px;font-weight:900;color:{NAVY};line-height:1.08;margin-bottom:38px;letter-spacing:-.035em;}}
.rn-why-item{{display:flex;gap:24px;align-items:flex-start;margin-bottom:32px;}}
.rn-why-num{{font-size:28px;font-weight:900;color:{TEAL};opacity:.45;min-width:44px;line-height:1.1;font-family:'Roboto Mono',monospace;}}
.rn-why-item-t{{font-size:15px;font-weight:700;color:{NAVY};margin-bottom:5px;}}
.rn-why-item-d{{font-size:13px;color:{GRAY};line-height:1.7;}}

/* TECH */
.rn-tech{{padding:80px 80px 0;background:{BG2};}}
.rn-tech-intro{{display:grid;grid-template-columns:1fr 1.8fr;gap:60px;margin-bottom:48px;align-items:start;}}
.rn-tech-title{{font-size:52px;font-weight:900;color:{NAVY};line-height:1.04;letter-spacing:-.035em;}}
.rn-tech-desc{{font-size:14px;color:{GRAY};line-height:1.8;padding-top:68px;}}

/* TOPIC CARD */
.rn-tc{{position:relative;overflow:hidden;border-radius:8px;}}
.rn-tc img{{width:100%;object-fit:cover;display:block;}}
.rn-tc-ov{{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.9) 0%,rgba(0,0,0,.4) 50%,transparent 100%);}}
.rn-tc-body{{position:absolute;bottom:0;left:0;right:0;padding:30px 36px;}}
.rn-tc-chip{{font-size:9px;letter-spacing:.22em;color:{TEAL};font-weight:700;text-transform:uppercase;margin-bottom:9px;font-family:'Roboto Mono',monospace;}}
.rn-tc-title{{font-size:24px;font-weight:800;color:#fff;margin-bottom:5px;letter-spacing:-.01em;}}
.rn-tc-sub{{font-size:12px;color:rgba(255,255,255,.46);margin-bottom:15px;}}
.rn-tc-more{{font-size:12px;color:{TEAL};font-weight:600;letter-spacing:.05em;}}

/* NEWSROOM — 1:1 비율 */
.rn-news{{padding:90px 80px;background:#fff;}}
.rn-news-title{{font-size:58px;font-weight:900;color:{NAVY};letter-spacing:-.035em;margin-bottom:0;}}
.rn-news-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:26px;margin-top:52px;}}
.rn-nc{{cursor:pointer;}}
.rn-nc-img{{
    width:100%;
    aspect-ratio:1/1;
    border-radius:5px;overflow:hidden;margin-bottom:16px;
}}
.rn-nc-img img{{width:100%;height:100%;object-fit:cover;transition:transform .4s;display:block;}}
.rn-nc:hover .rn-nc-img img{{transform:scale(1.05);}}
.rn-nc-date{{font-size:11px;color:{TEAL};font-weight:600;margin-bottom:8px;}}
.rn-nc-title{{font-size:14px;font-weight:700;color:{NAVY};line-height:1.5;margin-bottom:6px;}}
.rn-nc-src{{font-size:11px;color:{LGRAY};}}

/* PAPERS */
.rn-papers{{padding:80px 80px;background:{BG2};}}
.rn-paper-card{{background:#fff;border:1px solid {BD};border-radius:10px;padding:20px 24px;margin-bottom:12px;display:flex;gap:20px;align-items:flex-start;transition:border-color .15s,box-shadow .15s;}}
.rn-paper-card:hover{{border-color:{TEAL};box-shadow:0 4px 24px rgba(45,212,191,.08);}}
.rn-paper-num{{font-family:'Roboto Mono',monospace;font-size:12px;font-weight:700;color:{TEAL};min-width:28px;padding-top:2px;}}
.rn-paper-tag{{font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;display:inline-block;margin-bottom:6px;background:rgba(45,212,191,.1);color:{TEAL};border:1px solid rgba(45,212,191,.3);font-family:'Roboto Mono',monospace;letter-spacing:.06em;}}
.rn-paper-title{{font-size:14px;font-weight:700;color:{NAVY};margin-bottom:4px;line-height:1.45;}}
.rn-paper-authors{{font-size:12px;color:{GRAY};margin-bottom:3px;}}
.rn-paper-journal{{font-size:11px;color:{LGRAY};font-family:'Roboto Mono',monospace;margin-bottom:5px;}}
.rn-paper-desc{{font-size:12px;color:{GRAY};line-height:1.65;}}
.rn-paper-doi{{font-family:'Roboto Mono',monospace;font-size:10px;color:{TEAL};margin-top:5px;}}

/* FOOTER */
.rn-footer{{background:{NAVY};padding:44px 80px;display:flex;justify-content:space-between;align-items:center;}}
.rn-footer-logo{{font-size:15px;font-weight:700;color:#fff;}}
.rn-footer-copy{{font-size:11px;color:rgba(255,255,255,.3);font-family:'Roboto Mono',monospace;}}

/* SIDEBAR */
.sb-head{{background:linear-gradient(135deg,{TEAL},#0891b2);padding:13px 15px;border-radius:10px;margin-bottom:13px;}}
.sb-head-t{{font-size:13px;font-weight:700;color:#fff;}}
.sb-head-s{{font-size:10px;color:rgba(255,255,255,.68);margin-top:2px;}}
.sb-result{{background:rgba(45,212,191,.07);border:1px solid rgba(45,212,191,.2);border-radius:8px;padding:12px;margin-top:8px;}}
.sb-val{{font-family:'Roboto Mono',monospace;font-size:12px;color:{TEAL};line-height:2;}}
.sb-pb{{height:6px;background:{BD};border-radius:3px;overflow:hidden;}}
.sb-pb-fill{{height:100%;background:linear-gradient(90deg,{TEAL},#0891b2);border-radius:3px;transition:width .4s;}}

/* KP CARD */
.kp-card{{background:#f8fafc;border:1px solid {BD};border-left:3px solid {TEAL};border-radius:0 10px 10px 0;padding:13px;margin-bottom:10px;}}
.kp-i{{font-size:20px;margin-bottom:4px;}}
.kp-t{{font-size:12px;font-weight:700;color:{TEAL};margin-bottom:3px;}}
.kp-d{{font-size:12px;color:{GRAY};line-height:1.6;}}

/* EQ BOX */
.eq-box{{background:#0f172a;border-radius:10px;padding:14px 18px;margin:8px 0;font-family:'Roboto Mono',monospace;font-size:12px;color:#7dd3fc;line-height:2;border-left:3px solid {TEAL};overflow-x:auto;}}

/* Streamlit 버튼 오버라이드 */
.stButton>button{{
    background:{TEAL}!important;color:{NAVY}!important;
    border:none!important;border-radius:6px!important;
    font-family:'Noto Sans KR',sans-serif!important;
    font-weight:700!important;font-size:13px!important;transition:all .2s!important;
}}
.stButton>button:hover{{background:#14b8a6!important;box-shadow:0 4px 16px rgba(45,212,191,.3)!important;transform:translateY(-1px)!important;}}
[data-testid="metric-container"]{{background:#fff!important;border:1px solid {BD}!important;border-radius:10px!important;border-left:3px solid {TEAL}!important;padding:13px!important;}}
[data-testid="stExpander"]{{border:1px solid {BD}!important;border-radius:10px!important;}}
[data-baseweb="tab"][aria-selected="true"]{{color:{TEAL}!important;}}
[data-baseweb="tab-highlight"]{{background-color:{TEAL}!important;}}

/* 섹션 앵커 */
.section-anchor{{scroll-margin-top:80px;}}
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-head">
        <div class="sb-head-t">🧮 ECM 파라미터 계산기</div>
        <div class="sb-head-s">RC 파라미터 즉시 계산</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚡ RC 파라미터 계산", expanded=True):
        r1 = st.number_input("R₁ (mΩ)", 0.1, 1000.0, 15.8, 0.1, key="w_r1")
        c1 = st.number_input("C₁ (F)",  1.0, 1e6, 38000.0, 100.0, key="w_c1")
        r0 = st.number_input("R₀ (mΩ)", 0.1, 1000.0, 8.2, 0.1, key="w_r0")
        di = st.number_input("Δi (A)",  0.1, 1000.0, 5.0, 0.5, key="w_di")
        if st.button("🔢 계산하기", key="w_calc_btn", use_container_width=True):
            tau = (r1/1000)*c1; dv0=r0*di; dvI=(r0+r1)*di; f1=math.exp(-1/tau) if tau>0 else 0
            st.markdown(f"""
            <div class="sb-result">
            <div class="sb-val">
                τ = <b>{tau:.1f} s</b> ({tau/60:.1f}분)<br>
                4τ = <b>{4*tau:.0f} s</b> ({4*tau/60:.1f}분)<br>
                ΔV₀ = <b>{dv0:.2f} mV</b><br>
                ΔV∞ = <b>{dvI:.2f} mV</b><br>
                F₁ = <b>{f1:.6f}</b>
            </div></div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="font-size:12px;font-weight:700;color:{NAVY};margin-bottom:6px;">📝 메모장</div>', unsafe_allow_html=True)
    memo_val = st.text_area("메모", value=gs("_ss_memo"), height=100, key="w_memo_ta", label_visibility="collapsed")
    mbc1, mbc2 = st.columns(2)
    with mbc1:
        if st.button("💾 저장", key="w_memo_save", use_container_width=True):
            ss("_ss_memo", memo_val); st.toast("저장됨!")
    with mbc2:
        if st.button("🗑 지우기", key="w_memo_clr", use_container_width=True):
            ss("_ss_memo", ""); st.rerun()

    st.markdown("---")
    done_cnt = sum(1 for v in gs("_ss_progress").values() if v)
    st.markdown(f"""
    <div style="font-size:12px;font-weight:700;color:{NAVY};margin-bottom:6px;">
        📈 학습 진도 <span style="color:{TEAL};">{done_cnt}/{len(TOPICS)}</span>
    </div>
    <div class="sb-pb"><div class="sb-pb-fill" style="width:{done_cnt/len(TOPICS)*100:.0f}%;"></div></div>
    <div style="font-size:10px;color:{LGRAY};margin-top:4px;">섹션 카드를 열면 자동 저장됩니다</div>
    """, unsafe_allow_html=True)
    dc = st.columns(7)
    for di2, tp in enumerate(TOPICS):
        with dc[di2 % 7]:
            c_dot = TEAL if gs("_ss_progress").get(tp["id"], False) else BD
            st.markdown(f'<div style="height:4px;border-radius:2px;background:{c_dot};margin-top:6px;" title="{tp["title"]}"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f'<div style="font-size:11px;font-weight:600;color:{NAVY};margin-bottom:5px;">🔗 관련 자료</div>', unsafe_allow_html=True)
    st.markdown("[📦 ESCtoolbox](http://mocha-java.uccs.edu/BMS1/)")
    st.markdown("[📄 Plett 2004](https://doi.org/10.1016/j.jpowsour.2004.02.031)")

# ── 상단 NAV HTML (표시용) ──────────────────────────────────
st.markdown(f"""
<div class="rn-nav" id="top-nav">
    <div class="rn-logo">
        <img src="data:image/png;base64,{LOGO}" style="width:30px;height:30px;border-radius:8px;">
        <span class="rn-logo-name">ECM 연구포털</span>
    </div>
    <div class="rn-links">
        <span class="rn-link" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">🏠 홈</span>
        <span class="rn-link" id="nav-overview" onclick="document.getElementById('sec-overview') && document.getElementById('sec-overview').scrollIntoView({{behavior:'smooth'}})">연구 개요</span>
        <span class="rn-link" id="nav-tech" onclick="document.getElementById('sec-tech') && document.getElementById('sec-tech').scrollIntoView({{behavior:'smooth'}})">핵심 기술</span>
        <span class="rn-link" id="nav-news" onclick="document.getElementById('sec-news') && document.getElementById('sec-news').scrollIntoView({{behavior:'smooth'}})">뉴스룸</span>
        <span class="rn-link" id="nav-topics" onclick="document.getElementById('sec-topics') && document.getElementById('sec-topics').scrollIntoView({{behavior:'smooth'}})">14개 주제</span>
    </div>
    <div class="rn-right">
        <span>Plett · Ch 2</span>
        <div class="rn-sep"></div>
        <span>🔖 {len(gs("_ss_bookmarks"))}건</span>
    </div>
</div>
<div style="height:68px;"></div>
""", unsafe_allow_html=True)

# ── 네비게이션 버튼 ──────────────────────────────────────────
nav_cols = st.columns([1,1,1,1,1,1,0.45,0.45,0.6])
nav_pages = [
    ("home",      "🏠 홈"),
    ("topics",    "📖 주제별 학습"),
    ("equations", "🔢 핵심 수식"),
    ("quiz",      "📝 퀴즈"),
    ("bookmarks", "🔖 북마크"),
    ("notices",   "📢 공지사항"),
]
for ci, (pg_key, pg_label) in enumerate(nav_pages):
    with nav_cols[ci]:
        if st.button(pg_label, key=f"w_nav_{pg_key}", use_container_width=True):
            ss("_ss_page", pg_key); st.rerun()

with nav_cols[-3]:
    dm_label = "☀️" if gs("_ss_dark") else "🌙"
    if st.button(dm_label, key="w_btn_dark", use_container_width=True):
        ss("_ss_dark", not gs("_ss_dark")); st.rerun()
with nav_cols[-2]:
    lang_label = "🌐 EN" if gs("_ss_lang")=="ko" else "🌐 KO"
    if st.button(lang_label, key="w_btn_lang", use_container_width=True):
        ss("_ss_lang", "en" if gs("_ss_lang")=="ko" else "ko"); st.rerun()
with nav_cols[-1]:
    if st.button("🖨 PDF", key="w_btn_pdf", use_container_width=True):
        st.toast("브라우저 Ctrl+P (Mac: Cmd+P) 로 PDF 저장하세요.")

st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

# ── 플롯 헬퍼 ─────────────────────────────────────────────────
def plot_lyt(**kw):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR", color=GRAY, size=11),
        margin=dict(l=40,r=20,t=36,b=36), height=280,
        legend=dict(orientation="h",y=-0.24),
        xaxis=dict(gridcolor=BD, color=LGRAY, zerolinecolor=BD),
        yaxis=dict(gridcolor=BD, color=LGRAY, zerolinecolor=BD),
    )
    base.update(kw); return base

# ═══════════════════════════════════════════════════════════════
#  페이지 라우팅
# ═══════════════════════════════════════════════════════════════
page = gs("_ss_page")

# ── HOME ─────────────────────────────────────────────────────
if page == "home":

    # HERO
    st.markdown(f"""
    <div class="rn-hero" id="sec-home">
        <img src="data:image/png;base64,{HERO}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0.5;">
        <div class="rn-hero-ov"></div>
        <div class="rn-hero-grid"></div>
        <div class="rn-hero-body">
            <div class="rn-eyebrow">Battery Management Systems · Chapter 2-04</div>
            <div class="rn-h1">
                배터리
                <span class="rn-h1-teal">등가회로 모델</span>
                연구 포털
            </div>
            <div class="rn-sub">
                Battery Equivalent Circuit Model(ECM) 연구는<br>
                전기차와 에너지 저장 시스템의 정밀한 상태 추정을<br>
                위한 핵심 기술입니다.
            </div>
        </div>
        <div class="rn-scroll">SCROLL</div>
    </div>
    """, unsafe_allow_html=True)

    # 연구 개요 섹션
    st.markdown(f"""
    <div class="rn-why section-anchor" id="sec-overview">
        <div class="rn-eyebrow">왜 배터리 등가회로 모델인가</div>
        <div class="rn-why-grid">
            <div>
                <div class="rn-why-img">
                    <img src="data:image/png;base64,{WHY}" style="width:100%;height:460px;object-fit:cover;display:block;">
                </div>
            </div>
            <div>
                <div class="rn-why-title">배터리 등가회로<br>핵심 기술</div>
                <div>
                    <div class="rn-why-item">
                        <div class="rn-why-num">01</div>
                        <div>
                            <div class="rn-why-item-t">정밀 SoC 추정</div>
                            <div class="rn-why-item-d">OCV·RC·히스테리시스 통합 ESC 모델로 SoC 추정 오차를 ±1% 이하로 줄입니다.</div>
                        </div>
                    </div>
                    <div class="rn-why-item">
                        <div class="rn-why-num">02</div>
                        <div>
                            <div class="rn-why-item-t">실시간 EKF 자가 교정</div>
                            <div class="rn-why-item-d">확장 칼만 필터와 ESC 모델을 결합해 센서 노이즈 속에서도 SoC를 자동 교정합니다.</div>
                        </div>
                    </div>
                    <div class="rn-why-item">
                        <div class="rn-why-num">03</div>
                        <div>
                            <div class="rn-why-item-t">MCU 실시간 구현</div>
                            <div class="rn-why-item-d">ZOH 이산화로 연속 ODE를 정확하게 이산화해 마이크로컨트롤러에서 실시간으로 동작합니다.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 핵심 기술 섹션
    st.markdown(f"""
    <div class="rn-tech section-anchor" id="sec-tech">
        <div class="rn-eyebrow">주요 기술</div>
        <div class="rn-tech-intro">
            <div class="rn-tech-title">배터리 등가회로<br>핵심 기술</div>
            <div class="rn-tech-desc">
                OCV부터 ESC 완성 모델까지 — 14가지 핵심 기술을 탐색하세요.<br>
                아래 카드를 클릭하면 관련 수식과 논문을 바로 확인할 수 있습니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2열 카드 (TOPIC 01 & 07) — 버튼 클릭 → topics 페이지로 이동
    col_l, col_r = st.columns(2, gap="small")
    for col_idx, tp_idx in enumerate([0, 6]):
        tp = TOPICS[tp_idx]
        card_bg = make_topic_bg(tp_idx)
        col = col_l if col_idx == 0 else col_r
        with col:
            if st.button(
                f"자세히 보기 → ({tp['title']})",
                key=f"w_tech_card_{tp['id']}",
                use_container_width=True
            ):
                ss("_ss_topic", tp["id"])
                ss("_ss_page", "topics")
                st.rerun()
            st.markdown(f"""
            <div class="rn-tc" style="height:400px;margin-top:-46px;margin-bottom:4px;pointer-events:none;">
                <img src="data:image/png;base64,{card_bg}" style="height:400px;width:100%;object-fit:cover;">
                <div class="rn-tc-ov"></div>
                <div class="rn-tc-body">
                    <div class="rn-tc-chip">TOPIC {tp['num']}</div>
                    <div class="rn-tc-title">{tp['title']}</div>
                    <div class="rn-tc-sub">{tp['sub']}</div>
                    <div class="rn-tc-more">자세히 보기 →</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 14개 주제 바로가기 버튼 (섹션 앵커)
    st.markdown(f"""
    <div class="section-anchor" id="sec-topics" style="padding:60px 80px 30px;background:{BG2};">
        <div class="rn-eyebrow">전체 학습 목록</div>
        <div style="font-size:42px;font-weight:900;color:{NAVY};letter-spacing:-.035em;margin-bottom:32px;">14개 주제 전체 보기</div>
    </div>
    """, unsafe_allow_html=True)

    tc_grid = st.columns(4)
    for ti, tp in enumerate(TOPICS):
        with tc_grid[ti % 4]:
            done_tp = gs("_ss_progress").get(tp["id"], False)
            if st.button(
                f"{'✅' if done_tp else '📖'} {tp['num']}. {tp['title']}",
                key=f"w_home_topic_{tp['id']}",
                use_container_width=True
            ):
                ss("_ss_topic", tp["id"])
                ss("_ss_page", "topics")
                st.rerun()

    # 뉴스룸 섹션
    st.markdown(f"""
    <div class="rn-news section-anchor" id="sec-news">
        <div class="rn-eyebrow">최신 뉴스</div>
        <div class="rn-news-title">뉴스룸</div>
        <div class="rn-news-grid">
    """, unsafe_allow_html=True)

    for ni, news in enumerate(NEWS):
        nb64 = make_news_img(ni)
        st.markdown(f"""
            <a href="{news['url']}" target="_blank" style="text-decoration:none;">
            <div class="rn-nc">
                <div class="rn-nc-img">
                    <img src="data:image/png;base64,{nb64}" alt="뉴스 이미지">
                </div>
                <div class="rn-nc-date">{news['date']}</div>
                <div class="rn-nc-title">{news['title']}</div>
                <div class="rn-nc-src">{news['source']}</div>
            </div>
            </a>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # PAPERS
    st.markdown(f"""
    <div class="rn-papers">
        <div class="rn-eyebrow">학술 논문 &amp; 참고문헌</div>
        <div style="font-size:50px;font-weight:900;color:{NAVY};letter-spacing:-.035em;margin-bottom:36px;">
            논문 &amp; 참고문헌
        </div>
    </div>
    """, unsafe_allow_html=True)

    for p in PAPERS:
        doi_link = (f'<a href="{p["url"]}" target="_blank" class="rn-paper-doi">DOI: {p["doi"]} ↗</a>'
                    if p["doi"] else
                    f'<a href="{p["url"]}" target="_blank" class="rn-paper-doi">바로가기 ↗</a>')
        st.markdown(f"""
        <div class="rn-paper-card" style="margin:0 0 12px;">
            <div class="rn-paper-num">{p['idx']}</div>
            <div style="flex:1;">
                <span class="rn-paper-tag">{p['tag']}</span>
                <div class="rn-paper-title">{p['title']}</div>
                <div class="rn-paper-authors">{p['authors']}</div>
                <div class="rn-paper-journal">{p['journal']}</div>
                <div class="rn-paper-desc">{p['desc']}</div>
                {doi_link}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # FOOTER
    st.markdown(f"""
    <div style="height:60px;"></div>
    <div class="rn-footer">
        <div class="rn-footer-logo">🔋 ECM 등가회로 모델 연구포털</div>
        <div class="rn-footer-copy">© 2026 · Plett(2015) BMS Vol.1 Ch.02 · Streamlit</div>
    </div>
    """, unsafe_allow_html=True)

# ── TOPICS ────────────────────────────────────────────────────
elif page == "topics":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};letter-spacing:-.03em;margin-bottom:18px;">📖 주제별 학습 — 14개 섹션</div>', unsafe_allow_html=True)

    tnames = [f"Section {tp['num']}: {tp['title']}" for tp in TOPICS]
    cur_id = gs("_ss_topic")
    si = next((ti for ti, tp in enumerate(TOPICS) if tp["id"] == cur_id), 0)

    sname = st.selectbox("섹션 선택", tnames, index=si, key="w_tsel")
    si = tnames.index(sname)
    tp = TOPICS[si]

    # 진도 자동 저장
    prog = gs("_ss_progress"); prog[tp["id"]] = True; ss("_ss_progress", prog)

    card_bg = make_topic_bg(si)
    tags_h = " ".join([
        f'<span style="background:rgba(45,212,191,.1);color:{TEAL};border:1px solid rgba(45,212,191,.3);border-radius:20px;padding:2px 9px;font-size:10px;font-weight:700;">{t}</span>'
        for t in tp["tags"]
    ])
    bm_list = gs("_ss_bookmarks")
    bm_label = "★ 저장됨" if tp["id"] in bm_list else "☆ 북마크"

    th, tbm = st.columns([5, 1])
    with th:
        st.markdown(f"""
        <div style="position:relative;border-radius:12px;overflow:hidden;margin-bottom:14px;">
            <img src="data:image/png;base64,{card_bg}" style="width:100%;height:140px;object-fit:cover;display:block;">
            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(7,14,24,.92),rgba(12,26,55,.78));display:flex;flex-direction:column;justify-content:flex-end;padding:16px 20px;">
                <div style="font-family:'Roboto Mono',monospace;font-size:9px;color:rgba(45,212,191,.9);letter-spacing:.18em;margin-bottom:6px;">SECTION {tp['num']}</div>
                <div style="font-size:20px;font-weight:900;color:#fff;margin-bottom:7px;">{tp['title']}</div>
                <div>{tags_h}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with tbm:
        if st.button(bm_label, key=f"w_bm_{tp['id']}", use_container_width=True):
            bm = gs("_ss_bookmarks")
            if tp["id"] in bm: bm.remove(tp["id"])
            else: bm.append(tp["id"])
            ss("_ss_bookmarks", bm); st.rerun()

    tabs = st.tabs(["📖 개념 설명","🔢 핵심 수식","📊 AI 그래프","📋 비교 분석","📄 참고문헌"])

    with tabs[0]:
        kc = st.columns(2)
        for ki, kp in enumerate(tp["kps"]):
            with kc[ki % 2]:
                st.markdown(f'<div class="kp-card"><div class="kp-i">{kp["i"]}</div><div class="kp-t">{kp["t"]}</div><div class="kp-d">{kp["d"]}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**{tp['title']}** — {tp['desc']}")

    with tabs[1]:
        for eq in tp["eqs"]:
            st.markdown(f"**{eq['t']}**")
            st.markdown(f'<div class="eq-box">{eq["c"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

    with tabs[2]:
        fig = None
        if tp["id"] == "t01":
            sx = [i/10 for i in range(11)]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sx,y=[3.0,3.40,3.65,3.75,3.82,3.89,3.97,4.05,4.12,4.18,4.20],name="NMC",line=dict(color=TEAL,width=2.5)))
            fig.add_trace(go.Scatter(x=sx,y=[2.8,3.20,3.30,3.32,3.33,3.33,3.34,3.35,3.36,3.50,3.65],name="LFP",line=dict(color="#60a5fa",width=2.5,dash="dash")))
            fig.update_layout(**plot_lyt(title="OCV vs SoC",xaxis_title="SoC",yaxis_title="OCV (V)"))
        elif tp["id"] == "t02":
            zk = [1.0]; Q=25.0; eta=0.999; dt=1.0; I=5.0
            for _ in range(200): zk.append(max(0, zk[-1] - (dt/3600/Q)*eta*I))
            fig=go.Figure(); fig.add_trace(go.Scatter(x=list(range(201)),y=zk,name="SoC",line=dict(color=TEAL,width=2.5)))
            fig.update_layout(**plot_lyt(title="SoC 감소 (I=5A, Q=25Ah)",xaxis_title="시간(s)",yaxis_title="SoC"))
        elif tp["id"] in ["t03","t05"]:
            curr = [0]*5 + [5]*30 + [0]*20
            v = [4.1 - c*0.0082 for c in curr]
            fig=go.Figure()
            fig.add_trace(go.Scatter(y=[4.1]*len(curr),name="OCV",line=dict(color="#ef4444",dash="dash",width=1.5)))
            fig.add_trace(go.Scatter(y=v,name="V(t)",line=dict(color=TEAL,width=2.5)))
            fig.update_layout(**plot_lyt(title="R₀ 순간 전압 강하",xaxis_title="시간(s)",yaxis_title="전압(V)"))
        elif tp["id"] == "t04":
            t_rc=list(range(81)); irc=0.0; vo,oc=[],[]
            for tt in t_rc:
                oc.append(4.1)
                if tt<5: vo.append(4.1); irc=0.0
                else:
                    F=math.exp(-1/(0.0158*38000)); irc=F*irc+(1-F)*5.0
                    vo.append(4.1-0.0158*irc-0.0082*5.0)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=t_rc,y=oc,name="OCV",line=dict(color="#ef4444",dash="dash",width=1.5)))
            fig.add_trace(go.Scatter(x=t_rc,y=vo,name="V(t)",fill="tonexty",fillcolor="rgba(45,212,191,.06)",line=dict(color=TEAL,width=2.5)))
            fig.update_layout(**plot_lyt(title="RC 확산 전압 응답 (I=5A)",xaxis_title="시간(s)",yaxis_title="전압(V)"))
        elif tp["id"] == "t06":
            omega=np.logspace(4,-4,400); rez,imz=[],[]
            for w in omega:
                jw=complex(0,w)
                Z=0.0082+0.0158/(1+jw*0.0158*38000)+0.002/(complex(0,1)**0.5*w**0.5)
                rez.append(Z.real*1000); imz.append(-Z.imag*1000)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=rez,y=imz,mode="lines",name="임피던스",line=dict(color=TEAL,width=2.5)))
            fig.update_layout(**plot_lyt(title="나이키스트 플롯 (EIS)",xaxis_title="Re(Z) mΩ",yaxis_title="-Im(Z) mΩ"))
        elif tp["id"] == "t07":
            sh2=np.linspace(0,1,11)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(sh2),y=[2.8,3.3,3.34,3.35,3.36,3.37,3.38,3.40,3.45,3.5,3.65],name="충전 OCV",line=dict(color=TEAL,width=2.5)))
            fig.add_trace(go.Scatter(x=list(sh2),y=[2.8,3.2,3.27,3.28,3.29,3.30,3.31,3.33,3.38,3.44,3.60],name="방전 OCV",line=dict(color="#60a5fa",width=2.5,dash="dash")))
            fig.update_layout(**plot_lyt(title="히스테리시스 루프 (LFP)",xaxis_title="SoC",yaxis_title="OCV(V)"))
        elif tp["id"] == "t08":
            meas=[3.82,3.74,3.69,3.75,3.71,3.66,3.70,3.73,3.68,3.65,3.70]
            modl=[3.822,3.742,3.692,3.752,3.712,3.662,3.702,3.732,3.682,3.652,3.702]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(range(11)),y=meas,name="실측",mode="lines+markers",line=dict(color=LGRAY,dash="dot",width=2),marker=dict(size=5)))
            fig.add_trace(go.Scatter(x=list(range(11)),y=modl,name="ESC 모델",line=dict(color=TEAL,width=2.5)))
            fig.add_annotation(x=5,y=3.69,text="RMSE=5.37mV ✓",bgcolor="#dcfce7",bordercolor="#86efac",font=dict(color="#166534",size=11))
            fig.update_layout(**plot_lyt(title="ESC 검증: 모델 vs 실측 (UDDS)",xaxis_title="시간→",yaxis_title="V(V)"))
        elif tp["id"] == "t12":
            temps = [-20,-10,0,10,25,35,45]
            r0_vals = [0.042,0.028,0.018,0.013,0.0082,0.007,0.006]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=temps,y=r0_vals,name="R₀(T)",mode="lines+markers",line=dict(color=TEAL,width=2.5),marker=dict(size=7)))
            fig.update_layout(**plot_lyt(title="R₀ 온도 의존성",xaxis_title="온도(°C)",yaxis_title="R₀ (Ω)"))

        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("이 섹션의 그래프는 핵심 수식 탭의 시뮬레이터로 확인하세요.")

    with tabs[3]:
        comp = tp.get("comp")
        if comp:
            st.dataframe(pd.DataFrame(comp["r"], columns=comp["h"]), use_container_width=True, hide_index=True)
        else:
            st.info("비교 표가 없습니다.")

    with tabs[4]:
        for lbl, doi in tp.get("refs", []):
            doi_url = f"https://doi.org/{doi}" if doi else ""
            st.markdown(f"""
            <div style="background:{BG2};border-left:3px solid {TEAL};border-radius:0 8px 8px 0;padding:12px 14px;margin-bottom:9px;">
                <div style="font-family:'Roboto Mono',monospace;font-size:9px;font-weight:700;color:{TEAL};margin-bottom:4px;">{lbl}</div>
                {"<a href='"+doi_url+"' target='_blank' style='font-family:Roboto Mono,monospace;font-size:11px;color:"+TEAL+";'>DOI: "+doi+" ↗</a>" if doi else "<span style='color:"+LGRAY+";font-size:12px;'>교재 내 참고</span>"}
            </div>
            """, unsafe_allow_html=True)

    pp_col, pn_col = st.columns(2)
    with pp_col:
        if si > 0 and st.button(f"← {TOPICS[si-1]['title']}", key="w_prev_topic", use_container_width=True):
            ss("_ss_topic", TOPICS[si-1]["id"]); st.rerun()
    with pn_col:
        if si < len(TOPICS)-1 and st.button(f"{TOPICS[si+1]['title']} →", key="w_next_topic", use_container_width=True):
            ss("_ss_topic", TOPICS[si+1]["id"]); st.rerun()

    with st.expander("🗂 전체 14개 주제 목록"):
        ac = st.columns(4)
        for ti2, t2 in enumerate(TOPICS):
            with ac[ti2 % 4]:
                done2 = gs("_ss_progress").get(t2["id"], False)
                if st.button(f"{'✅' if done2 else '⬜'} {t2['num']}. {t2['title']}", key=f"w_all_{t2['id']}", use_container_width=True):
                    ss("_ss_topic", t2["id"]); st.rerun()

# ── EQUATIONS ─────────────────────────────────────────────────
elif page == "equations":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:18px;">🔢 핵심 수식 모음</div>', unsafe_allow_html=True)
    EQ_LIST = [
        {"n":"식 2.1","lc":TEAL,       "t":"SoC 연속시간",    "c":"ż(t) = −η(t)·i(t) / Q"},
        {"n":"식 2.4","lc":"#60a5fa",  "t":"SoC 이산시간",    "c":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"},
        {"n":"식 2.8","lc":"#34d399",  "t":"RC 이산화 (ZOH)", "c":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)"},
        {"n":"ESC 출력","lc":"#fbbf24","t":"ESC 단자 전압",    "c":"v[k] = OCV(z,T) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]"},
        {"n":"히스테리시스","lc":"#a78bfa","t":"동적 히스테리시스","c":"h[k+1] = exp(−|η·i·γ·Δt/Q|)·h[k]\n       − (1−exp(···))·sgn(i[k])"},
        {"n":"OCV 온도","lc":"#f87171","t":"OCV 온도 보정",    "c":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)"},
    ]
    ec = st.columns(2)
    for ei, eq in enumerate(EQ_LIST):
        with ec[ei % 2]:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid {BD};border-left:4px solid {eq['lc']};border-radius:10px;padding:16px;margin-bottom:14px;">
                <div style="font-family:'Roboto Mono',monospace;font-size:9px;font-weight:700;color:{eq['lc']};letter-spacing:.12em;margin-bottom:5px;">{eq['n']}</div>
                <div style="font-size:14px;font-weight:700;color:{NAVY};margin-bottom:8px;">{eq['t']}</div>
                <div class="eq-box">{eq['c'].replace(chr(10),"<br>")}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="font-size:18px;font-weight:700;color:{NAVY};margin-bottom:12px;">📊 전압 응답 시뮬레이터</div>', unsafe_allow_html=True)
    es1, es2 = st.columns([1, 1.5])
    with es1:
        sI  = st.slider("방전 전류 I (A)",  1.0, 100.0, 20.0, 1.0,  key="w_eI")
        sR0 = st.slider("R₀ (mΩ)",          1.0,  50.0,  8.2, 0.1,  key="w_eR0")
        sR1 = st.slider("R₁ (mΩ)",          1.0,  50.0, 15.8, 0.1,  key="w_eR1")
        sC1 = st.slider("C₁ (kF)",          1.0, 100.0, 38.0, 1.0,  key="w_eC1")
        tau_e = (sR1/1000)*(sC1*1000)
        st.info(f"τ = {tau_e:.0f} s | 4τ = {4*tau_e:.0f} s ({4*tau_e/60:.1f}분)")
    with es2:
        ts2 = list(range(81)); irc2=0.0; vs2,oc2=[],[]
        for tt in ts2:
            oc2.append(4.1)
            if tt<5: vs2.append(4.1); irc2=0.0
            else:
                F=math.exp(-1/((sR1/1000)*(sC1*1000))); irc2=F*irc2+(1-F)*sI
                vs2.append(4.1-(sR1/1000)*irc2-(sR0/1000)*sI)
        fg2=go.Figure()
        fg2.add_trace(go.Scatter(x=ts2,y=oc2,name="OCV",line=dict(color="#ef4444",dash="dash",width=1.5)))
        fg2.add_trace(go.Scatter(x=ts2,y=vs2,name="V(t)",fill="tonexty",fillcolor="rgba(45,212,191,.06)",line=dict(color=TEAL,width=2.5)))
        fg2.update_layout(**plot_lyt(title=f"V(t) | I={sI}A τ={tau_e:.0f}s",xaxis_title="시간(s)",yaxis_title="전압(V)"))
        st.plotly_chart(fg2, use_container_width=True)

# ── QUIZ ──────────────────────────────────────────────────────
elif page == "quiz":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:18px;">📝 이해도 퀴즈</div>', unsafe_allow_html=True)
    if st.button("🔄 다시 시작", key="w_quiz_reset"):
        ss("_ss_quiz_idx",0); ss("_ss_quiz_score",0)
        ss("_ss_quiz_ans",False); ss("_ss_quiz_done",False); ss("_ss_quiz_sel",-1); st.rerun()

    if gs("_ss_quiz_done"):
        pct = int(gs("_ss_quiz_score")/len(QUIZ)*100)
        msg = ("🏆 완벽! 배터리 모델링 마스터!" if pct==100
               else "👍 훌륭합니다!" if pct>=70
               else "📚 조금 더 복습해보세요.")
        st.markdown(f"""
        <div style="background:rgba(45,212,191,.07);border:1px solid rgba(45,212,191,.3);border-radius:16px;padding:40px;text-align:center;margin:20px 0;">
            <div style="font-size:52px;margin-bottom:14px;">🎉</div>
            <div style="font-family:'Roboto Mono',monospace;font-size:48px;font-weight:800;color:{TEAL};">
                {gs("_ss_quiz_score")} / {len(QUIZ)}
            </div>
            <div style="font-size:16px;color:{GRAY};margin-top:12px;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        idx = gs("_ss_quiz_idx")
        if idx >= len(QUIZ):
            ss("_ss_quiz_done", True); st.rerun()
        else:
            q = QUIZ[idx]
            st.progress(idx/len(QUIZ), text=f"문제 {idx+1}/{len(QUIZ)} · 점수: {gs('_ss_quiz_score')}점")
            st.markdown(f"### Q{idx+1}. {q['q']}")

            if not gs("_ss_quiz_ans"):
                for oi, opt in enumerate(q["opts"]):
                    if st.button(f"{chr(65+oi)}. {opt}", key=f"w_qopt_{idx}_{oi}", use_container_width=True):
                        ss("_ss_quiz_ans", True); ss("_ss_quiz_sel", oi)
                        if oi == q["ans"]:
                            ss("_ss_quiz_score", gs("_ss_quiz_score")+1)
                        st.rerun()
                if st.button("⏭ 건너뛰기", key=f"w_qskip_{idx}"):
                    ss("_ss_quiz_ans", True); ss("_ss_quiz_sel", -1); st.rerun()
            else:
                sel = gs("_ss_quiz_sel")
                for oi, opt in enumerate(q["opts"]):
                    lb = f"{chr(65+oi)}. {opt}"
                    if oi == q["ans"]:   st.success(f"✅ {lb}")
                    elif oi == sel:      st.error(f"❌ {lb}")
                    else:
                        st.markdown(f'<div style="padding:9px 12px;border:1px solid {BD};border-radius:7px;color:{GRAY};margin:3px 0;">{lb}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:rgba(45,212,191,.07);border-left:3px solid {TEAL};border-radius:0 8px 8px 0;padding:12px;margin:10px 0;">
                    <b>💡 해설:</b> {q['exp']}
                    <div class="eq-box" style="margin-top:8px;">{q['f']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("다음 문제 →", type="primary", use_container_width=True, key=f"w_qnext_{idx}"):
                    next_idx = idx + 1
                    ss("_ss_quiz_idx", next_idx); ss("_ss_quiz_ans", False); ss("_ss_quiz_sel", -1)
                    if next_idx >= len(QUIZ): ss("_ss_quiz_done", True)
                    st.rerun()

# ── BOOKMARKS ─────────────────────────────────────────────────
elif page == "bookmarks":
    bm_list = gs("_ss_bookmarks")
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:18px;">🔖 북마크 ({len(bm_list)}건)</div>', unsafe_allow_html=True)
    if not bm_list:
        st.info("북마크한 항목이 없습니다. 주제별 학습 페이지에서 ☆ 버튼을 눌러 추가하세요.")
    else:
        for bm_id in bm_list:
            tp_bm = next((t for t in TOPICS if t["id"]==bm_id), None)
            if tp_bm:
                b1, b2, b3 = st.columns([4,1,1])
                with b1:
                    st.markdown(f"**Section {tp_bm['num']}: {tp_bm['title']}** — {tp_bm['desc']}")
                with b2:
                    if st.button("열기", key=f"w_bm_open_{bm_id}", use_container_width=True):
                        ss("_ss_topic", bm_id); ss("_ss_page","topics"); st.rerun()
                with b3:
                    if st.button("삭제 ✕", key=f"w_bm_del_{bm_id}", use_container_width=True):
                        new_bm = [x for x in bm_list if x != bm_id]
                        ss("_ss_bookmarks", new_bm); st.rerun()
                st.markdown(f'<hr style="border-color:{BD};margin:8px 0;">', unsafe_allow_html=True)

# ── NOTICES ───────────────────────────────────────────────────
elif page == "notices":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:18px;">📢 공지사항</div>', unsafe_allow_html=True)
    nt = st.radio("", ["공지사항","업데이트","Q&A"], horizontal=True, key="w_ntab_sel", label_visibility="collapsed")
    st.markdown("---")
    for n in gs("_ss_notices"):
        ntype = n["type"]
        if nt=="공지사항" and ntype!="공지": continue
        if nt=="업데이트" and ntype!="업데이트": continue
        if nt=="Q&A"      and ntype!="Q&A": continue
        tc3 = "#1d4ed8" if ntype=="공지" else ("#166534" if ntype=="업데이트" else "#92400e")
        bc3 = "rgba(37,99,235,.07)" if ntype=="공지" else ("rgba(22,163,74,.07)" if ntype=="업데이트" else "rgba(245,158,11,.07)")
        st.markdown(f"""
        <div style="background:#fff;border:1px solid {BD};border-radius:10px;padding:14px 16px;margin-bottom:9px;">
            <span style="background:{bc3};color:{tc3};border:1px solid {tc3}33;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;font-family:'Roboto Mono',monospace;letter-spacing:.06em;display:inline-block;margin-bottom:7px;">{ntype}</span>
            <div style="font-size:14px;font-weight:700;color:{NAVY};margin-bottom:4px;">{n['title']}</div>
            <div style="font-size:13px;color:{GRAY};margin-bottom:5px;">{n['body']}</div>
            <div style="font-family:'Roboto Mono',monospace;font-size:10px;color:{LGRAY};">{n['date']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ✍️ 새 공지 작성")
    with st.form("w_nf_form"):
        n_type_sel = st.selectbox("분류", ["공지","업데이트","Q&A"], key="w_nf_type")
        n_title    = st.text_input("제목", key="w_nf_title")
        n_body     = st.text_area("내용", key="w_nf_body")
        if st.form_submit_button("✅ 게시", use_container_width=True):
            if n_title and n_body:
                notices = gs("_ss_notices")
                notices.insert(0, {
                    "type": n_type_sel, "title": n_title, "body": n_body,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                ss("_ss_notices", notices)
                st.success("공지가 게시되었습니다!"); st.rerun()
            else:
                st.warning("제목과 내용을 모두 입력해주세요.")
