import os
import math
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
# 보안 세션 키 초기화 (배포 시 환경 변수 설정 권장)
app.config = os.environ.get('SECRET_KEY', 'ecm_research_portal_secure_key')

# 1. 글로벌 네비게이션 라우팅 블록
@app.route('/')
def index():
    """메인 홈 화면: 연구포털의 핵심 비전과 기술 소개"""
    return render_template('index.html', title="홈")

@app.route('/learning')
def learning():
    """주제별 학습 화면: 등가회로의 종류 및 이론적 배경 제공"""
    return render_template('learning.html', title="주제별 학습")

@app.route('/formulas')
def formulas():
    """수식 모음 화면: State-space 방정식을 비롯한 수학적 레퍼런스"""
    return render_template('base.html', title="수식 모음")

@app.route('/calculator')
def calculator():
    """파라미터 계산기 화면: 시각화 차트가 포함된 대시보드 렌더링"""
    return render_template('calculator.html', title="파라미터 계산기")

@app.route('/quiz')
def quiz():
    return render_template('base.html', title="퀴즈")

@app.route('/programs')
def programs():
    return render_template('base.html', title="프로그램")

@app.route('/notice')
def notice():
    return render_template('base.html', title="공지사항")

# 2. 파라미터 시뮬레이션 REST API 코어 연산 로직
@app.route('/api/simulate_ecm', methods=)
def simulate_ecm():
    """
    클라이언트에서 전달받은 ECM 파라미터(R0, R1, C1, 전류)를 기반으로
    100초 동안의 이산화된 1-RC 테브닌 모델 전압 응답을 계산하여 반환함.
    """
    try:
        data = request.get_json()
        
        # 기본 파라미터 설정 (없을 경우 디폴트 튜닝 값 적용)
        r0 = float(data.get('r0', 0.015))    # Ohmic Resistance (Ohms)
        r1 = float(data.get('r1', 0.025))    # Polarization Resistance (Ohms)
        c1 = float(data.get('c1', 1200))     # Polarization Capacitance (Farads)
        current = float(data.get('current', -20)) # Discharge Current (Amps, 음수)
        ocv_initial = 3.8 # Initial Open Circuit Voltage (V)
        
        # 시간 배열 생성 (0 ~ 100초, 1초 간격)
        time_array = np.linspace(0, 100, 100)
        voltage_response =
        
        # 수식 기반 전압 응답 시뮬레이션 연산
        # V(t) = OCV - R0*I - R1*I*(1 - exp(-t/(R1*C1)))
        tau = r1 * c1
        
        for t in time_array:
            v_c1 = current * r1 * (1 - math.exp(-t / tau))
            v_term = ocv_initial + (current * r0) + v_c1 # 방전 시 current가 음수이므로 전압 강하 발생
            voltage_response.append(round(v_term, 4))
            
        response_payload = {
            'status': 'success',
            'time': time_array.tolist(),
            'voltage': voltage_response
        }
        return jsonify(response_payload)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    # 개발 및 테스트를 위한 로컬 웹 서버 구동 (포트 5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
