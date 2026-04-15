from flask import Flask, render_template_string
import json

app = Flask(__name__)

# 1. 파이썬 백엔드 데이터: 화면에 보여질 주제 및 구성 데이터를 파이썬 딕셔너리로 관리합니다.
# 실제 서비스에서는 이 부분을 DB(MySQL, MongoDB 등)와 연동하여 사용합니다.
PORTAL_INFO = {
    "title": "배터리 등가회로 연구포털",
    "subtitle": "배터리 등가회로를 결정하는 핵심 기술",
    # AI로 생성된 배터리 등가회로 이미지를 연동할 경로 (현재는 고품질 IT/회로 placeholder 이미지 사용)
    "hero_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop" 
}

TOPICS_DATA = [
    {"num": "2.1", "title": "개방회로 전압 (OCV)", "desc": "무부하 평형 상태의 단자 전압. 배터리 SoC 추정의 핵심 기준값."},
    {"num": "2.2", "title": "충전 상태 의존성 (SoC)", "desc": "현재 잔존 전하량 정량화. 쿨롱 카운팅과 이산시간 변환."},
    {"num": "2.3", "title": "등가 직렬 저항 (ESR)", "desc": "전류 인가 직후 순간 전압 강하로 측정. 저온에서 크게 증가."},
    {"num": "2.4", "title": "확산 전압 (Diffusion)", "desc": "리튬 이온 농도 구배로 발생하는 느린 동적 전압 현상."},
]

# 2. HTML 템플릿 (Jinja2 문법 적용)
# 파이썬에서 넘겨준 데이터를 {{ 변수명 }} 형태로 HTML에 동적으로 렌더링합니다.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ portal.title }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --blue: #1a5fa8; --navy: #0e3a6e; --bg: #f8fafc; --white: #ffffff;
            --text: #1e293b; --text2: #475569; --bd: #e2e8f0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Noto Sans KR', sans-serif; background: var(--bg); color: var(--text); }
        
        /* 헤더 스타일 */
        header { background: var(--white); border-bottom: 2px solid var(--blue); padding: 0 32px; height: 60px; display: flex; align-items: center; position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 18px; font-weight: 700; color: var(--navy); }
        
        /* 메인 히어로 배너 (이미지 포함) */
        #hero { 
            position: relative; 
            background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 100%); 
            color: white; 
            padding: 80px 32px; 
            display: flex; 
            align-items: center; 
            justify-content: space-between;
            overflow: hidden;
        }
        .hero-content { max-width: 600px; z-index: 2; }
        .hero-title { font-size: 38px; font-weight: 700; margin-bottom: 16px; line-height: 1.3; }
        .hero-sub { font-size: 18px; color: rgba(255,255,255,0.85); margin-bottom: 30px; }
        
        /* AI 이미지 영역 */
        .hero-image-wrap {
            position: relative;
            z-index: 2;
            width: 400px;
            height: 250px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.2);
        }
        .hero-image-wrap img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .ai-badge {
            position: absolute;
            top: 10px; right: 10px;
            background: rgba(0,0,0,0.6);
            color: #fff;
            padding: 4px 8px;
            font-size: 11px;
            border-radius: 4px;
            backdrop-filter: blur(4px);
        }

        /* 메인 콘텐츠 영역 */
        .container { max-width: 1200px; margin: 40px auto; padding: 0 32px; }
        .section-title { font-size: 20px; font-weight: 700; color: var(--navy); margin-bottom: 20px; border-left: 4px solid var(--blue); padding-left: 12px; }
        
        /* 기능 그리드 */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .card { background: var(--white); border: 1px solid var(--bd); border-radius: 10px; padding: 20px; transition: transform 0.2s; cursor: pointer; }
        .card:hover { transform: translateY(-3px); border-color: var(--blue); box-shadow: 0 4px 12px rgba(26,95,168,0.1); }
        .card-num { font-size: 12px; color: var(--blue); font-weight: 700; margin-bottom: 8px; }
        .card-title { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
        .card-desc { font-size: 13px; color: var(--text2); line-height: 1.5; }

        footer { background: var(--navy); color: rgba(255,255,255,0.7); padding: 30px; text-align: center; font-size: 13px; margin-top: 60px; }
    </style>
</head>
<body>

    <header>
        <div class="logo">🔋 {{ portal.title }}</div>
    </header>

    <section id="hero">
        <div class="hero-content">
            <h1 class="hero-title">{{ portal.title }}</h1>
            <p class="hero-sub">{{ portal.subtitle }}</p>
            <button style="background:#fff; color:var(--blue); border:none; padding:12px 24px; border-radius:6px; font-weight:bold; cursor:pointer;">학습 시작하기 →</button>
        </div>
        
        <div class="hero-image-wrap">
            <div class="ai-badge">AI Generated</div>
            <img src="{{ portal.hero_image }}" alt="배터리 등가회로 시각화 이미지">
        </div>
    </section>

    <div class="container">
        <h2 class="section-title">주제별 학습</h2>
        <div class="grid">
            {% for topic in topics %}
            <div class="card" onclick="alert('{{ topic.title }} 모달을 엽니다.')">
                <div class="card-num">Section {{ topic.num }}</div>
                <div class="card-title">{{ topic.title }}</div>
                <div class="card-desc">{{ topic.desc }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <footer>
        <p>&copy; 2026 {{ portal.title }} All rights reserved.</p>
    </footer>

</body>
</html>
"""

# 3. 라우팅 (경로 설정)
@app.route('/')
def home():
    # render_template_string을 통해 파이썬 데이터를 HTML 변수에 주입하여 브라우저로 반환합니다.
    return render_template_string(
        HTML_TEMPLATE, 
        portal=PORTAL_INFO, 
        topics=TOPICS_DATA
    )

# 4. 앱 실행
if __name__ == '__main__':
    print(f"🚀 웹 서버가 시작되었습니다. 브라우저에서 http://127.0.0.1:5000 으로 접속하세요.")
    app.run(host='0.0.0.0', port=5000, debug=True)
