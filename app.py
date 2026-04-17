"""
ECM 등가회로 모델 연구포털
battery_research_app 디자인 기반 + app ECM 콘텐츠 통합
"""
import streamlit as st
import feedparser
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import math
import urllib.parse
from datetime import datetime

try:
    from scholarly import scholarly
    HAS_SCHOLARLY = True
except Exception:
    HAS_SCHOLARLY = False

st.set_page_config(
    page_title="ECM 등가회로 모델 연구포털",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS (battery_research_app 스타일) ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

:root {
    --teal:  #00B4A0;
    --teal2: #009688;
    --navy:  #0D1B2A;
    --navy2: #1C2E40;
    --gray1: #F7F8FA;
    --gray2: #EEF0F3;
    --gray3: #D4D8DE;
    --gray4: #9EA5AF;
    --gray5: #6B7280;
    --white: #FFFFFF;
    --black: #0D1B2A;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Noto Sans KR','Plus Jakarta Sans',-apple-system,sans-serif;
    background: var(--white);
    color: var(--black);
}

.stApp { background: var(--white) !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stAppViewBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* 버튼 공통 */
.stButton > button {
    background: transparent !important;
    color: var(--navy) !important;
    border: 1px solid var(--gray3) !important;
    border-radius: 2px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: var(--teal) !important;
    color: var(--white) !important;
    border-color: var(--teal) !important;
}
.stTabs [data-baseweb="tab-list"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; background: transparent !important; border: none !important; }
textarea {
    background: var(--gray1) !important;
    color: var(--black) !important;
    border: 1px solid var(--gray3) !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
}

/* GNB */
.gnb {
    position: fixed; top: 0; left: 0; right: 0;
    height: 68px;
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--gray3);
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0 52px;
    z-index: 9999;
}
.gnb-logo {
    display: flex; align-items: center; gap: 10px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800; font-size: 1.1rem;
    color: var(--navy); letter-spacing: -0.3px;
}
.gnb-logo-mark {
    width: 32px; height: 32px;
    background: var(--teal);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; color: white;
}
.gnb-menu {
    display: flex; gap: 36px; list-style: none;
    font-size: 0.82rem; font-weight: 500; color: var(--gray5);
}
.gnb-menu li { cursor: pointer; transition: color 0.2s; }
.gnb-menu li:hover { color: var(--teal); }
.gnb-right { font-size: 0.75rem; color: var(--gray4); }

/* HERO */
.hero-wrap {
    position: relative; width: 100%;
    height: 100vh; min-height: 680px;
    overflow: hidden;
    background: var(--navy);
}
.hero-video-wrap { position: absolute; inset: 0; overflow: hidden; }
.hero-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(13,27,42,0.25) 0%,
        rgba(13,27,42,0.1) 40%,
        rgba(13,27,42,0.65) 80%,
        rgba(13,27,42,0.95) 100%
    );
}
.hero-content {
    position: absolute; bottom: 80px; left: 72px;
    z-index: 2; max-width: 760px;
}
.hero-eyebrow {
    display: flex; align-items: center; gap: 10px;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--teal); margin-bottom: 18px;
}
.hero-eyebrow::before {
    content: ''; display: block;
    width: 28px; height: 1px; background: var(--teal);
}
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.4rem,5vw,4rem);
    font-weight: 800; color: var(--white);
    line-height: 1.1; letter-spacing: -1.5px;
    margin-bottom: 18px;
}
.hero-title span { color: var(--teal); }
.hero-desc {
    font-size: 1rem; color: rgba(255,255,255,0.65);
    font-weight: 300; line-height: 1.75;
    margin-bottom: 32px; max-width: 520px;
}
.hero-scroll {
    position: absolute; bottom: 32px; right: 52px;
    display: flex; flex-direction: column;
    align-items: center; gap: 6px; z-index: 2;
    font-size: 0.62rem; letter-spacing: 2px;
    color: rgba(255,255,255,0.4); text-transform: uppercase;
}
.hero-scroll-line {
    width: 1px; height: 44px;
    background: linear-gradient(to bottom, rgba(255,255,255,0.4), transparent);
    animation: scrollLine 2s ease-in-out infinite;
}
@keyframes scrollLine {
    0%,100% { opacity:0.4; transform:scaleY(1); }
    50%      { opacity:1;   transform:scaleY(0.6); }
}

/* 섹션 공통 */
.sec { padding: 100px 72px; }
.sec-white  { background: var(--white); }
.sec-gray   { background: var(--gray1); }
.sec-navy   { background: var(--navy); color: var(--white); }
.sec-label {
    display: flex; align-items: center; gap: 10px;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--teal); margin-bottom: 16px;
}
.sec-label::before {
    content:''; display:block;
    width:24px; height:1px; background: var(--teal);
}
.sec-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(1.8rem,4vw,3rem);
    font-weight: 800; line-height: 1.15;
    letter-spacing: -0.8px; margin-bottom: 16px;
    color: var(--navy);
}
.sec-desc {
    font-size: 0.95rem; color: var(--gray5);
    font-weight: 300; line-height: 1.8;
    max-width: 520px;
}

/* WHY 섹션 */
.why-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 80px; margin-top: 64px; align-items: center;
}
.why-img-wrap {
    border-radius: 4px; overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,180,160,0.12);
}
.why-img-wrap img {
    width: 100%; height: 460px;
    object-fit: cover; display: block;
    transition: transform 0.5s ease;
}
.why-img-wrap:hover img { transform: scale(1.03); }
.why-points { display: flex; flex-direction: column; gap: 36px; }
.why-point {
    display: flex; gap: 22px; align-items: flex-start;
    padding-bottom: 36px;
    border-bottom: 1px solid var(--gray2);
    transition: border-color 0.2s;
}
.why-point:hover { border-bottom-color: var(--teal); }
.why-point:last-child { border-bottom: none; padding-bottom: 0; }
.why-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem; font-weight: 800;
    color: var(--teal); opacity: 0.5;
    min-width: 36px; line-height: 1;
}
.why-point-title {
    font-size: 1rem; font-weight: 700;
    color: var(--navy); margin-bottom: 7px;
    letter-spacing: -0.2px;
}
.why-point-desc {
    font-size: 0.84rem; color: var(--gray5);
    line-height: 1.7; font-weight: 300;
}

/* STATS */
.stats-row {
    background: var(--teal);
    padding: 56px 72px;
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 40px;
}
.stat-item { text-align: center; }
.stat-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.8rem; font-weight: 800;
    color: var(--white); letter-spacing: -2px;
    line-height: 1; margin-bottom: 8px;
}
.stat-num span { font-size: 1.6rem; }
.stat-label { font-size: 0.78rem; color: rgba(255,255,255,0.75); letter-spacing: 0.3px; }

/* TECH 패널 */
.tech-panel {
    position: relative; overflow: hidden;
    height: 420px; cursor: pointer;
    background: var(--navy2);
}
.tech-panel img {
    position: absolute; inset: 0;
    width: 100%; height: 100%;
    object-fit: cover; filter: brightness(0.45);
    transition: transform 0.5s ease, filter 0.3s;
}
.tech-panel:hover img { transform: scale(1.04); filter: brightness(0.55); }
.tech-panel-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(13,27,42,0.92) 0%, rgba(13,27,42,0.2) 60%, transparent 100%);
}
.tech-panel-top {
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px; background: var(--teal);
    transform: scaleX(0); transform-origin: left;
    transition: transform 0.4s ease;
}
.tech-panel:hover .tech-panel-top { transform: scaleX(1); }
.tech-panel-body {
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 32px 28px; z-index: 2;
}
.tech-panel-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 3px; color: var(--teal);
    text-transform: uppercase; margin-bottom: 8px;
}
.tech-panel-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.3rem; font-weight: 700;
    color: var(--white); line-height: 1.3;
    margin-bottom: 6px;
}
.tech-panel-sub {
    font-size: 0.78rem; color: var(--teal);
    font-weight: 600; margin-bottom: 10px;
}
.tech-panel-desc {
    font-size: 0.82rem; color: rgba(255,255,255,0.6);
    line-height: 1.6; font-weight: 300; margin-bottom: 18px;
}
.tech-panel-arrow {
    font-size: 0.78rem; color: rgba(255,255,255,0.4);
    font-weight: 500; letter-spacing: 0.5px;
    transition: color 0.2s;
}
.tech-panel:hover .tech-panel-arrow { color: var(--teal); }

/* 뉴스 카드 */
.news-card-lg {
    border: 1px solid var(--gray2);
    border-radius: 4px; overflow: hidden;
    background: var(--white);
    transition: box-shadow 0.2s;
}
.news-card-lg:hover {
    box-shadow: 0 8px 32px rgba(0,180,160,0.1);
}
.news-card-img-wrap {
    overflow: hidden; height: 180px;
}
.news-card-img {
    width: 100%; height: 180px;
    object-fit: cover; display: block;
    transition: transform 0.4s ease;
}
.news-card-lg:hover .news-card-img { transform: scale(1.04); }
.news-card-body { padding: 18px 16px; }
.news-card-date {
    font-size: 0.68rem; color: var(--gray4);
    letter-spacing: 0.5px; margin-bottom: 8px;
}
.news-card-title {
    font-size: 0.88rem; font-weight: 600;
    color: var(--navy); line-height: 1.5;
    margin-bottom: 8px;
}
.news-card-title a {
    color: var(--navy); text-decoration: none;
}
.news-card-title a:hover { color: var(--teal); }
.news-card-source { font-size: 0.72rem; color: var(--gray4); }

/* 논문 카드 */
.paper-card {
    display: flex; gap: 20px;
    border: 1px solid var(--gray2);
    border-radius: 4px;
    padding: 20px 22px;
    margin-bottom: 12px;
    background: var(--white);
    transition: border-color 0.2s;
}
.paper-card:hover { border-color: var(--teal); }
.paper-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.6rem; font-weight: 800;
    color: var(--teal); opacity: 0.4;
    min-width: 36px; line-height: 1;
}
.paper-tag {
    display: inline-block;
    background: rgba(0,180,160,0.08);
    color: var(--teal);
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    padding: 2px 8px; border-radius: 2px;
    margin-bottom: 6px;
}
.paper-title {
    font-size: 0.92rem; font-weight: 700;
    color: var(--navy); margin-bottom: 4px;
    line-height: 1.4;
}
.paper-authors { font-size: 0.78rem; color: var(--gray4); margin-bottom: 3px; }
.paper-journal { font-size: 0.76rem; color: var(--gray5); margin-bottom: 6px; }
.paper-desc { font-size: 0.8rem; color: var(--gray5); line-height: 1.6; margin-bottom: 8px; }
.paper-doi {
    font-size: 0.75rem; color: var(--teal);
    text-decoration: none; font-weight: 600;
}
.paper-doi:hover { text-decoration: underline; }

/* 주제 그리드 */
.topic-nav-grid {
    background: var(--navy);
    padding: 56px 72px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background-color: rgba(255,255,255,0.06);
}
.topic-nav-cell {
    background: var(--navy2);
    padding: 24px 22px;
    cursor: pointer;
    transition: background 0.2s;
    position: relative;
}
.topic-nav-cell:hover { background: #243548; }
.tnc-num {
    font-size: 0.65rem; font-weight: 700;
    color: var(--teal); letter-spacing: 2px;
    margin-bottom: 8px; text-transform: uppercase;
}
.tnc-title {
    font-size: 0.88rem; font-weight: 600;
    color: var(--white); line-height: 1.4;
    transition: color 0.2s;
}
.topic-nav-cell:hover .tnc-title { color: var(--teal); }
.tnc-arrow {
    position: absolute; right: 18px; top: 50%;
    transform: translateY(-50%);
    color: rgba(255,255,255,0.15); font-size: 0.9rem;
    transition: all 0.2s;
}
.topic-nav-cell:hover .tnc-arrow {
    color: var(--teal);
    transform: translateY(-50%) translateX(3px);
}

/* 키포인트 카드 */
.kp-card {
    background: var(--gray1);
    border: 1px solid var(--gray2);
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.kp-card:hover { border-color: var(--teal); }
.kp-icon { font-size: 1.4rem; margin-bottom: 8px; }
.kp-title { font-size: 0.85rem; font-weight: 700; color: var(--navy); margin-bottom: 5px; }
.kp-desc { font-size: 0.8rem; color: var(--gray5); line-height: 1.6; }

/* 수식 박스 */
.eq-box {
    background: var(--navy);
    color: #a5f3fc;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'Roboto Mono','Courier New', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    letter-spacing: 0.02em;
    margin: 8px 0 16px;
    border-left: 3px solid var(--teal);
    white-space: pre-wrap;
}

/* 퀴즈 */
.quiz-progress { margin-bottom: 20px; }

/* 다크 배너 */
.dark-banner {
    position: relative; width: 100%;
    min-height: 480px; overflow: hidden;
    display: flex; align-items: center;
    justify-content: center;
    background: var(--navy);
}
.dark-banner video {
    position: absolute; inset: 0;
    width: 100%; height: 100%;
    object-fit: cover; filter: brightness(0.28);
}
.dark-banner-overlay {
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at center, rgba(0,180,160,0.08) 0%, rgba(13,27,42,0.6) 70%);
}
.dark-banner-body {
    position: relative; z-index: 2;
    text-align: center; padding: 80px 48px;
    max-width: 900px;
}
.dark-banner-label {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--teal); margin-bottom: 24px;
    display: flex; align-items: center;
    justify-content: center; gap: 10px;
}
.dark-banner-label::before, .dark-banner-label::after {
    content: ''; display: block;
    width: 32px; height: 1px; background: var(--teal);
}
.dark-banner-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(1.8rem,4vw,3rem);
    font-weight: 800; color: var(--white);
    line-height: 1.25; letter-spacing: -1px;
    margin-bottom: 20px;
}
.dark-banner-title span { color: var(--teal); }
.dark-banner-desc {
    font-size: 1rem; color: rgba(255,255,255,0.55);
    font-weight: 300; line-height: 1.8;
}

/* 진행 사이드바 */
.side-w {
    background: var(--gray1);
    border: 1px solid var(--gray2);
    border-radius: 4px;
    padding: 18px 16px;
    margin-bottom: 12px;
}
.side-w-title {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--gray4); margin-bottom: 12px;
}
.prog-item {
    display: flex; align-items: center; gap: 10px;
    font-size: 0.82rem; margin-bottom: 10px;
}
.prog-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--gray3); flex-shrink: 0;
}
.prog-dot.on { background: var(--teal); }
.kw-chip {
    display: inline-block;
    background: rgba(0,180,160,0.08);
    color: var(--teal);
    font-size: 0.72rem; font-weight: 600;
    padding: 3px 9px; border-radius: 20px;
    margin: 2px 3px 2px 0;
    border: 1px solid rgba(0,180,160,0.2);
}

/* 상세 화면 히어로 */
.detail-hero {
    background: var(--navy);
    padding: 72px 72px 48px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.detail-crumb {
    font-size: 0.72rem; color: rgba(255,255,255,0.35);
    margin-bottom: 14px; letter-spacing: 0.3px;
}
.detail-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(1.8rem,4vw,2.8rem);
    font-weight: 800; color: var(--white);
    letter-spacing: -1px; line-height: 1.15; margin-bottom: 10px;
}
.detail-sub {
    font-size: 1rem; color: var(--teal);
    font-weight: 600; margin-bottom: 14px;
}
.detail-kws { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.d-kw {
    background: rgba(0,180,160,0.12);
    color: var(--teal);
    border: 1px solid rgba(0,180,160,0.25);
    font-size: 0.72rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.5px;
}

/* 탭 바 */
.dtab-bar {
    display: flex; gap: 0;
    border-bottom: 1px solid var(--gray2);
    padding: 0 72px;
    background: var(--white);
    margin-bottom: 0;
}
.dtab {
    font-size: 0.82rem; font-weight: 500;
    color: var(--gray4); padding: 14px 20px;
    cursor: pointer; border-bottom: 2px solid transparent;
    transition: all 0.2s; letter-spacing: 0.2px;
}
.dtab.on { color: var(--teal); border-bottom-color: var(--teal); font-weight: 600; }
.dtab:hover { color: var(--teal); }

/* 푸터 */
.footer {
    background: var(--navy);
    padding: 48px 72px;
    display: flex; align-items: center;
    justify-content: space-between;
}
.footer-logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem; font-weight: 800;
    color: var(--white);
}
.footer-logo span { color: var(--teal); }
.footer-copy { font-size: 0.72rem; color: rgba(255,255,255,0.3); }

/* 보고서 */
.report-area {
    background: var(--gray1);
    border: 1px solid var(--gray2);
    border-radius: 4px;
    padding: 24px;
    font-size: 0.85rem;
    line-height: 1.8;
    color: var(--black);
    white-space: pre-wrap;
    font-family: 'Noto Sans KR', sans-serif;
    max-height: 600px;
    overflow-y: auto;
}

/* GNB 스트림릿 버튼용 */
.stApp > div > div > div > div:first-child [data-testid="stHorizontalBlock"] {
    position: fixed !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    z-index: 9999 !important;
    background: rgba(255,255,255,0.97) !important;
    backdrop-filter: blur(10px) !important;
    border-bottom: 1px solid #D4D8DE !important;
    padding: 0 !important; margin: 0 !important;
    height: 64px !important;
    align-items: center !important;
    gap: 0 !important;
}
[data-testid="stHorizontalBlock"]:first-of-type button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: #6B7280 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    padding: 0 20px !important;
    height: 64px !important;
    width: 100% !important;
    letter-spacing: 0.2px !important;
    transition: color 0.15s !important;
}
[data-testid="stHorizontalBlock"]:first-of-type button:hover {
    color: #00B4A0 !important;
    background: transparent !important;
    border-bottom: 2px solid #00B4A0 !important;
}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:first-child button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    color: #0D1B2A !important;
    justify-content: flex-start !important;
    padding-left: 28px !important;
}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:first-child button:hover {
    color: #0D1B2A !important;
    border-bottom: none !important;
}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:last-child { flex: 2 !important; }
</style>
""", unsafe_allow_html=True)

# ── 색상 상수 ──────────────────────────────────────────────────
TEAL  = "#00B4A0"
NAVY  = "#0D1B2A"
GRAY  = "#6B7280"
LGRAY = "#9EA5AF"
BD    = "#D4D8DE"
BG2   = "#F7F8FA"

# ── SESSION STATE ──────────────────────────────────────────────
DEFAULTS = {
    "page": "home",
    "sel_topic_id": "t01",
    "tab": "concepts",
    "quiz_idx": 0,
    "quiz_score": 0,
    "quiz_ans": False,
    "quiz_done": False,
    "quiz_sel": -1,
    "progress": {},
    "bookmarks": [],
    "show_topics_grid": False,
    "home_news": [],
    "nr_news": [],
    "news_fetched": False,
    "notices": [
        {"type": "공지",     "title": "ECM 연구포털 오픈",       "body": "BatteryIQ 스타일 신규 디자인이 적용되었습니다.",           "date": "2026-04-16"},
        {"type": "업데이트", "title": "나이키스트 플롯 추가",     "body": "t06 와버그 섹션에서 EIS 나이키스트 플롯을 확인하세요.", "date": "2026-04-15"},
        {"type": "Q&A",      "title": "MATLAB 툴박스 다운로드", "body": "http://mocha-java.uccs.edu/BMS1/ 에서 무료로 받으실 수 있습니다.", "date": "2026-04-14"},
    ],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def gs(k):    return st.session_state[k]
def ss(k, v): st.session_state[k] = v

# ── TOPICS DATA ────────────────────────────────────────────────
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

PAPERS = [
    {"idx":"01","tag":"교재","title":"Battery Management Systems, Vol.1: Battery Modeling","authors":"Gregory L. Plett","journal":"Artech House, 2015. ISBN: 978-1-60807-650-3","doi":"","url":"https://www.artechhouse.com","desc":"ESC 등가회로 모델의 표준 교재."},
    {"idx":"02","tag":"핵심 논문","title":"Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 1","authors":"G. L. Plett","journal":"Journal of Power Sources, 134(2), 252–261, 2004","doi":"10.1016/j.jpowsour.2004.02.031","url":"https://doi.org/10.1016/j.jpowsour.2004.02.031","desc":"ESC 모델과 EKF를 결합한 SoC 자가 교정 추정법의 원조 논문."},
    {"idx":"03","tag":"리뷰 논문","title":"A review of lithium-ion battery equivalent circuit models","authors":"X. Hu, S. Li, H. Peng","journal":"Journal of Power Sources, 198, 359–367, 2012","doi":"10.1016/j.jpowsour.2011.10.013","url":"https://doi.org/10.1016/j.jpowsour.2011.10.013","desc":"RC 등가회로 모델들의 비교 검토."},
    {"idx":"04","tag":"EIS 분석","title":"A survey of equivalent circuits for describing the electrical behavior of lithium-ion batteries","authors":"A. Seaman, T.-S. Dao, J. McPhee","journal":"Journal of Power Sources, 252, 395–405, 2014","doi":"10.1016/j.jpowsour.2013.11.037","url":"https://doi.org/10.1016/j.jpowsour.2013.11.037","desc":"EIS 임피던스 분석과 와버그 임피던스를 포함한 등가회로 파라미터 추출법."},
    {"idx":"05","tag":"히스테리시스","title":"The thermodynamic origin of hysteresis in insertion batteries","authors":"W. Dreyer et al.","journal":"Nature Materials, 9(5), 448–453, 2010","doi":"10.1038/nmat2718","url":"https://doi.org/10.1038/nmat2718","desc":"LFP 배터리 히스테리시스의 열역학적 기원."},
]

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

TECH_HIGHLIGHTS = [
    {"num":"01","title":"개방회로 전압 (OCV)","sub":"SoC 추정의 핵심 기준","desc":"전류 i=0에서의 단자 전압. NMC는 S형 곡선, LFP는 극평탄 3.33V를 보입니다.","img":"https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=800&h=500&fit=crop"},
    {"num":"06","title":"와버그 임피던스 & EIS","sub":"나이키스트 플롯 45° 직선","desc":"고체 확산의 주파수 표현. 저주파 영역에서 45° 직선이 나타나는 와버그 임피던스.","img":"https://images.unsplash.com/photo-1509228468518-180dd4864904?w=800&h=500&fit=crop"},
    {"num":"08","title":"향상된 자가 교정 셀 모델","sub":"RMSE=5.37mV 검증 완료","desc":"OCV + R₀ + RC + 히스테리시스를 통합한 완성 모델. EKF와 결합하여 실시간 SoC 추정.","img":"https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&h=500&fit=crop"},
    {"num":"07","title":"히스테리시스 전압","sub":"경로 의존적 이력 현상","desc":"LFP에서 50~100mV에 달하는 이력 현상. SoC 추정 오류의 주원인.","img":"https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&h=500&fit=crop"},
    {"num":"04","title":"확산 전압 (RC 회로)","sub":"ZOH 이산화 RC 분극","desc":"리튬 이온 농도 구배에 의한 느린 동적 전압. τ≈600s (10분).","img":"https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?w=800&h=500&fit=crop"},
    {"num":"13","title":"결론 및 향후 방향","sub":"DFN+ML 하이브리드","desc":"ESC 한계를 넘어 DFN+LSTM 하이브리드로 RMSE≤2mV 목표를 향한 차세대 연구.","img":"https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&h=500&fit=crop"},
]

TECH_ID_MAP = {th["num"]: next(i for i,t in enumerate(TOPICS) if t["num"]==th["num"]) for th in TECH_HIGHLIGHTS}

NEWS_IMGS = [
    "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1543286386-713bdd548da4?w=600&h=300&fit=crop",
    "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=600&h=300&fit=crop",
]

# ── 데이터 수집 함수 ──────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_news(keyword, hl, gl, ceid, n=8):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl={hl}&gl={gl}&ceid={ceid}"
    try:
        entries = feedparser.parse(url).entries[:n]
        return [{"title": e.title, "link": e.link,
                 "published": getattr(e, "published", "")[:10],
                 "source": (getattr(e, "source", None) or {}).get("title", "Google News"),
                 "lang": hl} for e in entries]
    except:
        return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_arxiv(keyword, n=6):
    try:
        q = urllib.parse.quote(keyword)
        url = f"https://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results={n}&sortBy=submittedDate&sortOrder=descending"
        feed = feedparser.parse(url)
        out = []
        for e in feed.entries:
            title = e.get("title","").replace("\n"," ").strip()
            summary = e.get("summary","")[:400].replace("\n"," ").strip()
            pub = e.get("published","")[:10]
            link = e.get("id","") or e.get("link","")
            ar = e.get("authors",[])
            authors = ", ".join(a.get("name","") for a in ar[:3]) if ar else e.get("author","")
            if title: out.append({"title":title,"authors":authors,"abstract":summary,"url":link,"published":pub})
        return out
    except:
        return []

def plot_lyt(title="", xaxis_title="", yaxis_title=""):
    return dict(
        title=dict(text=title, font=dict(size=13, color=NAVY)),
        xaxis_title=xaxis_title, yaxis_title=yaxis_title,
        height=320, paper_bgcolor="white", plot_bgcolor=BG2,
        font=dict(family="Noto Sans KR", size=11, color=NAVY),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=-0.28),
        xaxis=dict(showgrid=True, gridcolor=BD),
        yaxis=dict(showgrid=True, gridcolor=BD),
    )

# ── GNB ───────────────────────────────────────────────────────
logo_col, nav1, nav2, nav3, nav4, nav5, right_col = st.columns([3, 1.1, 1, 1, 1.1, 1.1, 2])

with logo_col:
    if st.button("🔋 ECM 포털", key="gnb_logo"):
        ss("page","home"); st.rerun()
with nav1:
    if st.button("ECM 개요", key="gnb_home"):
        ss("page","home"); st.rerun()
with nav2:
    if st.button("14개 주제", key="gnb_topics"):
        ss("page","topics"); st.rerun()
with nav3:
    if st.button("시뮬레이터", key="gnb_sim"):
        ss("page","simulator"); st.rerun()
with nav4:
    if st.button("퀴즈", key="gnb_quiz"):
        ss("page","quiz"); st.rerun()
with nav5:
    if st.button("공지사항", key="gnb_notices"):
        ss("page","notices"); st.rerun()

st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

page = gs("page")

# =====================================================================
# HOME
# =====================================================================
if page == "home":

    # HERO
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-video-wrap">
            <video autoplay muted loop playsinline
                style="position:absolute;top:50%;left:50%;min-width:100%;min-height:100%;
                       width:auto;height:auto;transform:translate(-50%,-50%);object-fit:cover;">
                <source src="https://raw.githubusercontent.com/rain422/-/main/13814690_1920_1080_100fps.mp4" type="video/mp4">
            </video>
        </div>
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-eyebrow">Battery Management Systems · Plett(2015) Vol.1 · Chapter 2</div>
            <div class="hero-title">ECM<br><span>등가회로 모델</span><br>연구 포털</div>
            <div class="hero-desc">
                OCV · SoC · RC 회로 · 와버그 임피던스 · 히스테리시스 · ESC 모델<br>
                배터리 전기화학의 핵심 14개 주제를 체계적으로 탐구합니다.
            </div>
        </div>
        <div class="hero-scroll">
            <div class="hero-scroll-line"></div>
            <span>SCROLL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # WHY 섹션
    st.markdown("""
    <div class="sec sec-white">
        <div class="sec-label">왜 ECM 등가회로 모델인가</div>
        <div class="why-grid">
            <div class="why-img-wrap" style="position:relative;overflow:hidden;border-radius:4px;">
                <video autoplay muted loop playsinline
                    style="width:100%;height:460px;object-fit:cover;display:block;">
                    <source src="https://raw.githubusercontent.com/rain422/-/main/KakaoTalk_20260413_165858691.mp4" type="video/mp4">
                </video>
            </div>
            <div>
                <div class="sec-title" style="margin-bottom:36px;">배터리 거동을<br>수식으로 이해하는 방법</div>
                <div class="why-points">
                    <div class="why-point">
                        <div class="why-num">01</div>
                        <div>
                            <div class="why-point-title">실시간 구현 가능</div>
                            <div class="why-point-desc">ECM은 계산 비용이 낮아 MCU에서 실시간으로 구현할 수 있습니다. ZOH 이산화로 수치 안정성을 확보합니다.</div>
                        </div>
                    </div>
                    <div class="why-point">
                        <div class="why-num">02</div>
                        <div>
                            <div class="why-point-title">RMSE 5.37mV 검증</div>
                            <div class="why-point-desc">25Ah NMC 셀, UDDS 10시간 프로파일로 검증된 정확도. OCV+R₀+RC+히스테리시스 통합 ESC 모델.</div>
                        </div>
                    </div>
                    <div class="why-point">
                        <div class="why-num">03</div>
                        <div>
                            <div class="why-point-title">EKF와 결합 가능</div>
                            <div class="why-point-desc">ESC+EKF 조합으로 실시간 SoC 자가 교정 추정. 센서 노이즈 환경에서도 ±0.5~1.5% 정확도 달성.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # STATS
    st.markdown("""
    <div class="stats-row">
        <div class="stat-item"><div class="stat-num">14<span>개</span></div><div class="stat-label">핵심 학습 주제</div></div>
        <div class="stat-item"><div class="stat-num">5.37<span>mV</span></div><div class="stat-label">RMSE 검증 성능</div></div>
        <div class="stat-item"><div class="stat-num">3<span>종</span></div><div class="stat-label">전압 성분 (R₀·RC·Hys)</div></div>
        <div class="stat-item"><div class="stat-num">10<span>문항</span></div><div class="stat-label">이해도 퀴즈</div></div>
    </div>
    """, unsafe_allow_html=True)

    # TECH 패널
    st.markdown("""
    <div class="sec sec-gray" style="padding-bottom:0;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;margin-bottom:48px;align-items:end;">
            <div>
                <div class="sec-label">주요 기술</div>
                <div class="sec-title">ECM 등가회로 모델<br>핵심 기술</div>
            </div>
            <div>
                <div class="sec-desc">OCV부터 MATLAB 툴박스까지 — 6가지 핵심 기술을 탐색하세요.<br>패널을 클릭하면 해당 주제 학습 페이지로 이동합니다.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for row_start in range(0, len(TECH_HIGHLIGHTS), 2):
        row = TECH_HIGHLIGHTS[row_start:row_start+2]
        cols = st.columns(2)
        for col, th in zip(cols, row):
            with col:
                st.markdown(f"""
                <div class="tech-panel">
                    <div class="tech-panel-top"></div>
                    <img src="{th['img']}" alt="{th['title']}">
                    <div class="tech-panel-overlay"></div>
                    <div class="tech-panel-body">
                        <div class="tech-panel-num">SECTION {th['num']}</div>
                        <div class="tech-panel-title">{th['title']}</div>
                        <div class="tech-panel-sub">{th['sub']}</div>
                        <div class="tech-panel-desc">{th['desc']}</div>
                        <div class="tech-panel-arrow">자세히 보기 →</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"기술_{th['num']}", key=f"tp_{th['num']}", use_container_width=True):
                    tidx = TECH_ID_MAP.get(th["num"], 0)
                    ss("sel_topic_id", TOPICS[tidx]["id"])
                    ss("page", "topics"); st.rerun()

    st.markdown("<div style='height:8px;background:#f7f8fa;'></div>", unsafe_allow_html=True)

    # 14개 주제 바로가기
    st.markdown("""
    <div class="dark-banner">
        <video autoplay muted loop playsinline>
            <source src="https://raw.githubusercontent.com/rain422/-/main/15254965_1920_1080_24fps.mp4" type="video/mp4">
        </video>
        <div class="dark-banner-overlay"></div>
        <div class="dark-banner-body">
            <div class="dark-banner-label">14 Key Sections</div>
            <div class="dark-banner-title">
                ECM 등가회로 모델의<br><span>모든 것</span>을 탐구하세요
            </div>
            <div class="dark-banner-desc">
                OCV · SoC · R₀ · RC · 와버그 · 히스테리시스 · ESC · 실험 · MATLAB 툴박스<br>
                14개 섹션을 통해 배터리 모델링의 전체 그림을 완성하세요.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="background:#0D1B2A;padding:56px 72px 72px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-bottom:48px;">
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;
                    color:#00B4A0;margin-bottom:14px;display:flex;align-items:center;
                    justify-content:center;gap:10px;">
            <span style="display:block;width:32px;height:1px;background:#00B4A0;"></span>
            14개 핵심 섹션
            <span style="display:block;width:32px;height:1px;background:#00B4A0;"></span>
        </div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.8rem;font-weight:800;
                    color:#fff;letter-spacing:-0.5px;">
            ECM 등가회로 모델 학습 주제 전체 보기
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols_per_row = 4
    for row_start in range(0, len(TOPICS), cols_per_row):
        row_topics = TOPICS[row_start:row_start+cols_per_row]
        cols = st.columns(cols_per_row, gap="small")
        for col, tp in zip(cols, row_topics):
            i = next(j for j,t in enumerate(TOPICS) if t["id"]==tp["id"])
            done = gs("progress").get(tp["id"], False)
            with col:
                st.markdown(f"""
                <div class="topic-nav-cell">
                    <div class="tnc-num">SECTION {tp['num']}</div>
                    <div class="tnc-title">{'✅ ' if done else ''}{tp['title']}</div>
                    <div class="tnc-arrow">→</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"이동_{tp['num']}", key=f"hn_{tp['id']}", use_container_width=True):
                    ss("sel_topic_id", tp["id"]); ss("page", "topics"); st.rerun()
        st.markdown("<div style='height:1px;background:rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 홈 뉴스룸
    if not gs("home_news"):
        with st.spinner("뉴스를 불러오는 중..."):
            ko = fetch_news("배터리 등가회로 모델 ECM BMS","ko","KR","KR:ko",4)
            en = fetch_news("Battery equivalent circuit model ECM","en","US","US:en",4)
            ss("home_news", ko + en)

    home_all = gs("home_news")
    st.markdown("""
    <div class="sec sec-white">
        <div class="sec-label">최신 뉴스</div>
        <div class="sec-title">뉴스룸</div>
    """, unsafe_allow_html=True)

    if home_all:
        cols4 = st.columns(4, gap="small")
        for i, item in enumerate(home_all[:8]):
            flag = "🇰🇷" if item.get("lang")=="ko" else "🌍"
            date = item.get("published","")[:10]
            img  = NEWS_IMGS[i % len(NEWS_IMGS)]
            with cols4[i % 4]:
                st.markdown(f"""
                <div class="news-card-lg">
                    <div class="news-card-img-wrap">
                        <img class="news-card-img" src="{img}" alt="news">
                    </div>
                    <div class="news-card-body">
                        <div class="news-card-date">{date}</div>
                        <div class="news-card-title">
                            <a href="{item['link']}" target="_blank">{item['title']}</a>
                        </div>
                        <div class="news-card-source">{flag} {item['source']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, rc, _ = st.columns([4,2,4])
        with rc:
            if st.button("🔄 뉴스 새로고침", key="home_news_refresh", use_container_width=True):
                ss("home_news", []); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 참고문헌
    st.markdown(f"""
    <div class="sec sec-gray">
        <div class="sec-label">학술 논문 &amp; 참고문헌</div>
        <div class="sec-title">논문 &amp; 참고문헌</div>
        <br>
    """, unsafe_allow_html=True)
    for p in PAPERS:
        doi_link = (f'<a href="{p["url"]}" target="_blank" class="paper-doi">DOI: {p["doi"]} ↗</a>'
                    if p["doi"] else
                    f'<a href="{p["url"]}" target="_blank" class="paper-doi">바로가기 ↗</a>')
        st.markdown(f"""
        <div class="paper-card" style="margin:0 0 12px;">
            <div class="paper-num">{p['idx']}</div>
            <div style="flex:1;">
                <span class="paper-tag">{p['tag']}</span>
                <div class="paper-title">{p['title']}</div>
                <div class="paper-authors">{p['authors']}</div>
                <div class="paper-journal">{p['journal']}</div>
                <div class="paper-desc">{p['desc']}</div>
                {doi_link}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 푸터
    st.markdown("""
    <div class="footer">
        <div class="footer-logo">🔋 ECM<span>Portal</span></div>
        <div class="footer-copy">ECM 등가회로 모델 연구포털 · Plett(2015) BMS Vol.1 Ch.02</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# TOPICS (14개 주제 학습)
# =====================================================================
elif page == "topics":
    cur_id = gs("sel_topic_id")
    si = next((i for i, t in enumerate(TOPICS) if t["id"] == cur_id), 0)

    tnames = [f"Section {t['num']}: {t['title']}" for t in TOPICS]
    sname = st.selectbox("섹션 선택", tnames, index=si, key="w_tsel")
    si = tnames.index(sname)
    tp = TOPICS[si]
    ss("sel_topic_id", tp["id"])

    # 진도 저장
    prog = gs("progress"); prog[tp["id"]] = True; ss("progress", prog)

    # 상세 히어로
    kw_chips = "".join([f'<span class="d-kw">{t}</span>' for t in tp["tags"]])
    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-crumb">ECM Portal › 학습 주제 › <span style="color:rgba(255,255,255,0.5);">{tp['title']}</span></div>
        <div class="detail-title">{tp['title']}</div>
        <div class="detail-sub">{tp['sub']}</div>
        <div class="detail-kws">{kw_chips}</div>
    </div>
    """, unsafe_allow_html=True)

    # 북마크
    bm_list = gs("bookmarks")
    bm_label = "★ 저장됨" if tp["id"] in bm_list else "☆ 북마크"
    th_col, tbm_col = st.columns([5,1])
    with tbm_col:
        if st.button(bm_label, key=f"bm_{tp['id']}", use_container_width=True):
            bm = gs("bookmarks")
            if tp["id"] in bm: bm.remove(tp["id"])
            else: bm.append(tp["id"])
            ss("bookmarks", bm); st.rerun()

    # 탭 바
    tab_items = [("concepts","📖 개념 설명"), ("equations","🔢 핵심 수식"), ("graph","📊 그래프"), ("compare","📋 비교 분석"), ("refs","📄 참고문헌")]
    cur_tab = gs("tab")
    tab_html = '<div class="dtab-bar">'
    for tk, tl in tab_items:
        cls = "on" if cur_tab == tk else ""
        tab_html += f'<span class="dtab {cls}">{tl}</span>'
    tab_html += "</div>"
    st.markdown(tab_html, unsafe_allow_html=True)

    tc = st.columns(len(tab_items))
    for i, (tk, tl) in enumerate(tab_items):
        with tc[i]:
            if st.button(tl, key=f"dt_{tk}", use_container_width=True):
                ss("tab", tk); st.rerun()

    # 사이드 + 메인
    mc, sc = st.columns([7, 3], gap="medium")

    with sc:
        nc_done = sum(1 for t in TOPICS if gs("progress").get(t["id"], False))
        bm_cnt = len(gs("bookmarks"))
        st.markdown(f"""
        <div class="side-w">
            <div class="side-w-title">학습 현황</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;text-align:center;">
                <div style="background:#E6F7F5;padding:12px 4px;border-radius:4px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#00B4A0;font-family:'Plus Jakarta Sans',sans-serif;">{nc_done}</div>
                    <div style="font-size:0.65rem;color:#9EA5AF;margin-top:2px;">완료 섹션</div>
                </div>
                <div style="background:#E6F7F5;padding:12px 4px;border-radius:4px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#00B4A0;font-family:'Plus Jakarta Sans',sans-serif;">{bm_cnt}</div>
                    <div style="font-size:0.65rem;color:#9EA5AF;margin-top:2px;">북마크</div>
                </div>
            </div>
        </div>
        <div class="side-w">
            <div class="side-w-title">Topic Overview</div>
            <div style="font-size:0.82rem;color:#6B7280;line-height:1.7;font-weight:300;">{tp['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        kw_c = "".join([f'<span class="kw-chip">{k}</span>' for k in tp["tags"]])
        st.markdown(f'<div class="side-w"><div class="side-w-title">Tags</div>{kw_c}</div>', unsafe_allow_html=True)

        # 전체 주제 목록 (사이드)
        with st.expander("🗂 전체 14개 주제"):
            for t2 in TOPICS:
                done2 = gs("progress").get(t2["id"], False)
                if st.button(f"{'✅' if done2 else '⬜'} {t2['num']}. {t2['title']}", key=f"side_{t2['id']}", use_container_width=True):
                    ss("sel_topic_id", t2["id"]); ss("tab","concepts"); st.rerun()

    with mc:
        active = gs("tab")

        if active == "concepts":
            kc = st.columns(2)
            for ki, kp in enumerate(tp["kps"]):
                with kc[ki % 2]:
                    st.markdown(f"""
                    <div class="kp-card">
                        <div class="kp-icon">{kp['i']}</div>
                        <div class="kp-title">{kp['t']}</div>
                        <div class="kp-desc">{kp['d']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(f"**{tp['title']}** — {tp['desc']}")

        elif active == "equations":
            for eq in tp["eqs"]:
                st.markdown(f"**{eq['t']}**")
                st.markdown(f'<div class="eq-box">{eq["c"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

        elif active == "graph":
            fig = None
            if tp["id"] == "t01":
                sx = [i/10 for i in range(11)]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=sx, y=[3.0,3.40,3.65,3.75,3.82,3.89,3.97,4.05,4.12,4.18,4.20], name="NMC", line=dict(color=TEAL,width=2.5)))
                fig.add_trace(go.Scatter(x=sx, y=[2.8,3.20,3.30,3.32,3.33,3.33,3.34,3.35,3.36,3.50,3.65], name="LFP", line=dict(color="#60a5fa",width=2.5,dash="dash")))
                fig.update_layout(**plot_lyt("OCV vs SoC","SoC","OCV (V)"))
            elif tp["id"] == "t02":
                zk = [1.0]; Q=25.0; eta=0.999; dt=1.0; I=5.0
                for _ in range(200): zk.append(max(0, zk[-1] - (dt/3600/Q)*eta*I))
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(range(201)), y=zk, name="SoC", line=dict(color=TEAL,width=2.5)))
                fig.update_layout(**plot_lyt("SoC 감소 (I=5A, Q=25Ah)","시간(s)","SoC"))
            elif tp["id"] in ["t03","t05"]:
                curr = [0]*5 + [5]*30 + [0]*20
                v = [4.1 - c*0.0082 for c in curr]
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=[4.1]*len(curr), name="OCV", line=dict(color="#ef4444",dash="dash",width=1.5)))
                fig.add_trace(go.Scatter(y=v, name="V(t)", line=dict(color=TEAL,width=2.5)))
                fig.update_layout(**plot_lyt("R₀ 순간 전압 강하","시간(s)","전압(V)"))
            elif tp["id"] == "t04":
                t_rc = list(range(81)); irc=0.0; vo,oc=[],[]
                for tt in t_rc:
                    oc.append(4.1)
                    if tt<5: vo.append(4.1); irc=0.0
                    else:
                        F=math.exp(-1/(0.0158*38000)); irc=F*irc+(1-F)*5.0
                        vo.append(4.1-0.0158*irc-0.0082*5.0)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=t_rc, y=oc, name="OCV", line=dict(color="#ef4444",dash="dash",width=1.5)))
                fig.add_trace(go.Scatter(x=t_rc, y=vo, name="V(t)", fill="tonexty", fillcolor="rgba(0,180,160,.06)", line=dict(color=TEAL,width=2.5)))
                fig.update_layout(**plot_lyt("RC 확산 전압 응답 (I=5A)","시간(s)","전압(V)"))
            elif tp["id"] == "t06":
                omega = np.logspace(4,-4,400); rez,imz=[],[]
                for w in omega:
                    jw = complex(0,w)
                    Z = 0.0082 + 0.0158/(1+jw*0.0158*38000) + 0.002/(complex(0,1)**0.5*w**0.5)
                    rez.append(Z.real*1000); imz.append(-Z.imag*1000)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=rez, y=imz, mode="lines", name="임피던스", line=dict(color=TEAL,width=2.5)))
                fig.update_layout(**plot_lyt("나이키스트 플롯 (EIS)","Re(Z) mΩ","-Im(Z) mΩ"))
            elif tp["id"] == "t07":
                sh2 = np.linspace(0,1,11)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(sh2), y=[2.8,3.3,3.34,3.35,3.36,3.37,3.38,3.40,3.45,3.5,3.65], name="충전 OCV", line=dict(color=TEAL,width=2.5)))
                fig.add_trace(go.Scatter(x=list(sh2), y=[2.8,3.2,3.27,3.28,3.29,3.30,3.31,3.33,3.38,3.44,3.60], name="방전 OCV", line=dict(color="#60a5fa",width=2.5,dash="dash")))
                fig.update_layout(**plot_lyt("히스테리시스 루프 (LFP)","SoC","OCV(V)"))
            elif tp["id"] == "t08":
                meas=[3.82,3.74,3.69,3.75,3.71,3.66,3.70,3.73,3.68,3.65,3.70]
                modl=[3.822,3.742,3.692,3.752,3.712,3.662,3.702,3.732,3.682,3.652,3.702]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(range(11)), y=meas, name="실측", mode="lines+markers", line=dict(color=LGRAY,dash="dot",width=2), marker=dict(size=5)))
                fig.add_trace(go.Scatter(x=list(range(11)), y=modl, name="ESC 모델", line=dict(color=TEAL,width=2.5)))
                fig.add_annotation(x=5, y=3.69, text="RMSE=5.37mV ✓", bgcolor="#dcfce7", bordercolor="#86efac", font=dict(color="#166534",size=11))
                fig.update_layout(**plot_lyt("ESC 검증: 모델 vs 실측 (UDDS)","시간→","V(V)"))
            elif tp["id"] == "t12":
                temps = [-20,-10,0,10,25,35,45]
                r0_vals = [0.042,0.028,0.018,0.013,0.0082,0.007,0.006]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=temps, y=r0_vals, name="R₀(T)", mode="lines+markers", line=dict(color=TEAL,width=2.5), marker=dict(size=7)))
                fig.update_layout(**plot_lyt("R₀ 온도 의존성","온도(°C)","R₀ (Ω)"))

            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("이 섹션의 그래프는 시뮬레이터 탭에서 직접 확인하세요.")

        elif active == "compare":
            comp = tp.get("comp")
            if comp:
                st.dataframe(pd.DataFrame(comp["r"], columns=comp["h"]), use_container_width=True, hide_index=True)
            else:
                st.info("비교 표가 없습니다.")

        elif active == "refs":
            for lbl, doi in tp.get("refs", []):
                doi_url = f"https://doi.org/{doi}" if doi else ""
                st.markdown(f"""
                <div style="background:{BG2};border-left:3px solid {TEAL};border-radius:0 8px 8px 0;padding:12px 14px;margin-bottom:9px;">
                    <div style="font-family:'Roboto Mono',monospace;font-size:9px;font-weight:700;color:{TEAL};margin-bottom:4px;">{lbl}</div>
                    {"<a href='"+doi_url+"' target='_blank' style='font-family:Roboto Mono,monospace;font-size:11px;color:"+TEAL+";'>DOI: "+doi+" ↗</a>" if doi else "<span style='color:"+LGRAY+";font-size:12px;'>교재 내 참고</span>"}
                </div>
                """, unsafe_allow_html=True)

    # 이전/다음 섹션 이동
    pp_col, pn_col = st.columns(2)
    with pp_col:
        if si > 0 and st.button(f"← {TOPICS[si-1]['title']}", key="w_prev", use_container_width=True):
            ss("sel_topic_id", TOPICS[si-1]["id"]); ss("tab","concepts"); st.rerun()
    with pn_col:
        if si < len(TOPICS)-1 and st.button(f"{TOPICS[si+1]['title']} →", key="w_next", use_container_width=True):
            ss("sel_topic_id", TOPICS[si+1]["id"]); ss("tab","concepts"); st.rerun()

    st.markdown("""
    <div class="footer">
        <div class="footer-logo">🔋 ECM<span>Portal</span></div>
        <div class="footer-copy">ECM 등가회로 모델 연구포털 · Plett(2015) BMS Vol.1 Ch.02</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# SIMULATOR (전압 응답 + 수식 모음)
# =====================================================================
elif page == "simulator":
    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-crumb">ECM Portal › 시뮬레이터</div>
        <div class="detail-title">📊 전압 응답 시뮬레이터</div>
        <div class="detail-sub">R₀·RC 파라미터를 조정하고 배터리 단자 전압 응답을 실시간으로 확인하세요.</div>
    </div>
    """, unsafe_allow_html=True)

    # 핵심 수식 모음
    st.markdown(f'<div style="padding:40px 72px 0;font-size:1.5rem;font-weight:800;color:{NAVY};">🔢 핵심 수식 모음</div>', unsafe_allow_html=True)

    EQ_LIST = [
        {"n":"식 2.1","lc":TEAL,        "t":"SoC 연속시간",    "c":"ż(t) = −η(t)·i(t) / Q"},
        {"n":"식 2.4","lc":"#60a5fa",   "t":"SoC 이산시간",    "c":"z[k+1] = z[k] − (Δt/Q)·η[k]·i[k]"},
        {"n":"식 2.8","lc":"#34d399",   "t":"RC 이산화 (ZOH)", "c":"i_R1[k+1] = F₁·i_R1[k] + (1−F₁)·i[k]\nF₁ = exp(−Δt/R₁C₁)"},
        {"n":"ESC 출력","lc":"#fbbf24", "t":"ESC 단자 전압",    "c":"v[k] = OCV(z,T) + M₀·s[k] + M·h[k]\n      − R₁·i_R1[k] − R₀·i[k]"},
        {"n":"히스테리시스","lc":"#a78bfa","t":"동적 히스테리시스","c":"h[k+1] = exp(−|η·i·γ·Δt/Q|)·h[k]\n       − (1−exp(···))·sgn(i[k])"},
        {"n":"OCV 온도","lc":"#f87171", "t":"OCV 온도 보정",    "c":"OCV(z,T) = OCV₀(z) + T·OCVrel(z)"},
    ]

    st.markdown('<div style="padding:20px 72px;">', unsafe_allow_html=True)
    ec = st.columns(2)
    for ei, eq in enumerate(EQ_LIST):
        with ec[ei % 2]:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid {BD};border-left:4px solid {eq['lc']};border-radius:8px;padding:16px;margin-bottom:14px;">
                <div style="font-family:'Roboto Mono',monospace;font-size:9px;font-weight:700;color:{eq['lc']};letter-spacing:.12em;margin-bottom:5px;">{eq['n']}</div>
                <div style="font-size:14px;font-weight:700;color:{NAVY};margin-bottom:8px;">{eq['t']}</div>
                <div class="eq-box">{eq['c'].replace(chr(10),"<br>")}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div style="padding:0 72px;font-size:1.2rem;font-weight:700;color:{NAVY};margin-bottom:12px;">⚡ RC 전압 응답 시뮬레이터</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 72px 40px;">', unsafe_allow_html=True)
    es1, es2 = st.columns([1, 1.5])
    with es1:
        sI  = st.slider("방전 전류 I (A)",  1.0, 100.0, 20.0, 1.0,  key="sim_I")
        sR0 = st.slider("R₀ (mΩ)",          1.0,  50.0,  8.2, 0.1,  key="sim_R0")
        sR1 = st.slider("R₁ (mΩ)",          1.0,  50.0, 15.8, 0.1,  key="sim_R1")
        sC1 = st.slider("C₁ (kF)",          1.0, 100.0, 38.0, 1.0,  key="sim_C1")
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
        fg2 = go.Figure()
        fg2.add_trace(go.Scatter(x=ts2, y=oc2, name="OCV", line=dict(color="#ef4444",dash="dash",width=1.5)))
        fg2.add_trace(go.Scatter(x=ts2, y=vs2, name="V(t)", fill="tonexty", fillcolor="rgba(0,180,160,.06)", line=dict(color=TEAL,width=2.5)))
        fg2.update_layout(**plot_lyt(f"V(t) | I={sI}A τ={tau_e:.0f}s","시간(s)","전압(V)"))
        st.plotly_chart(fg2, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # OCV vs SoC 시뮬레이터
    st.markdown(f'<div style="padding:0 72px;font-size:1.2rem;font-weight:700;color:{NAVY};margin-bottom:12px;">📈 OCV vs SoC 비교</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 72px 40px;">', unsafe_allow_html=True)
    sx = [i/10 for i in range(11)]
    fig_ocv = go.Figure()
    fig_ocv.add_trace(go.Scatter(x=sx, y=[3.0,3.40,3.65,3.75,3.82,3.89,3.97,4.05,4.12,4.18,4.20], name="NMC", line=dict(color=TEAL,width=2.5)))
    fig_ocv.add_trace(go.Scatter(x=sx, y=[2.8,3.20,3.30,3.32,3.33,3.33,3.34,3.35,3.36,3.50,3.65], name="LFP", line=dict(color="#60a5fa",width=2.5,dash="dash")))
    fig_ocv.update_layout(**plot_lyt("OCV vs SoC (NMC vs LFP)","SoC","OCV (V)"))
    st.plotly_chart(fig_ocv, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        <div class="footer-logo">🔋 ECM<span>Portal</span></div>
        <div class="footer-copy">ECM 등가회로 모델 연구포털 · Plett(2015) BMS Vol.1 Ch.02</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# QUIZ
# =====================================================================
elif page == "quiz":
    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-crumb">ECM Portal › 이해도 퀴즈</div>
        <div class="detail-title">📝 이해도 퀴즈</div>
        <div class="detail-sub">ECM 등가회로 모델 핵심 개념 10문항을 풀어보세요.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:40px 72px;">', unsafe_allow_html=True)

    if st.button("🔄 다시 시작", key="quiz_reset"):
        ss("quiz_idx",0); ss("quiz_score",0); ss("quiz_ans",False)
        ss("quiz_done",False); ss("quiz_sel",-1); st.rerun()

    if gs("quiz_done"):
        pct = int(gs("quiz_score")/len(QUIZ)*100)
        msg = ("🏆 완벽! ECM 모델링 마스터!" if pct==100
               else "👍 훌륭합니다!" if pct>=70
               else "📚 조금 더 복습해보세요.")
        st.markdown(f"""
        <div style="background:rgba(0,180,160,.07);border:1px solid rgba(0,180,160,.3);border-radius:16px;padding:40px;text-align:center;margin:20px 0;">
            <div style="font-size:52px;margin-bottom:14px;">🎉</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:48px;font-weight:800;color:{TEAL};">
                {gs("quiz_score")} / {len(QUIZ)}
            </div>
            <div style="font-size:16px;color:{GRAY};margin-top:12px;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        idx = gs("quiz_idx")
        if idx >= len(QUIZ):
            ss("quiz_done", True); st.rerun()
        else:
            q = QUIZ[idx]
            st.progress(idx/len(QUIZ), text=f"문제 {idx+1}/{len(QUIZ)} · 점수: {gs('quiz_score')}점")
            st.markdown(f"### Q{idx+1}. {q['q']}")

            if not gs("quiz_ans"):
                for oi, opt in enumerate(q["opts"]):
                    if st.button(f"{chr(65+oi)}. {opt}", key=f"qopt_{idx}_{oi}", use_container_width=True):
                        ss("quiz_ans", True); ss("quiz_sel", oi)
                        if oi == q["ans"]: ss("quiz_score", gs("quiz_score")+1)
                        st.rerun()
                if st.button("⏭ 건너뛰기", key=f"qskip_{idx}"):
                    ss("quiz_ans", True); ss("quiz_sel", -1); st.rerun()
            else:
                sel = gs("quiz_sel")
                for oi, opt in enumerate(q["opts"]):
                    lb = f"{chr(65+oi)}. {opt}"
                    if oi == q["ans"]:   st.success(f"✅ {lb}")
                    elif oi == sel:      st.error(f"❌ {lb}")
                    else:
                        st.markdown(f'<div style="padding:9px 12px;border:1px solid {BD};border-radius:7px;color:{GRAY};margin:3px 0;">{lb}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:rgba(0,180,160,.07);border-left:3px solid {TEAL};border-radius:0 8px 8px 0;padding:12px;margin:10px 0;">
                    <b>💡 해설:</b> {q['exp']}
                    <div class="eq-box" style="margin-top:8px;">{q['f']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("다음 문제 →", type="primary", use_container_width=True, key=f"qnext_{idx}"):
                    next_idx = idx + 1
                    ss("quiz_idx", next_idx); ss("quiz_ans", False); ss("quiz_sel", -1)
                    if next_idx >= len(QUIZ): ss("quiz_done", True)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <div class="footer-logo">🔋 ECM<span>Portal</span></div>
        <div class="footer-copy">ECM 등가회로 모델 연구포털 · Plett(2015) BMS Vol.1 Ch.02</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# NOTICES
# =====================================================================
elif page == "notices":
    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-crumb">ECM Portal › 공지사항</div>
        <div class="detail-title">📢 공지사항</div>
        <div class="detail-sub">최신 업데이트 및 Q&A를 확인하세요.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:40px 72px;">', unsafe_allow_html=True)
    nt = st.radio("", ["공지사항","업데이트","Q&A"], horizontal=True, key="ntab_sel", label_visibility="collapsed")
    st.markdown("---")
    for n in gs("notices"):
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
    with st.form("nf_form"):
        n_type_sel = st.selectbox("분류", ["공지","업데이트","Q&A"], key="nf_type")
        n_title    = st.text_input("제목", key="nf_title")
        n_body     = st.text_area("내용", key="nf_body")
        if st.form_submit_button("✅ 게시", use_container_width=True):
            if n_title and n_body:
                notices = gs("notices")
                notices.insert(0, {"type":n_type_sel,"title":n_title,"body":n_body,"date":datetime.now().strftime("%Y-%m-%d")})
                ss("notices", notices)
                st.success("공지가 게시되었습니다!"); st.rerun()
            else:
                st.warning("제목과 내용을 모두 입력해주세요.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <div class="footer-logo">🔋 ECM<span>Portal</span></div>
        <div class="footer-copy">ECM 등가회로 모델 연구포털 · Plett(2015) BMS Vol.1 Ch.02</div>
    </div>
    """, unsafe_allow_html=True)
