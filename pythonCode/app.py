from flask import Flask, request, jsonify, render_template
import base64
import json
import io
import pymysql
import numpy as np
from PIL import Image
import torch
from transformers import pipeline

# ====== 1. Flask 및 환경 설정 ======
app = Flask(__name__)

# ====== 2. DB 및 모델 전역 설정 (성능 최적화) ======
# TODO: 실제 사용자의 DB 비밀번호와 정보를 설정하세요.
DB_CONFIG = {
    'host': '127.0.0.1', 
    'user': 'root', 
    'password': '', # ⬅️ 본인의 MySQL root 비밀번호로 변경하세요.
    'db': 'kculture', 
    'charset': 'utf8'
}

# GPU/CPU 설정
device_option = 0 if torch.cuda.is_available() else -1
print(f"모델 실행 장치: {'GPU' if device_option == 0 else 'CPU'}")

# 모델 로딩 (서버 시작 시 1회만 실행되어야 함)
try:
    detector = pipeline(
        model="google/owlv2-base-patch16-ensemble", 
        task="zero-shot-object-detection", 
        device=device_option
    )
    print("Zero-Shot Object Detection 모델 로딩 완료.")
except Exception as e:
    print(f"모델 로딩 중 오류 발생: {e}")
    detector = None

# ====== 3. DB에서 탐지할 객체 목록 로드 ======
def load_candidate_labels():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        # 테이블 생성 및 초기 데이터 삽입 로직은 서버 시작 시점에 한 번 실행하는 것이 좋지만, 
        # 여기서는 ObjectList 테이블이 이미 존재한다고 가정합니다.
        cur.execute("SELECT name from ObjectList")
        labels = [row[0] for row in cur.fetchall()]
        conn.close()
        return labels
    except Exception as e:
        print(f"DB 연결 및 레이블 로드 오류: {e}")
        return []

CANDIDATE_LABELS = load_candidate_labels()
print(f"DB에서 탐지 레이블 {len(CANDIDATE_LABELS)}개 로드 완료.")

# ===============================================
# Flask 엔드포인트
# ===============================================

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def analyze_image():
    if not detector:
        return jsonify({'status': 'error', 'description': '모델 초기화 실패.'}), 500
        
    try:
        input_year = int(request.form.get('year')) # 연도를 정수로 받음
        file = request.files.get('image')
        
        if not file or not input_year:
            return jsonify({'message': '이미지 혹은 연도가 누락되었습니다.'}), 400

        # 1. 이미지 로딩
        image = Image.open(file.stream)

        # 2. 객체 탐지 실행
        predictions = detector(image, candidate_labels=CANDIDATE_LABELS)
        
        # 3. 탐지된 객체 이름 추출
        # 딕셔너리 사용하여 중복 제거(최대 스코어) 및 box 정보 저장
        detected = {}
        for prediction in predictions:
            # 신뢰도 점수가 0.1 이상인 결과만 필터링 (Jupyter Notebook과 동일)
            score = prediction["score"]
            label = prediction["label"]
            box = prediction["box"]
            if score > 0.1:
                if label in detected and score < detected[label][0]:
                    continue
                detected[label] = (score, box)
        
        # 딕셔너리 키 추출 - 탐지된 객체 이름 리스트
        detected_objects = list(detected.keys())
        
        # 탐지된 객체가 없을 경우 처리
        if not detected_objects:
            analysis_result = f"요청 연도 {input_year}년. 이미지에서 지정된 K-Culture 관련 객체를 찾지 못했습니다."
            return jsonify({
                'status': 'success',
                'description': analysis_result,
                'detected_count': 0
            })
            
        # 4. 탐지된 객체를 DB에서 조회하고 연도 비교
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        format_strings = ','.join(['%s'] * len(detected_objects))
        sql = "SELECT name, start_year, description FROM ObjectList WHERE name IN (%s)" % format_strings
        cur.execute(sql, tuple(detected_objects))
        
        rows = cur.fetchall()
        conn.close()

        # 5. 최종 분석 결과 생성
        anachronistic_objects = [] # 연도 불일치 객체
        
        # ✅ 추가: 탐지된 모든 객체의 상세 정보를 저장할 리스트
        all_detected_details = [] 
        
        # 오류 탐지 여부
        error_not_detected = True

        for name, start_year, description in rows:
            # 탐지된 객체의 상세 정보를 리스트에 추가
            all_detected_details.append(
                f"'{name}' (출시: {start_year}년)"
            )
            
            # 연도 불일치 검사 (고증 오류 의심)
            if start_year > input_year:
                anachronistic_objects.append(
                    f"'{name}' (출시: {start_year}년, 설명: {description})"
                )

        if anachronistic_objects:
            error_not_detected = False
            # 🚨 오류 문구 (고증 오류 의심)
            analysis_result = (
                f"🚨 고증 오류 의심: 이미지 연도({input_year}년)보다 늦게 출시된 객체 {len(anachronistic_objects)}개가 탐지되었습니다.\n"
                f"---------------------------------------------------\n"
                f"{'\n'.join(anachronistic_objects)}"
            )
        else:
            # ✅ 성공 문구 수정: 상세 정보와 비교 근거 포함
            
            # 1. 비교 근거 문구 생성
            comparison_details = []
            for name, start_year, description in rows:
                comparison_details.append(
                    f"'{name}' (출시: {start_year}년)은/는 요청 연도({input_year}년)보다 먼저 출시되어 고증 충돌이 없습니다."
                )
                
            # 2. 최종 분석 결과 문구 조합
            analysis_result = (
                f"\n✅ 이미지 분석 완료: 탐지된 객체 {len(detected_objects)}개는 연도({input_year}년)와 충돌하지 않습니다.\n"
                f"---------------------------------------------------\n"
                f"**[탐지 객체 목록 및 비교]**\n"
                f"{'\\n'.join(comparison_details)}"
            )
            
        # 6. 결과 반환
        return jsonify({
            'status': 'success',
            'year_received': input_year,
            'description': analysis_result, 
            'detected_count': len(detected_objects),
            'is_successful' : error_not_detected
        })
    

    except Exception as e:
        import traceback
        print("="*30 + " 파이썬 서버 오류 " + "="*30)
        traceback.print_exc() # 상세 오류 출력
        return jsonify({'status': 'error', 'description': f'파이썬 서버 처리 오류: {str(e)}'}), 500

if __name__ == '__main__':
    # Flask 실행
    app.run('0.0.0.0', port=8080, debug=True)