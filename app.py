import streamlit as st
import numpy as np
import json
from datetime import datetime

# ─── 페이지 설정 ───
st.set_page_config(
    page_title="ECM 연구포털 v2 — 등가회로 모델",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.metric-card {
    background: linear-gradient(135deg, #1a3a5c, #2d5a8e);
    color: white; padding: 1.2rem; border-radius: 12px; text-align: center;
}
.metric-card h2 { font-size: 2rem; margin: 0; }
.metric-card p { font-size: 0.85rem; opacity: 0.8; margin: 0; }
.section-card {
    background: #f8f9fa; border-left: 4px solid #2d5a8e;
    padding: 1rem 1.2rem; border-radius: 8px; margin-bottom: 0.8rem;
}
.badge { background: #e8f0fe; color: #1a3a5c; padding: 2px 10px;
    border-radius: 12px; font-size: 0.78rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ─── 세션 초기화 ───
if "progress" not in st.session_state:
    st.session_state.progress = set()
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = set()

# ─── 데이터 ───
TOPICS = [
    {"id": 1, "icon": "🔋", "title": "셀 모델링 개요", "cat": "개념",
     "desc": "배터리 셀의 전기적 거동을 수학적으로 표현하는 방법론 소개. 왜 등가회로 모델이 필요한지, 물리 기반 모델과의 차이를 학습합니다."},
    {"id": 2, "icon": "📈", "title": "OCV–SOC 관계", "cat": "수식",
     "desc": "개방 회로 전압(OCV)과 충전 상태(SOC)의 비선형 관계. OCV(z) 곡선 측정법과 다항식/룩업테이블 모델링을 다룹니다."},
    {"id": 3, "icon": "⚡", "title": "등가 직렬 저항 (ESR)", "cat": "수식",
     "desc": "옴 저항 R₀에 의한 순간 전압 강하. 온도·SOC 의존성과 HPPC 테스트를 통한 식별법을 학습합니다."},
    {"id": 4, "icon": "🔄", "title": "RC 분극 모델", "cat": "수식",
     "desc": "1-RC, 2-RC 병렬 회로로 전하 이동 및 이중층 효과를 모델링. 시정수 τ = R₁C₁의 물리적 의미를 이해합니다."},
    {"id": 5, "icon": "🌊", "title": "확산 전압", "cat": "수식",
     "desc": "저주파 확산 현상을 RC 래더 또는 와버그 임피던스로 모델링. 긴 시정수의 전압 완화 거동을 분석합니다."},
    {"id": 6, "icon": "🔀", "title": "히스테리시스 전압", "cat": "개념",
     "desc": "충전/방전 경로에 따른 OCV 차이. One-state 히스테리시스 모델 h(z,t)의 수학적 표현과 감쇠율 γ를 학습합니다."},
    {"id": 7, "icon": "🧮", "title": "쿨롱 카운팅", "cat": "수식",
     "desc": "SOC 추정의 기본: z(t) = z(t₀) − (1/Q)∫i(τ)dτ. 쿨롱 효율 η와 누적 오차 문제를 다룹니다."},
    {"id": 8, "icon": "📊", "title": "ESC 통합 모델", "cat": "수식",
     "desc": "OCV + ESR + RC + 히스테리시스를 결합한 Enhanced Self-Correcting 모델. 이산시간 상태공간 표현을 완성합니다."},
    {"id": 9, "icon": "📐", "title": "상태공간 표현", "cat": "수식",
     "desc": "x[k+1] = Ax[k] + Bu[k], y[k] = Cx[k] + Du[k] 형태의 이산시간 모델. 행렬 A, B, C, D 구성법을 학습합니다."},
    {"id": 10, "icon": "🔍", "title": "파라미터 식별", "cat": "실습",
     "desc": "최소자승법(LS)과 펄스 테스트를 이용한 R₀, R₁, C₁ 추출. MATLAB/Python 실습 코드를 제공합니다."},
    {"id": 11, "icon": "📡", "title": "EIS 임피던스 분석", "cat": "실습",
     "desc": "전기화학 임피던스 분광법(EIS) 나이퀴스트 플롯 해석. 주파수 영역에서 ECM 파라미터를 추출하는 방법을 다룹니다."},
    {"id": 12, "icon": "🎯", "title": "칼만 필터 기초", "cat": "개념",
     "desc": "확장 칼만 필터(EKF)를 이용한 실시간 SOC 추정. 예측-업데이트 사이클과 공분산 행렬의 역할을 학습합니다."},
    {"id": 13, "icon": "🛠", "title": "MATLAB 툴박스 실습", "cat": "실습",
     "desc": "Plett BMS 툴박스(ESCtoolbox.zip)를 활용한 시뮬레이션. 모델 구축부터 EKF 적용까지 단계별 실습입니다."},
    {"id": 14, "icon": "📝", "title": "종합 정리 및 응용", "cat": "개념",
     "desc": "ECM 모델의 한계와 확장 (열결합, 노화 모델). 최신 연구 동향과 산업 적용 사례를 정리합니다."},
]

EQUATIONS = [
    {"title": "쿨롱 카운팅 (SOC)", "latex": r"z[k+1] = z[k] - \frac{\eta \, \Delta t}{Q}\, i[k]",
     "desc": "η: 쿨롱 효율, Q: 공칭 용량, Δt: 샘플링 주기"},
    {"title": "OCV 다항식 모델", "latex": r"OCV(z) = k_0 + k_1 z + k_2 z^2 + \cdots + k_n z^n",
     "desc": "SOC(z)에 대한 n차 다항식 피팅"},
    {"title": "RC 분극 전압", "latex": r"v_{R1}[k+1] = \exp\!\left(\frac{-\Delta t}{R_1 C_1}\right) v_{R1}[k] \;+\; R_1\!\left(1 - \exp\!\left(\frac{-\Delta t}{R_1 C_1}\right)\right) i[k]",
     "desc": "1차 RC 회로의 이산시간 전압 응답"},
    {"title": "단자 전압 (ESC 모델)", "latex": r"V_t[k] = OCV(z[k]) - R_0\, i[k] - v_{R1}[k] + h[k]",
     "desc": "OCV − 옴 강하 − 분극 전압 + 히스테리시스"},
    {"title": "히스테리시스 모델", "latex": r"h[k+1] = \exp(-|\eta\, i[k]\, \gamma\, \Delta t / Q|)\, h[k] + (1 - \exp(-|\eta\, i[k]\, \gamma\, \Delta t / Q|))\, M \cdot \text{sgn}(i[k])",
     "desc": "γ: 히스테리시스 감쇠율, M: 최대 히스테리시스 전압"},
    {"title": "와버그 임피던스", "latex": r"Z_W = \frac{\sigma}{\sqrt{\omega}}(1 - j)",
     "desc": "σ: 와버그 계수, ω: 각주파수"},
]

QUIZ = [
    {"q": "등가회로 모델(ECM)에서 R₀가 나타내는 것은?", "opts": ["분극 저항", "확산 저항", "등가 직렬 저항 (옴 저항)", "히스테리시스"], "ans": 2},
    {"q": "시정수 τ = R₁C₁ 의 물리적 의미는?", "opts": ["최대 전압", "63.2% 응답 도달 시간", "공칭 용량", "쿨롱 효율"], "ans": 1},
    {"q": "SOC 추정에서 쿨롱 카운팅의 주요 단점은?", "opts": ["계산 비용이 높다", "초기값 오차가 누적된다", "온도 보정이 불가하다", "고주파 응답이 느리다"], "ans": 1},
    {"q": "OCV-SOC 곡선에서 히스테리시스란?", "opts": ["전압 노이즈", "충방전 경로 차이에 의한 OCV 차이", "ESR에 의한 전압 강하", "확산 전압"], "ans": 1},
    {"q": "ESC 모델의 'Enhanced Self-Correcting'에서 보정 대상은?", "opts": ["온도", "SOC 추정값", "전류 센서", "저항값"], "ans": 1},
    {"q": "EIS에서 나이퀴스트 플롯의 x축은?", "opts": ["주파수", "실수 임피던스 Z'", "허수 임피던스 Z''", "위상각"], "ans": 1},
    {"q": "1-RC 모델에서 4τ 시간이 의미하는 것은?", "opts": ["50% 수렴", "약 98% 수렴", "100% 수렴", "63% 수렴"], "ans": 1},
    {"q": "칼만 필터의 두 단계는?", "opts": ["충전-방전", "예측-업데이트", "측정-보정", "초기화-종료"], "ans": 1},
    {"q": "쿨롱 효율 η의 일반적인 값은?", "opts": ["~50%", "~80%", "~99.9%", "~110%"], "ans": 2},
    {"q": "확산 전압 모델링에 사용되는 임피던스는?", "opts": ["옴 임피던스", "유도 임피던스", "와버그 임피던스", "커패시턴스"], "ans": 2},
]

REFERENCES = [
    {"type": "교재", "title": "Battery Management Systems Vol.1", "author": "G.L. Plett", "year": 2015,
     "detail": "Artech House · ISBN 978-1-60807-650-3"},
    {"type": "SCI 논문", "title": "EKF for Battery Management Systems", "author": "Plett, G.L.", "year": 2004,
     "detail": "J. Power Sources, 134 · DOI: 10.1016/j.jpowsour.2004.02"},
    {"type": "SCI 논문", "title": "ECM 비교연구", "author": "Hu, X. et al.", "year": 2012,
     "detail": "J. Power Sources, 198 · DOI: 10.1016/j.jpowsour.2012.03"},
    {"type": "툴박스", "title": "MATLAB ESC toolbox", "author": "Plett", "year": 2015,
     "detail": "mocha-java.uccs.edu"},
]

# ─── 사이드바 ───
with st.sidebar:
    st.markdown("## 🔋 ECM 연구포털 v2")
    st.caption("Battery Management Systems · Ch.02")
    st.divider()
    page = st.radio("메뉴", [
        "📖 주제별 학습", "🔢 핵심 수식", "🧮 파라미터 계산기",
        "📊 전압 응답 시뮬레이터", "📝 이해도 퀴즈", "📚 참고문헌",
    ], label_visibility="collapsed")
    st.divider()
    prog = len(st.session_state.progress)
    st.markdown(f"📈 **학습 진도** {prog} / 14")
    st.progress(prog / 14)
    if st.session_state.bookmarks:
        st.markdown("🔖 **북마크**")
        for b in sorted(st.session_state.bookmarks):
            t = next((x for x in TOPICS if x["id"] == b), None)
            if t:
                st.markdown(f"- {t['icon']} {t['title']}")
    else:
        st.caption("🔖 북마크 없음")

# ════════════════════════════════════════
# 📖 주제별 학습
# ════════════════════════════════════════
if page == "📖 주제별 학습":
    st.title("📖 주제별 학습")
    st.markdown("**14개 섹션** — OCV·ESR·확산 전압·히스테리시스를 통합한 ESC 모델까지")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card"><h2>14</h2><p>주제 섹션</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h2>5.4 mV</h2><p>모델 RMSE</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><h2>99.9%</h2><p>쿨롱 효율 η</p></div>', unsafe_allow_html=True)

    st.divider()
    filt = st.selectbox("카테고리 필터", ["전체", "개념", "수식", "실습"])
    filtered = TOPICS if filt == "전체" else [t for t in TOPICS if t["cat"] == filt]

    for t in filtered:
        with st.expander(f"{t['icon']}  **{t['id']:02d}. {t['title']}**  `{t['cat']}`", expanded=False):
            st.session_state.progress.add(t["id"])
            st.markdown(t["desc"])
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if t["id"] in st.session_state.bookmarks:
                    if st.button("★ 북마크 해제", key=f"bm_{t['id']}"):
                        st.session_state.bookmarks.discard(t["id"])
                        st.rerun()
                else:
                    if st.button("☆ 북마크", key=f"bm_{t['id']}"):
                        st.session_state.bookmarks.add(t["id"])
                        st.rerun()

# ════════════════════════════════════════
# 🔢 핵심 수식
# ════════════════════════════════════════
elif page == "🔢 핵심 수식":
    st.title("🔢 핵심 수식 한눈에 보기")
    for eq in EQUATIONS:
        with st.container():
            st.markdown(f'<div class="section-card"><b>{eq["title"]}</b></div>', unsafe_allow_html=True)
            st.latex(eq["latex"])
            st.caption(eq["desc"])
            st.markdown("")

# ════════════════════════════════════════
# 🧮 파라미터 계산기
# ════════════════════════════════════════
elif page == "🧮 파라미터 계산기":
    st.title("🧮 RC 파라미터 계산기")
    c1, c2 = st.columns(2)
    with c1:
        R1 = st.number_input("R₁ 분극 저항 (mΩ)", value=10.0, min_value=0.1, step=0.1)
        C1 = st.number_input("C₁ 분극 커패시턴스 (F)", value=1000.0, min_value=1.0, step=10.0)
    with c2:
        R0 = st.number_input("R₀ 직렬 저항 (mΩ)", value=5.0, min_value=0.1, step=0.1)
        dI = st.number_input("전류 Δi (A)", value=10.0, step=1.0)

    if st.button("⚡ 계산", type="primary"):
        R1_ohm = R1 / 1000
        R0_ohm = R0 / 1000
        tau = R1_ohm * C1
        conv_4tau = 4 * tau
        dV0 = R0_ohm * dI
        dVinf = (R0_ohm + R1_ohm) * dI
        F1 = np.exp(-1.0 / tau) if tau > 0 else 0

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("시정수 τ = R₁×C₁", f"{tau:.3f} s")
        m2.metric("4τ (98% 수렴)", f"{conv_4tau:.2f} s")
        m3.metric("속도계수 F₁", f"{F1:.6f}")
        m4, m5 = st.columns(2)
        m4.metric("순간 전압 강하 ΔV₀", f"{dV0*1000:.2f} mV")
        m5.metric("정상상태 ΔV∞", f"{dVinf*1000:.2f} mV")

# ════════════════════════════════════════
# 📊 전압 응답 시뮬레이터
# ════════════════════════════════════════
elif page == "📊 전압 응답 시뮬레이터":
    st.title("📊 전압 응답 시뮬레이터")
    st.caption("5초 시점에 방전 시작 — 1-RC 등가회로 모델")
    c1, c2, c3, c4 = st.columns(4)
    with c1: I_dis = st.slider("방전 전류 I (A)", 1.0, 50.0, 10.0)
    with c2: r0 = st.slider("R₀ (mΩ)", 1.0, 50.0, 5.0)
    with c3: r1 = st.slider("R₁ (mΩ)", 1.0, 100.0, 10.0)
    with c4: c1v = st.slider("C₁ (F)", 100.0, 10000.0, 1000.0, step=100.0)

    dt = 0.05
    t = np.arange(0, 60, dt)
    OCV_base = 3.8
    R0 = r0 / 1000; R1 = r1 / 1000; C1 = c1v
    tau = R1 * C1
    F1 = np.exp(-dt / tau) if tau > 0 else 0
    H1 = R1 * (1 - F1)

    vrc = np.zeros_like(t)
    vt = np.zeros_like(t)
    for k in range(len(t)):
        i_k = I_dis if t[k] >= 5 else 0
        if k > 0:
            i_prev = I_dis if t[k-1] >= 5 else 0
            vrc[k] = F1 * vrc[k-1] + H1 * i_prev
        vt[k] = OCV_base - R0 * i_k - vrc[k]

    import matplotlib.pyplot as plt
    import koreanize_matplotlib

# AUTO-INJECTED: Korean font setup for matplotlib
import os as _os
import matplotlib.font_manager as _fm
import matplotlib.pyplot as _plt
if not any('NanumGothic' in f.name for f in _fm.fontManager.ttflist):
    for _font in ['/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                  '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf']:
        if _os.path.exists(_font):
            _fm.fontManager.addfont(_font)
_plt.rcParams.update({'font.family': 'NanumGothic', 'axes.unicode_minus': False})
del _os, _fm, _plt
# END AUTO-INJECTED Korean font setup

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, vt, color="#2d5a8e", linewidth=2, label="단자전압 V(t)")
    ax.axhline(OCV_base, color="#e74c3c", linestyle="--", label="OCV 기준선")
    ax.axvline(5, color="gray", linestyle=":", alpha=0.5, label="방전 시작 (5s)")
    ax.set_xlabel("시간 (s)"); ax.set_ylabel("전압 (V)")
    ax.legend(); ax.grid(True, alpha=0.3)
    ax.set_title("1-RC 등가회로 전압 응답")
    st.pyplot(fig)
    plt.close()

# ════════════════════════════════════════
# 📝 이해도 퀴즈
# ════════════════════════════════════════
elif page == "📝 이해도 퀴즈":
    st.title("📝 이해도 퀴즈")
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = None
        st.session_state.quiz_answers = {}

    with st.form("quiz_form"):
        for i, q in enumerate(QUIZ):
            st.markdown(f"**Q{i+1}.** {q['q']}")
            st.session_state.quiz_answers[i] = st.radio(
                f"q{i+1}", q["opts"], key=f"quiz_{i}", label_visibility="collapsed"
            )
            st.markdown("")

        submitted = st.form_submit_button("✅ 제출", type="primary")
        if submitted:
            score = 0
            for i, q in enumerate(QUIZ):
                sel = q["opts"].index(st.session_state.quiz_answers[i])
                if sel == q["ans"]:
                    score += 1
            st.session_state.quiz_score = score

    if st.session_state.quiz_score is not None:
        s = st.session_state.quiz_score
        if s == 10:
            st.balloons()
            st.success(f"🎉 만점! {s} / 10")
        elif s >= 7:
            st.success(f"👏 잘했습니다! {s} / 10")
        else:
            st.warning(f"📖 복습이 필요합니다. {s} / 10")

# ════════════════════════════════════════
# 📚 참고문헌
# ════════════════════════════════════════
elif page == "📚 참고문헌":
    st.title("📚 참고문헌 및 관련 자료")
    for r in REFERENCES:
        st.markdown(f"""
<div class="section-card">
<span class="badge">{r['type']}</span><br>
<b>{r['title']}</b> — {r['author']} ({r['year']})<br>
<small>{r['detail']}</small>
</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("**🔗 외부 링크**")
    st.markdown("- [MATLAB ESC toolbox](http://mocha-java.uccs.edu) — Plett BMS 툴박스")
    st.markdown("- [Plett(2004) DOI](https://doi.org/10.1016/j.jpowsour.2004.02) — EKF for BMS")
