import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="배터리 등가회로 연구포털",
    page_icon="🔋",
    layout="wide"
)

# 2. 상단 헤더 및 타이틀 영역 (요청하신 텍스트 반영)
st.title("🔋 배터리 등가회로 연구포털")
st.subheader("배터리 등가회로를 결정하는 핵심 기술")
st.markdown("---")

# 3. 메인 이미지 영역 (AI 이미지 생성 프롬프트 기반의 대체 이미지)
# 프롬프트: "Create a modern, clean digital illustration in a style similar to `image_cf8d33.png`. The image should depict a stylized lithium-ion battery from a cutaway perspective. Within and around the battery structure, illustrate key equivalent circuit model elements..."
st.image(
    "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop", 
    caption="배터리 등가회로 시각화 (AI Generated Placeholder)", 
    use_container_width=True
)

# 4. 네비게이션 탭 구성 (HTML의 메뉴 역할)
tab1, tab2, tab3 = st.tabs(["🏠 홈", "📖 주제별 학습", "🧮 파라미터 계산기"])

# 첫 번째 탭: 홈
with tab1:
    st.markdown("### 📌 포털 소개")
    st.write("""
    배터리 등가회로 연구포털에 오신 것을 환영합니다. 
    
    본 포털은 전기차, 에너지 저장 장치 등 현대 사회의 핵심 기술인 배터리의 성능과 상태를 정확하게 모델링하고 예측하기 위한 필수 기술인 **'등가회로 모델(Equivalent Circuit Model, ECM)'**에 대한 연구 정보를 제공합니다. 
    
    등가회로는 복잡한 배터리의 전기화학적 특성을 직관적이고 계산이 용이한 회로 소자로 표현하여, BMS(Battery Management System) 알고리즘 개발의 기반이 됩니다.
    """)

# 두 번째 탭: 주제별 학습
with tab2:
    st.markdown("### 📚 주제별 학습")
    
    # 두 개의 열로 나누어 카드 형태로 배치
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("2.1 개방회로 전압 (OCV)"):
            st.write("무부하 평형 상태의 단자 전압. 배터리 SoC 추정의 핵심 기준값입니다.")
            st.code("v(t) = OCV(z(t))", language="python")
            
        with st.expander("2.2 충전 상태 의존성 (SoC)"):
            st.write("현재 잔존 전하량 정량화. 쿨롱 카운팅과 이산시간 변환을 학습합니다.")
            
    with col2:
        with st.expander("2.3 등가 직렬 저항 (ESR)"):
            st.write("전류 인가 직후 순간 전압 강하로 측정하며, 저온에서 크게 증가합니다.")
            
        with st.expander("2.4 확산 전압 (Diffusion)"):
            st.write("리튬 이온 농도 구배로 발생하는 느린 동적 전압 현상입니다. RC 회로로 근사합니다.")

# 세 번째 탭: 파라미터 계산기 (Streamlit의 장점인 인터랙티브 기능)
with tab3:
    st.markdown("### ⚡ 간단한 RC 파라미터 계산기")
    st.write("아래에 값을 입력하여 시정수(τ)를 즉시 계산해 보세요.")
    
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        r1 = st.number_input("R₁ 분극 저항 (mΩ)", value=15.8, step=0.1)
    with calc_col2:
        c1 = st.number_input("C₁ 분극 커패시턴스 (F)", value=38000, step=1000)
        
    if st.button("계산하기"):
        # 저항 단위를 mΩ에서 Ω으로 변환하여 계산
        tau = (r1 / 1000) * c1
        st.success(f"**시정수 τ = R₁ × C₁ = {tau:.1f} 초**")
        st.info(f"💡 4τ (98% 수렴 시간) = {4*tau:.1f} 초 (약 {round((4*tau)/60)}분)")

# 5. 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>&copy; 2026 배터리 등가회로 연구포털. All rights reserved.</p>", unsafe_allow_html=True)
