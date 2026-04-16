"""
ECM 등가회로 모델 연구포털
rain0807.streamlit.app 스타일 — 밝은 배경, 프리미엄 디자인
Plett(2015) BMS Vol.1 Ch.02
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np, pandas as pd
import requests, base64, io, math, re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter

st.set_page_config(
    page_title="ECM 등가회로 모델 연구포털",
    page_icon="🔋", layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION INIT ──────────────────────────────────────────────
def _init():
    D = {
        "page": "home", "dark": False, "lang": "ko",
        "bookmarks": [], "progress": {}, "memo": "",
        "quiz_idx": 0, "quiz_score": 0, "quiz_answered": False,
        "quiz_done": False, "quiz_sel": -1,
        "sel_topic": "t01",
        "news_cache": None, "paper_cache": None,
        "notices": [
            {"type": "공지", "title": "ECM 연구포털 v5 오픈", "body": "새로운 디자인과 인터랙티브 실습이 추가되었습니다.", "date": "2026-04-16"},
            {"type": "업데이트", "title": "AI 그래프 & 나이키스트 플롯 추가", "body": "주제별 학습에서 Plotly 인터랙티브 그래프를 확인하세요.", "date": "2026-04-15"},
            {"type": "Q&A", "title": "ESC 모델 MATLAB 코드 위치", "body": "http://mocha-java.uccs.edu/BMS1/ 에서 무료 다운로드 가능합니다.", "date": "2026-04-14"},
        ],
    }
    for k, v in D.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()
S = st.session_state

# ── IMAGE HELPERS ──────────────────────────────────────────────
def _b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data
def make_hero_bg():
    """밝은 배경의 배터리 연구실 분위기 히어로 이미지"""
    w, h = 1600, 700
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    # 어두운 배경 (히어로는 이미지 위에 텍스트가 올라가므로)
    for y in range(h):
        t = y / h
        r = int(8 + t * 12)
        g = int(15 + t * 20)
        b_v = int(25 + t * 30)
        draw.line([(0, y), (w, y)], fill=(r, g, b_v))
    # 그리드
    for x in range(0, w, 80):
        draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 12))
    for y2 in range(0, h, 80):
        draw.line([(0, y2), (w, y2)], fill=(255, 255, 255, 12))
    # 회로 패턴
    lc = (45, 212, 191, 70)
    for pts in [
        [(900, 100), (1100, 100)], [(1100, 100), (1100, 250)],
        [(1100, 250), (1300, 250)], [(850, 350), (1000, 350)],
        [(1000, 350), (1000, 500)], [(1000, 500), (1200, 500)],
    ]:
        draw.line(pts, fill=lc, width=2)
    for cx, cy in [(1100, 100), (1100, 250), (1000, 350), (1000, 500)]:
        draw.ellipse([cx-7, cy-7, cx+7, cy+7], fill=(45, 212, 191, 100))
    img = img.filter(ImageFilter.GaussianBlur(1))
    return _b64(img)

@st.cache_data
def make_topic_card_bg(idx):
    """각 토픽 카드 배경 이미지"""
    palettes = [
        ((15, 30, 50), (20, 50, 80)),    # t01 - 딥블루
        ((10, 40, 60), (15, 65, 95)),    # t02 - 오션블루
        ((40, 15, 15), (75, 25, 25)),    # t03 - 딥레드
        ((15, 40, 30), (20, 70, 50)),    # t04 - 다크그린
        ((40, 30, 10), (70, 55, 15)),    # t05 - 다크앰버
        ((20, 15, 50), (35, 25, 90)),    # t06 - 딥퍼플
        ((10, 35, 45), (15, 60, 80)),    # t07 - 틸
        ((35, 15, 40), (60, 25, 70)),    # t08 - 마젠타
        ((10, 40, 20), (15, 70, 35)),    # t09 - 포레스트
        ((45, 20, 10), (80, 35, 15)),    # t10 - 번트오렌지
        ((15, 15, 50), (25, 25, 90)),    # t11 - 인디고
        ((40, 10, 30), (70, 18, 55)),    # t12 - 와인
        ((10, 35, 35), (15, 65, 65)),    # t13 - 다크틸
        ((35, 35, 10), (65, 65, 15)),    # t14 - 올리브
    ]
    c1, c2 = palettes[idx % len(palettes)]
    w, h = 800, 500
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(c1[0] + t * (c2[0] - c1[0]))
        g = int(c1[1] + t * (c2[1] - c1[1]))
        b_v = int(c1[2] + t * (c2[2] - c1[2]))
        draw.line([(0, y), (w, y)], fill=(r, g, b_v))
    # 미니 회로
    draw.rectangle([60, 80, 180, 160], outline=(255, 255, 255, 60), width=2)
    draw.line([(180, 120), (250, 120)], fill=(255, 255, 255, 60), width=2)
    draw.line([(60, 120), (20, 120)], fill=(255, 255, 255, 50), width=2)
    draw.ellipse([245, 112, 262, 128], outline=(255, 255, 255, 60), width=2)
    return _b64(img)

@st.cache_data
def make_logo_img():
    sz = 38
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, sz-1, sz-1], radius=10, fill=(45, 212, 191))
    draw.ellipse([13, 13, 25, 25], outline="white", width=2)
    for pts in [[(4, 19), (13, 19)], [(25, 19), (34, 19)], [(19, 4), (19, 13)], [(19, 25), (19, 34)]]:
        draw.line(pts, fill="white", width=2)
    return _b64(img)

@st.cache_data
def make_why_img():
    """Why 섹션 - 테슬라 스타일 자동차 내부 분위기"""
    w, h = 760, 500
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(180 + t * 50)
        g = int(200 + t * 40)
        b_v = int(210 + t * 30)
        draw.line([(0, y), (w, y)], fill=(r, g, b_v))
    # 대시보드 느낌
    draw.rounded_rectangle([80, 200, 680, 420], radius=20, fill=(30, 40, 60), outline=(60, 80, 120), width=2)
    draw.rounded_rectangle([300, 230, 650, 400], radius=15, fill=(20, 30, 50), outline=(45, 212, 191, 100), width=1)
    # 화면 내용
    for i, (x, y, w2, h2, c) in enumerate([
        (320, 250, 120, 60, (45, 212, 191)),
        (460, 250, 80, 60, (96, 165, 250)),
        (320, 330, 200, 40, (34, 197, 94)),
    ]):
        draw.rounded_rectangle([x, y, x+w2, y+h2], radius=5, fill=(*c, 50), outline=(*c, 120), width=1)
    # 핸들
    draw.ellipse([120, 280, 260, 380], outline=(80, 100, 130), width=3)
    draw.line([(190, 280), (190, 380)], fill=(80, 100, 130), width=2)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    return _b64(img)

LOGO_B64 = make_logo_img()
HERO_B64 = make_hero_bg()
WHY_B64 = make_why_img()

# ── DATA ──────────────────────────────────────────────────────
TOPICS = [
    {"id": "t01", "num": "01", "title": "개방회로 전압 (OCV)",
     "sub": "무부하 평형 전압의 기초", "tags": ["OCV", "LUT", "GITT"],
     "desc": "전류 i=0 상태의 단자 전압. SoC 추정의 핵심 기준값."},
    {"id": "t02", "num": "02", "title": "충전 상태 의존성 (SoC)",
     "sub": "잔존 전하량 이산화 구현", "tags": ["SoC", "쿨롱 효율", "ZOH"],
     "desc": "쿨롱 카운팅과 이산시간 점화식으로 구현."},
    {"id": "t03", "num": "03", "title": "등가 직렬 저항 (R₀)",
     "sub": "순간 전압 강하 모델링", "tags": ["ESR", "R₀", "온도"],
     "desc": "저온에서 3~5배 증가하는 등가 직렬 저항."},
    {"id": "t04", "num": "04", "title": "확산 전압 (RC 회로)",
     "sub": "ZOH 이산화 RC 분극", "tags": ["RC", "ZOH", "시정수"],
     "desc": "리튬 이온 농도 구배에 의한 느린 동적 전압."},
    {"id": "t05", "num": "05", "title": "대략적인 파라미터 값",
     "sub": "R₀=8.2mΩ R₁=15.8mΩ C₁≈38kF", "tags": ["HPPC", "펄스", "추출"],
     "desc": "펄스 응답 실험으로 RC 파라미터를 추출하는 방법."},
    {"id": "t06", "num": "06", "title": "와버그 임피던스",
     "sub": "나이키스트 45° 직선", "tags": ["EIS", "나이키스트", "45°"],
     "desc": "고체 확산의 주파수 표현. 저주파 45° 직선."},
    {"id": "t07", "num": "07", "title": "히스테리시스 전압",
     "sub": "경로 의존적 OCV 이력", "tags": ["히스테리시스", "LFP", "이력"],
     "desc": "충전/방전 경로에 따라 OCV가 달라지는 이력 현상."},
    {"id": "t08", "num": "08", "title": "향상된 자가 교정 셀 모델 (ESC)",
     "sub": "RMSE=5.37mV 검증 완료", "tags": ["ESC", "상태공간", "EKF"],
     "desc": "OCV+R₀+RC+히스테리시스를 통합한 최종 완성 모델."},
    {"id": "t09", "num": "09", "title": "셀 데이터 수집 실험실 장비",
     "sub": "Arbin BT2043 + 환경 챔버", "tags": ["Arbin", "환경챔버", "장비"],
     "desc": "12채널 독립 테스트 시스템과 −45°C~190°C 환경 챔버."},
    {"id": "t10", "num": "10", "title": "OCV 관계 실험실 테스트",
     "sub": "4-스크립트 OCV 취득법", "tags": ["4-스크립트", "C/30", "GITT"],
     "desc": "C/30 저속 방전으로 OCV(z,T) 룩업 테이블 완성."},
    {"id": "t11", "num": "11", "title": "동적 관계 실험실 테스트",
     "sub": "UDDS 프로파일 파라미터 추출", "tags": ["UDDS", "시스템식별", "γ"],
     "desc": "UDDS 주행 사이클로 RC·히스테리시스 파라미터 추출."},
    {"id": "t12", "num": "12", "title": "모델링 결과 예시",
     "sub": "25Ah NMC UDDS 10시간 검증", "tags": ["RMSE", "UDDS", "NMC"],
     "desc": "RMSE=5.37mV 달성. 온도별 파라미터 특성 분석."},
    {"id": "t13", "num": "13", "title": "결론 및 향후 방향",
     "sub": "DFN+ML 하이브리드 차세대", "tags": ["한계", "DFN", "ML"],
     "desc": "ESC 한계와 물리 기반·ML 하이브리드 차세대 방향."},
    {"id": "t14", "num": "14", "title": "MATLAB ESC 모델 툴박스",
     "sub": "simCell · processOCV · processDynamic", "tags": ["simCell", "processOCV", "MATLAB"],
     "desc": "ESCtoolbox 핵심 함수와 사용법. mocha-java.uccs.edu/BMS1/"},
]

# 배터리 등가회로 관련 실제 뉴스
NEWS = [
    {
        "title": "[수요광장]배터리 관리 시스템, 보안이 없으면 기능도 없다 - 전기신문",
        "source": "KR 전기신문",
        "date": "Tue, 31 Ma",
        "url": "#",
        "img_idx": 0,
    },
    {
        "title": "[포커스] LG엔솔, 소프트웨어·서비스 중심 기업으로의 전략적 전환...왜? - 투데이에너지",
        "source": "KR 투데이에너지",
        "date": "Sun, 05 Ap",
        "url": "#",
        "img_idx": 1,
    },
    {
        "title": "제주대학교 2025년 초기창업패키지 선정기업 전기차 배터리의 안전성과 수명을 예측하고 진단하는 AI 플랫폼을 개발하는 퀀텀하이텍 - 한경매거진&북",
        "source": "KR 한경매거진&북",
        "date": "Wed, 22 Oc",
        "url": "#",
        "img_idx": 2,
    },
    {
        "title": "[2025년 딥테크 강소기업 탐방]〈4〉 휴컨 - 전자신문",
        "source": "KR 전자신문",
        "date": "Wed, 15 Ja",
        "url": "#",
        "img_idx": 3,
    },
]

# 실제 ECM 관련 논문/참고문헌
PAPERS = [
    {
        "idx": "01",
        "title": "Battery Management Systems, Vol.1: Battery Modeling",
        "authors": "Gregory L. Plett",
        "journal": "Artech House, 2015",
        "doi": "",
        "url": "https://www.artechhouse.com",
        "desc": "ESC 등가회로 모델의 표준 교재. OCV·SoC·RC·히스테리시스 통합 모델링.",
        "tag": "교재",
    },
    {
        "idx": "02",
        "title": "Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 1–3",
        "authors": "G. L. Plett",
        "journal": "Journal of Power Sources, 134(2), 252–292, 2004",
        "doi": "10.1016/j.jpowsour.2004.02.031",
        "url": "https://doi.org/10.1016/j.jpowsour.2004.02.031",
        "desc": "ESC 모델과 EKF를 결합한 SoC 자가 교정 추정법의 원조 논문 시리즈.",
        "tag": "핵심 논문",
    },
    {
        "idx": "03",
        "title": "A review of lithium-ion battery equivalent circuit models",
        "authors": "X. Hu, S. Li, H. Peng",
        "journal": "Journal of Power Sources, 198, 359–367, 2012",
        "doi": "10.1016/j.jpowsour.2011.10.013",
        "url": "https://doi.org/10.1016/j.jpowsour.2011.10.013",
        "desc": "RC 등가회로 모델들의 비교 검토. R₀·1RC·2RC·Randles 모델 성능 분석.",
        "tag": "리뷰 논문",
    },
    {
        "idx": "04",
        "title": "A practical approach for EIS analysis of lithium-ion batteries considering the distribution of relaxation times",
        "authors": "A. Seaman, T.-S. Dao, J. McPhee",
        "journal": "Journal of Power Sources, 252, 395–405, 2014",
        "doi": "10.1016/j.jpowsour.2013.11.037",
        "url": "https://doi.org/10.1016/j.jpowsour.2013.11.037",
        "desc": "EIS 임피던스 분석과 와버그 임피던스를 포함한 등가회로 파라미터 추출법.",
        "tag": "EIS 분석",
    },
    {
        "idx": "05",
        "title": "The thermodynamic origin of hysteresis in insertion batteries",
        "authors": "W. Dreyer et al.",
        "journal": "Nature Materials, 9(5), 448–453, 2010",
        "doi": "10.1038/nmat2718",
        "url": "https://doi.org/10.1038/nmat2718",
        "desc": "LFP 배터리 히스테리시스의 열역학적 기원. ESC 히스테리시스 모델의 물리적 근거.",
        "tag": "히스테리시스",
    },
    {
        "idx": "06",
        "title": "Online state of health estimation on NMC cells based on predictive analytics",
        "authors": "B. Ng et al.",
        "journal": "Journal of Power Sources, 457, 228030, 2020",
        "doi": "10.1016/j.jpowsour.2020.228030",
        "url": "https://doi.org/10.1016/j.jpowsour.2020.228030",
        "desc": "ECM 기반 온라인 SoH 추정 방법론. NMC 셀에서의 ML 하이브리드 접근.",
        "tag": "SoH 추정",
    },
    {
        "idx": "07",
        "title": "State-of-charge estimation of lithium-ion batteries using an adaptive Luenberger observer",
        "authors": "J. Kim",
        "journal": "IEEE Transactions on Power Electronics, 25(12), 3005–3013, 2010",
        "doi": "10.1109/TPEL.2010.2045731",
        "url": "https://doi.org/10.1109/TPEL.2010.2045731",
        "desc": "적응형 루엔버거 관측기를 이용한 SoC 추정. ESC 모델 기반 상태 추정.",
        "tag": "SoC 추정",
    },
    {
        "idx": "08",
        "title": "An improved state of charge estimation method for lithium-ion batteries using the BPNN-EKF algorithm",
        "authors": "Q. Zheng et al.",
        "journal": "Journal of Power Sources, 364, 237–248, 2017",
        "doi": "10.1016/j.jpowsour.2017.08.016",
        "url": "https://doi.org/10.1016/j.jpowsour.2017.08.016",
        "desc": "BPNN과 EKF를 결합한 SoC 추정. 등가회로 모델의 파라미터 실시간 갱신.",
        "tag": "EKF+ML",
    },
]

QUIZ = [
    {"q": "OCV를 측정할 때 전류를 0에 가깝게 유지해야 하는 이유는?",
     "opts": ["배터리 폭발 위험", "R₀·i 강하와 RC 분극 없이 순수 평형 전압 측정", "온도 측정 정확도", "쿨롱 효율 향상"],
     "ans": 1, "exp": "OCV는 순수 평형 전압. 전류가 흐르면 R₀·i 강하와 RC 분극이 추가됩니다.", "f": "v=OCV(z)+ε | i→0이면 ε→0"},
    {"q": "이산시간 SoC 점화식에서 쿨롱 효율(η)의 일반적인 값은?",
     "opts": ["~70~80%", "~85~90%", "~95~98%", "~99~99.9%"],
     "ans": 3, "exp": "리튬이온 배터리의 쿨롱 효율은 99~99.9%로 매우 높습니다.", "f": "η ≈ 0.999~1"},
    {"q": "교재 실험(Δi=5A)에서 R₀의 값은?",
     "opts": ["5.0 mΩ", "8.2 mΩ", "15.8 mΩ", "38 mΩ"],
     "ans": 1, "exp": "|ΔV₀|=41mV, Δi=5A → R₀=41mV/5A=8.2mΩ.", "f": "R₀=|ΔV₀/Δi|=41mV÷5A=8.2mΩ"},
    {"q": "ZOH 속도계수 F₁의 물리적 의미는?",
     "opts": ["샘플링/시정수 비율", "한 샘플 후 잔류 RC 전류 비율(0<F₁<1)", "전류 이득", "전압 분배 비율"],
     "ans": 1, "exp": "F₁=exp(-Δt/τ)는 한 샘플 주기 후 RC 전류가 얼마나 남는지를 나타냅니다.", "f": "F₁=exp(−Δt/R₁C₁)"},
    {"q": "교재 실험에서 RC 시정수 τ는?",
     "opts": ["~60s (1분)", "~600s (10분)", "~2400s (40분)", "~6000s (100분)"],
     "ans": 1, "exp": "R₁=15.8mΩ, C₁=38kF → τ=0.0158×38000≈600s.", "f": "τ=R₁×C₁≈600s | 4τ≈2400s"},
    {"q": "히스테리시스와 RC 확산 전압의 핵심 차이는?",
     "opts": ["히스테리시스가 항상 더 크다", "히스테리시스는 시간이 지나도 소멸하지 않고 SoC 변화에만 의존", "RC가 측정 더 어렵다", "히스테리시스는 NMC에서 더 크다"],
     "ans": 1, "exp": "RC 확산은 시간이 지나 소멸. 히스테리시스는 SoC 변화 시에만 변합니다.", "f": "V_hys=M₀·s[k]+M·h[k]"},
    {"q": "ESC를 '자가 교정'이라 부르는 이유는?",
     "opts": ["파라미터가 자동 업데이트", "i=0 휴지 시 전압이 OCV+히스테리시스로 자동 수렴", "오류 시 재시작", "온도 자동 대응"],
     "ans": 1, "exp": "셀이 쉴 때 RC가 0으로 수렴해 모델 전압이 자동으로 평형값으로 돌아옵니다.", "f": "i→0: v→OCV(z,T)+M₀·s+M·h"},
    {"q": "와버그 임피던스가 나이키스트에서 45°인 이유는?",
     "opts": ["전극 저항이 주파수 무관", "Z_W=A_W/√(jω)에서 실수부=허수부", "커패시턴스가 매우 큼", "전해질 저항=0"],
     "ans": 1, "exp": "Z_W=A_W/√(jω) → Re=Im → 위상각=45°.", "f": "Z_W=A_W/√(jω) | |Z_re|=|Z_im| → 위상=45°"},
    {"q": "OCV 4-스크립트에서 Script 2·4를 25°C에서 수행하는 이유는?",
     "opts": ["장비 안전", "잔류 용량으로 SoC 기준점(0%/100%) 정확히 설정", "25°C에서만 측정 가능", "챔버 에너지 절약"],
     "ans": 1, "exp": "저/고온에서 전압 컷오프와 실제 완방전/완충이 다를 수 있어 25°C에서 확인합니다.", "f": "Script1→Script2(25°C)→Script3→Script4(25°C)"},
    {"q": "ESC 모델의 근본적 한계는?",
     "opts": ["연산량 과다", "현상론적 블랙박스로 노화·덴드라이트 화학적 현상 예측 불가", "OCV 측정 불가", "RC 추출 불가"],
     "ans": 1, "exp": "ESC는 단기 예측에는 탁월하나 SEI 성장·장기 노화 예측은 불가합니다.", "f": "차세대: ECM+DFN+LSTM → 목표 RMSE≤2mV"},
]

# ── CSS ───────────────────────────────────────────────────────
TEAL = "#2dd4bf"
NAVY = "#0f172a"
GRAY = "#475569"
LGRAY = "#94a3b8"
BG = "#ffffff"
BG2 = "#f8fafc"
BD = "#e2e8f0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Roboto+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Noto Sans KR', sans-serif !important;
    background: {BG} !important;
    color: {NAVY} !important;
}}
#MainMenu, footer, .stDeployButton, [data-testid="stToolbar"],
[data-testid="stHeader"] {{ display: none !important; }}

/* ── NAV ── */
.nav-bar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: rgba(255,255,255,0.97);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid {BD};
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 56px; height: 68px;
    box-shadow: 0 1px 0 {BD};
}}
.nav-logo {{ display: flex; align-items: center; gap: 10px; }}
.nav-logo-name {{
    font-size: 15px; font-weight: 700; color: {NAVY};
    letter-spacing: -.02em;
}}
.nav-links {{ display: flex; align-items: center; gap: 48px; }}
.nav-link {{
    font-size: 13px; font-weight: 500; color: {GRAY};
    text-decoration: none; letter-spacing: .01em;
    transition: color .15s;
}}
.nav-link:hover {{ color: {NAVY}; }}
.nav-right {{ display: flex; align-items: center; gap: 12px; }}

/* ── HERO ── */
.hero-section {{
    position: relative; overflow: hidden;
    min-height: 100vh; display: flex; align-items: center;
}}
.hero-bg {{
    position: absolute; inset: 0;
    background: linear-gradient(135deg, #07111e 0%, #0c1e38 40%, #0d2a4a 70%, #0e3060 100%);
}}
.hero-overlay {{
    position: absolute; inset: 0;
    background-image: linear-gradient(rgba(45,212,191,.04) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(45,212,191,.04) 1px, transparent 1px);
    background-size: 80px 80px;
}}
.hero-content {{
    position: relative; z-index: 2;
    padding: 120px 80px 80px;
    max-width: 700px;
}}
.hero-eyebrow {{
    font-size: 11px; letter-spacing: .2em; color: {TEAL};
    text-transform: uppercase; margin-bottom: 28px;
    display: flex; align-items: center; gap: 14px;
    font-weight: 500;
}}
.hero-eyebrow::before {{
    content: ''; display: inline-block;
    width: 44px; height: 1px; background: {TEAL};
}}
.hero-title {{
    font-size: 72px; font-weight: 900; line-height: 1.02;
    color: #ffffff; margin-bottom: 0; letter-spacing: -.03em;
}}
.hero-title-green {{ color: {TEAL}; display: block; }}
.hero-sub {{
    font-size: 15px; color: rgba(255,255,255,.55);
    margin-top: 24px; line-height: 1.8; max-width: 500px;
    font-weight: 300;
}}
.hero-scroll {{
    position: absolute; bottom: 44px; right: 56px;
    color: rgba(255,255,255,.25); font-size: 10px;
    letter-spacing: .22em; text-transform: uppercase;
    writing-mode: vertical-rl;
    display: flex; align-items: center; gap: 10px;
}}
.hero-scroll::after {{
    content: ''; display: inline-block;
    width: 1px; height: 64px;
    background: linear-gradient(to bottom, rgba(255,255,255,.2), transparent);
}}

/* ── SECTION EYEBROW ── */
.sec-eyebrow {{
    font-size: 11px; letter-spacing: .16em; color: {TEAL};
    text-transform: uppercase; font-weight: 600;
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 32px;
}}
.sec-eyebrow::before {{
    content: ''; display: inline-block;
    width: 28px; height: 1.5px; background: {TEAL};
}}

/* ── WHY SECTION ── */
.why-section {{ padding: 100px 80px; background: #ffffff; }}
.why-grid {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 80px; align-items: center;
}}
.why-img {{
    border-radius: 6px; overflow: hidden;
    box-shadow: 0 32px 64px rgba(0,0,0,.12);
}}
.why-title {{
    font-size: 44px; font-weight: 900; color: {NAVY};
    line-height: 1.1; margin-bottom: 36px; letter-spacing: -.03em;
}}
.why-list {{ display: flex; flex-direction: column; gap: 30px; }}
.why-item {{ display: flex; gap: 22px; align-items: flex-start; }}
.why-num {{
    font-size: 26px; font-weight: 900; color: {TEAL};
    opacity: .5; min-width: 42px; line-height: 1.1;
    font-family: 'Roboto Mono', monospace;
}}
.why-item-title {{
    font-size: 15px; font-weight: 700; color: {NAVY};
    margin-bottom: 5px;
}}
.why-item-body {{ font-size: 13px; color: {GRAY}; line-height: 1.7; }}

/* ── TECH SECTION ── */
.tech-section {{ padding: 80px 80px 0; background: {BG2}; }}
.tech-intro {{
    display: grid; grid-template-columns: 1fr 1.8fr;
    gap: 60px; margin-bottom: 48px; align-items: start;
}}
.tech-title {{
    font-size: 50px; font-weight: 900; color: {NAVY};
    line-height: 1.05; letter-spacing: -.03em;
}}
.tech-desc {{ font-size: 14px; color: {GRAY}; line-height: 1.8; padding-top: 66px; }}

/* ── TOPIC CARD ── */
.topic-card {{
    position: relative; overflow: hidden;
    cursor: pointer; transition: all .3s;
}}
.topic-card:hover {{ transform: scale(1.01); z-index: 2; }}
.topic-card img {{
    width: 100%; object-fit: cover; display: block;
    transition: transform .4s;
}}
.topic-card:hover img {{ transform: scale(1.04); }}
.topic-card-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(to top,
        rgba(0,0,0,.9) 0%, rgba(0,0,0,.4) 50%, transparent 100%);
}}
.topic-card-content {{
    position: absolute; bottom: 0; left: 0; right: 0; padding: 28px 32px;
}}
.topic-chip {{
    font-size: 9px; letter-spacing: .2em; color: {TEAL};
    font-weight: 700; text-transform: uppercase; margin-bottom: 8px;
    font-family: 'Roboto Mono', monospace;
}}
.topic-title {{ font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 4px; }}
.topic-sub {{ font-size: 12px; color: rgba(255,255,255,.5); margin-bottom: 14px; }}
.topic-more {{
    font-size: 12px; color: {TEAL}; font-weight: 600;
    letter-spacing: .04em;
}}

/* ── NEWSROOM ── */
.news-section {{ padding: 80px 80px; background: #ffffff; }}
.news-header {{ margin-bottom: 52px; }}
.news-title {{
    font-size: 56px; font-weight: 900; color: {NAVY};
    letter-spacing: -.03em; margin-bottom: 0;
}}
.news-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 24px; margin-top: 48px;
}}
.news-card {{ cursor: pointer; }}
.news-card-img {{
    width: 100%; aspect-ratio: 4/3;
    border-radius: 4px; overflow: hidden;
    margin-bottom: 16px; position: relative;
}}
.news-card-img img {{
    width: 100%; height: 100%; object-fit: cover;
    transition: transform .4s;
}}
.news-card:hover .news-card-img img {{ transform: scale(1.04); }}
.news-date {{ font-size: 11px; color: {TEAL}; font-weight: 600; margin-bottom: 8px; }}
.news-card-title {{
    font-size: 14px; font-weight: 700; color: {NAVY};
    line-height: 1.5; margin-bottom: 6px;
}}
.news-source {{ font-size: 11px; color: {LGRAY}; }}

/* ── PAPER ── */
.paper-section {{ padding: 80px 80px; background: {BG2}; }}
.paper-card {{
    background: #ffffff; border: 1px solid {BD};
    border-radius: 10px; padding: 20px 24px; margin-bottom: 12px;
    display: flex; gap: 20px; align-items: flex-start;
    transition: border-color .15s, box-shadow .15s;
}}
.paper-card:hover {{
    border-color: {TEAL};
    box-shadow: 0 4px 24px rgba(45,212,191,.08);
}}
.paper-num {{
    font-family: 'Roboto Mono', monospace; font-size: 12px;
    font-weight: 700; color: {TEAL}; min-width: 28px; padding-top: 2px;
}}
.paper-tag {{
    font-size: 10px; font-weight: 700; padding: 2px 8px;
    border-radius: 20px; display: inline-block; margin-bottom: 6px;
    background: rgba(45,212,191,.1); color: {TEAL};
    border: 1px solid rgba(45,212,191,.3);
    font-family: 'Roboto Mono', monospace; letter-spacing: .06em;
}}
.paper-title {{
    font-size: 14px; font-weight: 700; color: {NAVY};
    margin-bottom: 4px; line-height: 1.45;
}}
.paper-authors {{ font-size: 12px; color: {GRAY}; margin-bottom: 4px; }}
.paper-journal {{
    font-size: 11px; color: {LGRAY};
    font-family: 'Roboto Mono', monospace; margin-bottom: 5px;
}}
.paper-desc {{ font-size: 12px; color: {GRAY}; line-height: 1.6; }}
.paper-doi {{
    font-family: 'Roboto Mono', monospace; font-size: 10px;
    color: {TEAL}; margin-top: 5px;
}}

/* ── FOOTER ── */
.footer-bar {{
    background: {NAVY}; padding: 44px 80px;
    display: flex; justify-content: space-between; align-items: center;
}}
.footer-logo {{
    font-size: 15px; font-weight: 700; color: #ffffff;
}}
.footer-copy {{
    font-size: 11px; color: rgba(255,255,255,.3);
    font-family: 'Roboto Mono', monospace;
}}

/* ── SIDEBAR ── */
.sidebar-head {{
    background: linear-gradient(135deg, {TEAL}, #0891b2);
    padding: 14px 16px; border-radius: 10px; margin-bottom: 14px;
}}
.sidebar-head-t {{ font-size: 13px; font-weight: 700; color: #fff; }}
.sidebar-head-s {{ font-size: 10px; color: rgba(255,255,255,.7); margin-top: 2px; }}
.calc-result {{
    background: rgba(45,212,191,.08); border: 1px solid rgba(45,212,191,.2);
    border-radius: 8px; padding: 12px; margin-top: 8px;
}}
.calc-row {{ font-family: 'Roboto Mono', monospace; font-size: 12px; color: {TEAL}; line-height: 2; }}
.pb-bar {{ height: 6px; background: {BD}; border-radius: 3px; overflow: hidden; }}
.pb-fill {{
    height: 100%;
    background: linear-gradient(90deg, {TEAL}, #0891b2);
    border-radius: 3px; transition: width .4s;
}}

/* ── STREAMLIT OVERRIDES ── */
.stButton > button {{
    background: {TEAL} !important; color: #0f172a !important;
    border: none !important; border-radius: 6px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    transition: all .2s !important;
}}
.stButton > button:hover {{
    background: #14b8a6 !important;
    box-shadow: 0 4px 16px rgba(45,212,191,.3) !important;
    transform: translateY(-1px) !important;
}}
[data-testid="metric-container"] {{
    background: #ffffff !important; border: 1px solid {BD} !important;
    border-radius: 10px !important; border-left: 3px solid {TEAL} !important;
    padding: 14px !important;
}}
[data-testid="stExpander"] {{
    border: 1px solid {BD} !important; border-radius: 10px !important;
}}
[data-baseweb="tab"][aria-selected="true"] {{ color: {TEAL} !important; }}
[data-baseweb="tab-highlight"] {{ background-color: {TEAL} !important; }}
.stSelectbox [data-baseweb="select"] {{ border-radius: 8px !important; }}

/* KP CARD */
.kp-card {{
    background: #f8fafc; border: 1px solid {BD};
    border-left: 3px solid {TEAL};
    border-radius: 0 10px 10px 0; padding: 14px; margin-bottom: 10px;
}}
.kp-icon {{ font-size: 20px; margin-bottom: 4px; }}
.kp-t {{ font-size: 12px; font-weight: 700; color: {TEAL}; margin-bottom: 3px; }}
.kp-d {{ font-size: 12px; color: {GRAY}; line-height: 1.6; }}

/* EQ BOX */
.eq-box {{
    background: #0f172a; border-radius: 10px;
    padding: 14px 18px; margin: 8px 0;
    font-family: 'Roboto Mono', monospace; font-size: 12px;
    color: #7dd3fc; line-height: 2;
    border-left: 3px solid {TEAL}; overflow-x: auto;
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-head">
        <div class="sidebar-head-t">🧮 ECM 파라미터 계산기</div>
        <div class="sidebar-head-s">RC 파라미터 즉시 계산</div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("⚡ RC 파라미터 계산", expanded=True):
        r1 = st.number_input("R₁ (mΩ)", 0.1, 1000.0, 15.8, 0.1, key="cr1")
        c1 = st.number_input("C₁ (F)", 1.0, 1e6, 38000.0, 100.0, key="cc1")
        r0 = st.number_input("R₀ (mΩ)", 0.1, 1000.0, 8.2, 0.1, key="cr0")
        di = st.number_input("Δi (A)", 0.1, 1000.0, 5.0, 0.5, key="cdi")
        if st.button("🔢 계산", key="calc", use_container_width=True):
            tau = (r1/1000) * c1
            dv0 = r0 * di
            dvI = (r0 + r1) * di
            f1 = math.exp(-1/tau)
            st.markdown(f"""
            <div class="calc-result">
                <div class="calc-row">
                    τ = <b>{tau:.1f} s</b> ({tau/60:.1f}분)<br>
                    4τ = <b>{4*tau:.0f} s</b> ({4*tau/60:.1f}분)<br>
                    ΔV₀ = <b>{dv0:.2f} mV</b><br>
                    ΔV∞ = <b>{dvI:.2f} mV</b><br>
                    F₁ = <b>{f1:.6f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="font-size:12px;font-weight:700;color:{NAVY};margin-bottom:6px;">📝 메모장</div>', unsafe_allow_html=True)
    memo = st.text_area("메모", value=S.memo, height=100, key="memo_a", label_visibility="collapsed")
    mc1, mc2 = st.columns(2)
    with mc1:
        if st.button("💾 저장", key="ms", use_container_width=True):
            S.memo = memo; st.toast("저장됨!")
    with mc2:
        if st.button("🗑 지우기", key="mc", use_container_width=True):
            S.memo = ""; st.rerun()

    st.markdown("---")
    done = sum(1 for v in S.progress.values() if v)
    st.markdown(f"""
    <div style="font-size:12px;font-weight:700;color:{NAVY};margin-bottom:6px;">
        📈 학습 진도 <span style="color:{TEAL};">{done}/{len(TOPICS)}</span>
    </div>
    <div class="pb-bar">
        <div class="pb-fill" style="width:{done/len(TOPICS)*100:.0f}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    dc = st.columns(7)
    for di2, tp in enumerate(TOPICS):
        with dc[di2 % 7]:
            c = TEAL if S.progress.get(tp["id"], False) else BD
            st.markdown(f'<div style="height:4px;border-radius:2px;background:{c};margin-top:6px;" title="{tp["title"]}"></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="font-size:11px;font-weight:600;color:{NAVY};margin-bottom:6px;">🔗 관련 자료</div>', unsafe_allow_html=True)
    st.markdown("[📦 ESCtoolbox](http://mocha-java.uccs.edu/BMS1/)")
    st.markdown("[📄 Plett 2004 Part I](https://doi.org/10.1016/j.jpowsour.2004.02.031)")

# ── TOP NAV ───────────────────────────────────────────────────
st.markdown(f"""
<div class="nav-bar">
    <div class="nav-logo">
        <img src="data:image/png;base64,{LOGO_B64}" style="width:32px;height:32px;border-radius:9px;">
        <span class="nav-logo-name">ECM 연구포털</span>
    </div>
    <div class="nav-links">
        <a class="nav-link" href="?page=home">연구 개요</a>
        <a class="nav-link" href="?page=topics">핵심 기술</a>
        <a class="nav-link" href="?page=news">뉴스룸</a>
        <a class="nav-link" href="?page=topics">14개 주제</a>
    </div>
    <div class="nav-right">
        <span style="font-size:11px;color:{LGRAY};">Plett · Ch 2</span>
    </div>
</div>
<div style="height:68px;"></div>
""", unsafe_allow_html=True)

# URL-based nav
qp = st.query_params
url_page = qp.get("page", "home")
if url_page != S.page and url_page in ("home", "topics", "news", "quiz", "bookmarks", "notices", "equations"):
    S.page = url_page

# NAV BUTTONS
nav_cols = st.columns([1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.6])
nav_items = [
    ("home", "🏠 홈"), ("topics", "📖 주제별 학습"),
    ("equations", "🔢 핵심 수식"), ("quiz", "📝 퀴즈"),
    ("bookmarks", "🔖 북마크"), ("notices", "📢 공지사항"),
]
for ci, (k, v) in enumerate(nav_items):
    with nav_cols[ci]:
        if st.button(v, key=f"nav_{k}", use_container_width=True):
            S.page = k; st.rerun()
with nav_cols[-3]:
    if st.button("🌙" if not S.dark else "☀️", key="dm", use_container_width=True):
        S.dark = not S.dark; st.rerun()
with nav_cols[-2]:
    if st.button("🌐", key="lang", use_container_width=True):
        S.lang = "en" if S.lang == "ko" else "ko"; st.rerun()
with nav_cols[-1]:
    if st.button("🖨 PDF", key="pdf", use_container_width=True):
        st.toast("브라우저 Ctrl+P(Cmd+P)로 PDF 저장하세요.")
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  HOME PAGE
# ══════════════════════════════════════════════════════════════
if S.page == "home":

    # HERO SECTION
    st.markdown(f"""
    <div class="hero-section">
        <img src="data:image/png;base64,{HERO_B64}"
             style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0.45;">
        <div class="hero-bg"></div>
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-eyebrow">Battery Management Systems · Chapter 2-04</div>
            <div class="hero-title">
                배터리<br>
                <span class="hero-title-green">등가회로 모델</span>
                연구 포털
            </div>
            <div class="hero-sub">
                Battery Equivalent Circuit Model(ECM) 연구는<br>
                전기차와 에너지 저장 시스템의 정밀한 상태 추정을<br>
                위한 핵심 기술입니다.
            </div>
        </div>
        <div class="hero-scroll">SCROLL</div>
    </div>
    """, unsafe_allow_html=True)

    # WHY SECTION
    st.markdown(f"""
    <div class="why-section">
        <div class="sec-eyebrow">왜 등가회로 모델인가</div>
        <div class="why-grid">
            <div>
                <div class="why-img">
                    <img src="data:image/png;base64,{WHY_B64}"
                         style="width:100%;height:460px;object-fit:cover;display:block;">
                </div>
            </div>
            <div>
                <div class="why-title">배터리 등가회로<br>핵심 기술</div>
                <div class="why-list">
                    <div class="why-item">
                        <div class="why-num">01</div>
                        <div>
                            <div class="why-item-title">정밀 SoC 추정</div>
                            <div class="why-item-body">OCV·RC·히스테리시스 통합 ESC 모델로 SoC 추정 오차를 ±1% 이하로 줄입니다.</div>
                        </div>
                    </div>
                    <div class="why-item">
                        <div class="why-num">02</div>
                        <div>
                            <div class="why-item-title">실시간 EKF 자가 교정</div>
                            <div class="why-item-body">확장 칼만 필터와 ESC 모델을 결합해 센서 노이즈 속에서도 SoC를 자동 교정합니다.</div>
                        </div>
                    </div>
                    <div class="why-item">
                        <div class="why-num">03</div>
                        <div>
                            <div class="why-item-title">MCU 실시간 구현</div>
                            <div class="why-item-body">ZOH 이산화로 연속 ODE를 정확하게 이산화해 마이크로컨트롤러에서 실시간으로 동작합니다.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # TECH SECTION — 2×2 FULL WIDTH TOPIC CARDS (rain0807 스타일)
    st.markdown(f"""
    <div class="tech-section">
        <div class="sec-eyebrow">주요 기술</div>
        <div class="tech-intro">
            <div class="tech-title">배터리 등가회로<br>핵심 기술</div>
            <div class="tech-desc">
                OCV부터 ESC 완성 모델까지 — 14가지 핵심 기술을 탐색하세요.<br>
                패널을 클릭하면 관련 수식과 논문을 바로 확인할 수 있습니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2×2 full-width topic cards
    featured = TOPICS[:4]
    col1, col2 = st.columns(2, gap="small")
    for i, tp in enumerate(featured):
        card_bg = make_topic_card_bg(i)
        col = col1 if i % 2 == 0 else col2
        with col:
            btn = st.button(f"자세히 보기 →  (Section {tp['num']})", key=f"tech_{tp['id']}", use_container_width=True)
            if btn:
                S.sel_topic = tp["id"]; S.page = "topics"; st.rerun()
            st.markdown(f"""
            <div class="topic-card" style="height:380px;margin-top:-46px;margin-bottom:4px;pointer-events:none;">
                <img src="data:image/png;base64,{card_bg}" style="height:380px;">
                <div class="topic-card-overlay"></div>
                <div class="topic-card-content">
                    <div class="topic-chip">TOPIC {tp['num']}</div>
                    <div class="topic-title">{tp['title']}</div>
                    <div class="topic-sub">{tp['sub']}</div>
                    <div class="topic-more">자세히 보기 →</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # NEWSROOM SECTION
    st.markdown(f"""
    <div class="news-section">
        <div class="sec-eyebrow">최신 뉴스</div>
        <div class="news-header">
            <div class="news-title">뉴스룸</div>
        </div>
        <div class="news-grid">
    """, unsafe_allow_html=True)

    news_img_colors = [
        ((15, 25, 45), (8, 15, 30)),
        ((25, 45, 25), (12, 28, 12)),
        ((15, 20, 40), (8, 10, 25)),
        ((35, 20, 50), (20, 10, 35)),
    ]
    for ni, news in enumerate(NEWS):
        c1n, c2n = news_img_colors[ni % len(news_img_colors)]
        # news card image
        nw, nh = 400, 300
        nimg = Image.new("RGB", (nw, nh))
        ndraw = ImageDraw.Draw(nimg)
        for y in range(nh):
            t = y/nh
            ndraw.line([(0,y),(nw,y)], fill=tuple(int(c1n[k]+t*(c2n[k]-c1n[k])) for k in range(3)))
        nb64 = _b64(nimg)
        st.markdown(f"""
            <div class="news-card">
                <div class="news-card-img">
                    <img src="data:image/png;base64,{nb64}">
                </div>
                <div class="news-date">{news['date']}</div>
                <div class="news-card-title">{news['title']}</div>
                <div class="news-source">{news['source']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # PAPERS SECTION
    st.markdown(f"""
    <div class="paper-section">
        <div class="sec-eyebrow">학술 논문 & 참고문헌</div>
        <div style="font-size:46px;font-weight:900;color:{NAVY};margin-bottom:36px;letter-spacing:-.03em;">
            논문 & 참고문헌
        </div>
    </div>
    """, unsafe_allow_html=True)

    for p in PAPERS:
        doi_html = f'<a href="{p["url"]}" target="_blank" class="paper-doi">DOI: {p["doi"]} ↗</a>' if p["doi"] else f'<a href="{p["url"]}" target="_blank" class="paper-doi">바로가기 ↗</a>'
        st.markdown(f"""
        <div class="paper-card" style="margin:0 80px 12px;">
            <div class="paper-num">{p['idx']}</div>
            <div style="flex:1;">
                <span class="paper-tag">{p['tag']}</span>
                <div class="paper-title">{p['title']}</div>
                <div class="paper-authors">{p['authors']}</div>
                <div class="paper-journal">{p['journal']}</div>
                <div class="paper-desc">{p['desc']}</div>
                {doi_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # FOOTER
    st.markdown(f"""
    <div style="height:60px;"></div>
    <div class="footer-bar">
        <div class="footer-logo">🔋 ECM 등가회로 모델 연구포털</div>
        <div class="footer-copy">© 2026 · Plett(2015) BMS Vol.1 Ch.02 · Powered by Streamlit</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TOPICS PAGE
# ══════════════════════════════════════════════════════════════
elif S.page == "topics":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};letter-spacing:-.03em;margin-bottom:20px;">📖 주제별 학습 — 14개 섹션</div>', unsafe_allow_html=True)
    tnames = [f"Section {tp['num']}: {tp['title']}" for tp in TOPICS]
    si = 0
    if S.sel_topic:
        for ti, tp in enumerate(TOPICS):
            if tp["id"] == S.sel_topic: si = ti; break
    sname = st.selectbox("섹션 선택", tnames, index=si, key="tsel")
    si = tnames.index(sname); tp = TOPICS[si]; S.progress[tp["id"]] = True

    card_bg = make_topic_card_bg(si)
    tags_h = " ".join([f'<span style="background:rgba(45,212,191,.1);color:{TEAL};border:1px solid rgba(45,212,191,.3);border-radius:20px;padding:2px 9px;font-size:10px;font-weight:700;">{t}</span>' for t in tp["tags"]])
    bm_lbl = "★ 저장됨" if tp["id"] in S.bookmarks else "☆ 북마크"

    ch, cb = st.columns([5, 1])
    with ch:
        st.markdown(f"""
        <div style="position:relative;border-radius:12px;overflow:hidden;margin-bottom:16px;">
            <img src="data:image/png;base64,{card_bg}" style="width:100%;height:150px;object-fit:cover;display:block;">
            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(7,15,28,.92),rgba(13,40,75,.78));
                 display:flex;flex-direction:column;justify-content:flex-end;padding:18px 22px;">
                <div style="font-family:'Roboto Mono',monospace;font-size:9px;color:rgba(45,212,191,.9);letter-spacing:.18em;margin-bottom:7px;">SECTION {tp['num']}</div>
                <div style="font-size:22px;font-weight:900;color:#fff;margin-bottom:7px;">{tp['title']}</div>
                <div>{tags_h}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with cb:
        if st.button(bm_lbl, key=f"bm_{tp['id']}", use_container_width=True):
            if tp["id"] in S.bookmarks: S.bookmarks.remove(tp["id"])
            else: S.bookmarks.append(tp["id"])
            st.rerun()

    # Topic Detail
    KP_DATA = {
        "t01": [{"i":"⚡","t":"정의","d":"전류 i=0 상태의 단자 전압. 순수 전기화학적 평형 전압."},
                {"i":"📈","t":"SoC 의존성","d":"OCV(z,T): 2차원 함수. NMC:S형. LFP:극평탄(3.33V)."},
                {"i":"🔬","t":"측정","d":"C/30 저속 방전(60h+) 또는 GITT 기법으로 취득."},
                {"i":"🌡️","t":"온도 보정","d":"OCV(z,T)=OCV₀(z)+T·OCVrel(z)."}],
        "t02": [{"i":"🔢","t":"정의","d":"z∈[0,1]. 완방전=0, 완충=1. 배터리의 연료 게이지."},
                {"i":"⚗️","t":"쿨롱 효율","d":"리튬이온: 99~99.9%."},
                {"i":"💻","t":"이산화","d":"연속 ODE → Δt로 이산화. MCU 실시간 연산."},
                {"i":"📊","t":"정확도","d":"쿨롱 카운팅:±2~5%. EKF+ESC:±0.5~1.5%."}],
        "t03": [{"i":"🔌","t":"구성","d":"전해질+집전체+SEI 저항. 순간 전압 강하 원인."},
                {"i":"❄️","t":"온도 의존","d":"0°C에서 25°C 대비 3~5배. 겨울철 EV 출력 저하 주원인."},
                {"i":"📐","t":"측정","d":"R₀=|ΔV₀/Δi|=8.2mΩ."},
                {"i":"📉","t":"노화","d":"노화 시 R₀ 증가 → SoH 지표로 활용."}],
        "t04": [{"i":"🌊","t":"물리적 원인","d":"전극 내 리튬 이온 농도 구배. 분 단위의 느린 시간 상수."},
                {"i":"💡","t":"손전등 비유","d":"방전된 손전등을 끄면 2분 후 다시 켜짐."},
                {"i":"⚙️","t":"RC 모델링","d":"R₁-C₁ 병렬 서브회로. τ=R₁C₁≈600s."},
                {"i":"💻","t":"ZOH 이산화","d":"F₁=exp(-Δt/τ). 오일러보다 수치적으로 안정."}],
    }
    kp_list = KP_DATA.get(tp["id"], [{"i":"📖","t":"핵심 포인트","d":tp["desc"]}] * 4)

    tabs = st.tabs(["📖 개념 설명", "🔢 핵심 수식", "📊 AI 그래프", "📋 비교 분석", "📄 참고문헌"])
    with tabs[0]:
        kc = st.columns(2)
        for ki, kp in enumerate(kp_list[:4]):
            with kc[ki % 2]:
                st.markdown(f'<div class="kp-card"><div class="kp-icon">{kp["i"]}</div><div class="kp-t">{kp["t"]}</div><div class="kp-d">{kp["d"]}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**{tp['title']}** — {tp['desc']}")

    with tabs[1]:
        EQ_MAP = {
            "t01": [{"t":"이상 전압원","c":"v(t) = OCV(z(t))  // i=0 가정"},{"t":"온도 보정","c":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)"}],
            "t02": [{"t":"연속시간 상태방정식","c":"ż(t) = −η(t)·i(t) / Q"},{"t":"이산시간 점화식 (식 2.4)","c":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"}],
            "t03": [{"t":"단자 전압","c":"v(t) = OCV(z) − i(t)·R₀"},{"t":"R₀ 추출","c":"R₀ = |ΔV₀/Δi| = 8.2 mΩ"}],
            "t04": [{"t":"ZOH 이산화 (식 2.8)","c":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)"},{"t":"단자 전압","c":"v[k] = OCV(z) − R₁·i_R1[k] − R₀·i[k]"}],
            "t08": [{"t":"ESC 출력방정식","c":"v[k] = OCV(z,T) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]"}],
        }
        eqs = EQ_MAP.get(tp["id"], [{"t":"핵심 수식","c":"해당 섹션 교재 참조"}])
        for eq in eqs:
            st.markdown(f"**{eq['t']}**")
            st.markdown(f'<div class="eq-box">{eq["c"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

    with tabs[2]:
        bg_c = "#1e293b"
        gc = "rgba(45,212,191,.06)"
        lyt = dict(paper_bgcolor=bg_c, plot_bgcolor=bg_c,
                   font=dict(family="Noto Sans KR", color="#94a3b8", size=11),
                   margin=dict(l=40,r=20,t=36,b=36), height=280,
                   legend=dict(orientation="h",y=-0.22),
                   xaxis=dict(gridcolor=gc,color="#64748b",zerolinecolor=gc),
                   yaxis=dict(gridcolor=gc,color="#64748b",zerolinecolor=gc))
        fig = None
        if tp["id"] == "t01":
            sx = [i/10 for i in range(11)]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sx, y=[3.0,3.40,3.65,3.75,3.82,3.89,3.97,4.05,4.12,4.18,4.20], name="NMC", line=dict(color=TEAL,width=2.5)))
            fig.add_trace(go.Scatter(x=sx, y=[2.8,3.20,3.30,3.32,3.33,3.33,3.34,3.35,3.36,3.50,3.65], name="LFP", line=dict(color="#60a5fa",width=2.5,dash="dash")))
            fig.update_layout(**lyt, title="OCV vs SoC (NMC/LFP)", xaxis_title="SoC", yaxis_title="OCV (V)")
        elif tp["id"] == "t04":
            t_rc=list(range(81)); irc=0.0; vo,oc=[],[]
            for tt in t_rc:
                oc.append(4.1)
                if tt<5: vo.append(4.1); irc=0.0
                else:
                    F=math.exp(-1/(0.0158*38000)); irc=F*irc+(1-F)*5.0
                    vo.append(4.1-0.0158*irc-0.0082*5.0)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t_rc,y=oc,name="OCV",line=dict(color="#ef4444",dash="dash",width=1.5)))
            fig.add_trace(go.Scatter(x=t_rc,y=vo,name="V(t)",fill="tonexty",fillcolor="rgba(45,212,191,.07)",line=dict(color=TEAL,width=2.5)))
            fig.update_layout(**lyt, title="RC 확산 전압 응답(I=5A)", xaxis_title="시간(s)", yaxis_title="전압(V)")
        elif tp["id"] == "t06":
            omega=np.logspace(4,-4,400); rez,imz=[],[]
            for w in omega:
                jw=complex(0,w); Z=0.0082+0.0158/(1+jw*0.0158*38000)+0.002/(complex(0,1)**0.5*w**0.5)
                rez.append(Z.real*1000); imz.append(-Z.imag*1000)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=rez,y=imz,mode="lines",name="임피던스",line=dict(color=TEAL,width=2.5)))
            fig.update_layout(**lyt, title="나이키스트 플롯 (EIS)", xaxis_title="Re(Z) mΩ", yaxis_title="-Im(Z) mΩ")
        elif tp["id"] == "t07":
            sh2=np.linspace(0,1,11)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(sh2),y=[2.8,3.3,3.34,3.35,3.36,3.37,3.38,3.40,3.45,3.5,3.65],name="충전 OCV",line=dict(color=TEAL,width=2.5)))
            fig.add_trace(go.Scatter(x=list(sh2),y=[2.8,3.2,3.27,3.28,3.29,3.30,3.31,3.33,3.38,3.44,3.60],name="방전 OCV",line=dict(color="#60a5fa",width=2.5,dash="dash")))
            fig.update_layout(**lyt, title="히스테리시스 루프(LFP)", xaxis_title="SoC", yaxis_title="OCV(V)")
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("이 섹션의 그래프는 핵심 수식 탭의 시뮬레이터로 확인하세요.")

    with tabs[3]:
        COMP_MAP = {
            "t01": {"h":["항목","NMC","LFP"],"r":[["OCV 형태","단조 S곡선","극평탄(3.33V)"],["히스테리시스","<10mV","50~100mV"],["SoC 추정 난이도","보통","어려움"]]},
            "t03": {"h":["온도","R₀ 배수","현상"],"r":[["−30°C","~5배","시동 불가"],["0°C","~3배","주행거리 급감"],["25°C","기준","정상"],["45°C","~0.8배","성능 향상"]]},
        }
        comp = COMP_MAP.get(tp["id"])
        if comp:
            st.dataframe(pd.DataFrame(comp["r"], columns=comp["h"]), use_container_width=True, hide_index=True)
        else: st.info("비교 표가 없습니다.")

    with tabs[4]:
        for p in PAPERS[:3]:
            st.markdown(f"""
            <div class="paper-card">
                <div class="paper-num">{p['idx']}</div>
                <div style="flex:1;">
                    <span class="paper-tag">{p['tag']}</span>
                    <div class="paper-title">{p['title']}</div>
                    <div class="paper-authors">{p['authors']}</div>
                    <div class="paper-journal">{p['journal']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Nav buttons
    pp, pn = st.columns(2)
    with pp:
        if si > 0 and st.button(f"← {TOPICS[si-1]['title']}", use_container_width=True, key="prev"):
            S.sel_topic = TOPICS[si-1]["id"]; st.rerun()
    with pn:
        if si < len(TOPICS)-1 and st.button(f"{TOPICS[si+1]['title']} →", use_container_width=True, key="nxt"):
            S.sel_topic = TOPICS[si+1]["id"]; st.rerun()

    with st.expander("🗂 전체 14개 주제 목록"):
        ac = st.columns(4)
        for ti, t in enumerate(TOPICS):
            with ac[ti % 4]:
                done2 = S.progress.get(t["id"], False)
                if st.button(f"{'✅' if done2 else '⬜'} {t['num']}. {t['title']}", key=f"all_{t['id']}", use_container_width=True):
                    S.sel_topic = t["id"]; st.rerun()

# ══════════════════════════════════════════════════════════════
#  NEWS PAGE
# ══════════════════════════════════════════════════════════════
elif S.page == "news":
    st.markdown(f"""
    <div style="padding:40px 0 20px;">
        <div class="sec-eyebrow">최신 뉴스</div>
        <div style="font-size:52px;font-weight:900;color:{NAVY};letter-spacing:-.03em;margin-bottom:36px;">뉴스룸</div>
    </div>
    """, unsafe_allow_html=True)
    nc = st.columns(4, gap="medium")
    news_img_colors = [((15,25,45),(8,15,30)),((25,45,25),(12,28,12)),((15,20,40),(8,10,25)),((35,20,50),(20,10,35))]
    for ni, news in enumerate(NEWS):
        c1n,c2n=news_img_colors[ni%len(news_img_colors)]
        nw,nh=400,300; nimg=Image.new("RGB",(nw,nh)); ndraw=ImageDraw.Draw(nimg)
        for y in range(nh):
            t=y/nh; ndraw.line([(0,y),(nw,y)],fill=tuple(int(c1n[k]+t*(c2n[k]-c1n[k])) for k in range(3)))
        nb64=_b64(nimg)
        with nc[ni]:
            st.markdown(f"""
            <div class="news-card">
                <div class="news-card-img"><img src="data:image/png;base64,{nb64}"></div>
                <div class="news-date">{news['date']}</div>
                <div class="news-card-title">{news['title']}</div>
                <div class="news-source">{news['source']}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  EQUATIONS PAGE
# ══════════════════════════════════════════════════════════════
elif S.page == "equations":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:20px;">🔢 핵심 수식 모음</div>', unsafe_allow_html=True)
    EQS = [
        {"n":"식 2.1","c":TEAL,"t":"SoC 연속시간","code":"ż(t) = −η(t)·i(t) / Q"},
        {"n":"식 2.4","c":"#60a5fa","t":"SoC 이산시간","code":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"},
        {"n":"식 2.8","c":"#34d399","t":"RC 이산화 (ZOH)","code":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)"},
        {"n":"ESC 출력","c":"#fbbf24","t":"ESC 단자 전압","code":"v[k] = OCV(z,T) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]"},
        {"n":"히스테리시스","c":"#a78bfa","t":"동적 히스테리시스","code":"h[k+1] = exp(−|η·i·γ·Δt/Q|)·h[k]\n       − (1−exp(···))·sgn(i[k])"},
        {"n":"OCV 온도","c":"#f87171","t":"OCV 온도 보정","code":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)"},
    ]
    ec = st.columns(2)
    for ei, eq in enumerate(EQS):
        with ec[ei % 2]:
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid {BD};border-left:4px solid {eq['c']};
                 border-radius:10px;padding:16px;margin-bottom:14px;">
                <div style="font-family:'Roboto Mono',monospace;font-size:9px;font-weight:700;
                     color:{eq['c']};letter-spacing:.12em;margin-bottom:5px;">{eq['n']}</div>
                <div style="font-size:14px;font-weight:700;color:{NAVY};margin-bottom:8px;">{eq['t']}</div>
                <div class="eq-box">{eq['code'].replace(chr(10),'<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f'<div style="font-size:18px;font-weight:700;color:{NAVY};margin-bottom:12px;">📊 전압 응답 시뮬레이터</div>', unsafe_allow_html=True)
    es1, es2 = st.columns([1, 1.5])
    with es1:
        sI = st.slider("I (A)", 1.0, 100.0, 20.0, 1.0, key="eI")
        sR0 = st.slider("R₀ (mΩ)", 1.0, 50.0, 8.2, 0.1, key="eR0")
        sR1 = st.slider("R₁ (mΩ)", 1.0, 50.0, 15.8, 0.1, key="eR1")
        sC1 = st.slider("C₁ (kF)", 1.0, 100.0, 38.0, 1.0, key="eC1")
        tau_e = (sR1/1000)*(sC1*1000)
        st.info(f"τ = {tau_e:.0f}s | 4τ = {4*tau_e:.0f}s ({4*tau_e/60:.1f}분)")
    with es2:
        ts = list(range(81)); irc_e=0.0; vs,oc=[],[]
        for tt in ts:
            oc.append(4.1)
            if tt<5: vs.append(4.1); irc_e=0.0
            else:
                F=math.exp(-1/((sR1/1000)*(sC1*1000))); irc_e=F*irc_e+(1-F)*sI
                vs.append(4.1-(sR1/1000)*irc_e-(sR0/1000)*sI)
        fg=go.Figure()
        fg.add_trace(go.Scatter(x=ts,y=oc,name="OCV",line=dict(color="#ef4444",dash="dash",width=1.5)))
        fg.add_trace(go.Scatter(x=ts,y=vs,name="V(t)",fill="tonexty",fillcolor="rgba(45,212,191,.06)",line=dict(color=TEAL,width=2.5)))
        fg.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                         font=dict(color=GRAY),margin=dict(l=40,r=20,t=40,b=36),height=270,
                         legend=dict(orientation="h",y=-0.25),
                         xaxis=dict(gridcolor=BD,color=LGRAY),yaxis=dict(gridcolor=BD,color=LGRAY),
                         title=f"V(t) | I={sI}A τ={tau_e:.0f}s",xaxis_title="시간(s)",yaxis_title="전압(V)")
        st.plotly_chart(fg, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  QUIZ PAGE
# ══════════════════════════════════════════════════════════════
elif S.page == "quiz":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:20px;">📝 이해도 퀴즈</div>', unsafe_allow_html=True)
    rc, _ = st.columns([1, 5])
    with rc:
        if st.button("🔄 다시 시작", key="qr"):
            S.quiz_idx=0; S.quiz_score=0; S.quiz_answered=False; S.quiz_done=False; st.rerun()
    if S.quiz_done:
        pct = int(S.quiz_score/len(QUIZ)*100)
        msg = "🏆 완벽!" if pct==100 else "👍 훌륭합니다!" if pct>=70 else "📚 다시 복습해보세요."
        st.markdown(f"""
        <div style="background:rgba(45,212,191,.08);border:1px solid rgba(45,212,191,.3);
             border-radius:16px;padding:40px;text-align:center;">
            <div style="font-size:52px;margin-bottom:14px;">🎉</div>
            <div style="font-family:'Roboto Mono',monospace;font-size:48px;font-weight:800;color:{TEAL};">{S.quiz_score} / {len(QUIZ)}</div>
            <div style="font-size:16px;color:{GRAY};margin-top:12px;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        idx=S.quiz_idx; q=QUIZ[idx]
        st.progress(idx/len(QUIZ), text=f"문제 {idx+1}/{len(QUIZ)} · 점수: {S.quiz_score}점")
        st.markdown(f"### Q{idx+1}. {q['q']}")
        if not S.quiz_answered:
            for oi, opt in enumerate(q["opts"]):
                if st.button(f"{chr(65+oi)}. {opt}", key=f"qo{idx}_{oi}", use_container_width=True):
                    S.quiz_answered=True; S.quiz_sel=oi
                    if oi==q["ans"]: S.quiz_score+=1
                    st.rerun()
            if st.button("⏭ 건너뛰기", key=f"sk{idx}"):
                S.quiz_answered=True; S.quiz_sel=-1; st.rerun()
        else:
            sel=S.quiz_sel
            for oi, opt in enumerate(q["opts"]):
                lb=f"{chr(65+oi)}. {opt}"
                if oi==q["ans"]: st.success(f"✅ {lb}")
                elif oi==sel: st.error(f"❌ {lb}")
                else: st.markdown(f'<div style="padding:9px 12px;border:1px solid {BD};border-radius:7px;color:{GRAY};margin:3px 0;">{lb}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(45,212,191,.08);border-left:3px solid {TEAL};border-radius:0 8px 8px 0;padding:12px;margin:10px 0;">
                <b>💡 해설:</b> {q['exp']}
                <div class="eq-box" style="margin-top:8px;">{q['f']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("다음 문제 →", type="primary", use_container_width=True, key=f"nx{idx}"):
                S.quiz_idx+=1; S.quiz_answered=False
                if S.quiz_idx>=len(QUIZ): S.quiz_done=True
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  BOOKMARKS PAGE
# ══════════════════════════════════════════════════════════════
elif S.page == "bookmarks":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:20px;">🔖 북마크 ({len(S.bookmarks)}건)</div>', unsafe_allow_html=True)
    if not S.bookmarks:
        st.info("북마크한 항목이 없습니다. 주제별 학습 페이지에서 ☆ 버튼을 눌러 추가하세요.")
    else:
        for bm_id in S.bookmarks:
            tp_bm = next((t for t in TOPICS if t["id"]==bm_id), None)
            if tp_bm:
                b1, b2, b3 = st.columns([4, 1, 1])
                with b1: st.markdown(f"**Section {tp_bm['num']}: {tp_bm['title']}** — {tp_bm['desc']}")
                with b2:
                    if st.button("열기", key=f"bo_{bm_id}", use_container_width=True):
                        S.sel_topic=bm_id; S.page="topics"; st.rerun()
                with b3:
                    if st.button("삭제 ✕", key=f"bd_{bm_id}", use_container_width=True):
                        S.bookmarks.remove(bm_id); st.rerun()
                st.markdown(f'<hr style="border-color:{BD};margin:8px 0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  NOTICES PAGE
# ══════════════════════════════════════════════════════════════
elif S.page == "notices":
    st.markdown(f'<div style="font-size:32px;font-weight:900;color:{NAVY};margin-bottom:20px;">📢 공지사항</div>', unsafe_allow_html=True)
    nt = st.radio("", ["공지사항", "업데이트", "Q&A"], horizontal=True, key="ntab", label_visibility="collapsed")
    st.markdown("---")
    for n in S.notices:
        ntype=n["type"]
        if nt=="공지사항" and ntype!="공지": continue
        if nt=="업데이트" and ntype!="업데이트": continue
        if nt=="Q&A" and ntype!="Q&A": continue
        tc3="#1d4ed8" if ntype=="공지" else ("#166534" if ntype=="업데이트" else "#92400e")
        bc3="rgba(37,99,235,.08)" if ntype=="공지" else ("rgba(22,163,74,.08)" if ntype=="업데이트" else "rgba(245,158,11,.08)")
        st.markdown(f"""
        <div style="background:#fff;border:1px solid {BD};border-radius:10px;padding:14px 16px;margin-bottom:9px;">
            <span style="background:{bc3};color:{tc3};border:1px solid {tc3}33;font-size:10px;font-weight:700;
                 padding:2px 8px;border-radius:20px;font-family:'Roboto Mono',monospace;letter-spacing:.06em;
                 display:inline-block;margin-bottom:7px;">{ntype}</span>
            <div style="font-size:14px;font-weight:700;color:{NAVY};margin-bottom:4px;">{n['title']}</div>
            <div style="font-size:13px;color:{GRAY};margin-bottom:5px;">{n['body']}</div>
            <div style="font-family:'Roboto Mono',monospace;font-size:10px;color:{LGRAY};">{n['date']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ✍️ 새 공지 작성")
    with st.form("nf"):
        ns = st.selectbox("분류", ["공지", "업데이트", "Q&A"], key="nts")
        nt2 = st.text_input("제목", key="ntt")
        nb = st.text_area("내용", key="ntb")
        if st.form_submit_button("✅ 게시", use_container_width=True):
            if nt2 and nb:
                S.notices.insert(0, {"type": ns, "title": nt2, "body": nb, "date": datetime.now().strftime("%Y-%m-%d")})
                st.success("공지가 게시되었습니다!"); st.rerun()
