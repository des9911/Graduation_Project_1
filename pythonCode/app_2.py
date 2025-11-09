from flask import Flask, request, jsonify
import base64
import json
import io
from PIL import Image

app = Flask(__name__)

# ⭐ 스프링 부트 서비스 코드의 URL과 일치해야 합니다.
@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    try:
        # 1. 스프링 부트로부터 JSON 데이터 받기
        data = request.get_json()
        base64_img = data.get('base64Image')
        year = data.get('year')
        file_name = data.get('fileName')

        if not base64_img or not year:
            return jsonify({'message': 'Base64 이미지 및 연도가 누락되었습니다.'}), 400

        # 2. Base64 문자열을 이미지 데이터로 디코딩
        img_bytes = base64.b64decode(base64_img)
        
        # 3. PIL (Pillow)을 사용하여 이미지 객체로 변환 (이미지 처리 준비)
        image = Image.open(io.BytesIO(img_bytes))

        # 4. ⭐ 여기에 실제 이미지 분석 및 K-Culture 연관 로직 구현 ⭐
        #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ


        # 예시: 연도와 파일 크기를 이용한 더미 분석 결과 생성
        width, height = image.size
        
        analysis_result = f"요청 연도 {year}년. 파일 '{file_name}' 분석 완료. (크기: {width}x{height} 픽셀)"
        
        if int(year) < 1600:
            analysis_result += " - 조선 초기~중기 이미지로 추정됩니다."
        else:
            analysis_result += " - 조선 후기 이후 또는 현대 이미지로 추정됩니다."

        # 5. 결과를 스프링 부트로 다시 JSON 형태로 반환
        return jsonify({
            'status': 'success',
            'year_received': year,
            # ⭐ 프론트엔드가 기대하는 'description' 키를 여기에 담아 반환
            'description': analysis_result 
        })

    except Exception as e:
        print(f"오류 발생: {e}")
        return jsonify({'message': f'파이썬 서버 처리 오류: {str(e)}'}), 500

if __name__ == '__main__':
    # ⭐ 스프링 서비스에 설정된 포트 8082와 일치해야 합니다.
    app.run('0.0.0.0', port=8082, debug=True)