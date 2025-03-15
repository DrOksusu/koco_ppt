from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from ppt_generator1 import create_ppt
from green_line import draw_psa_line
import os
from config import UPLOAD_FOLDER, RESULT_FOLDER
from werkzeug.utils import secure_filename
import logging
from flask import request

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():

    return render_template('index1.html')

@app.route('/dash_board', methods=['POST'])
def generate_ppt():
    try:
        result = create_ppt(request)
        return result
    except Exception as e:
        return jsonify({"error": str(e)})
    


@app.route('/upload_psa_image', methods=['POST'])
def upload_psa_image():
    """
    사용자가 이미지를 업로드하면 서버에 저장하고 URL을 반환하는 API
    """
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "선택된 파일이 없습니다."}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return jsonify({"message": "이미지 업로드 완료", "image_url": f"/static/uploads/{filename}"}), 200


@app.route('/draw_psa_line', methods=['POST'])
def draw_psa():
    print("draw_psa_line API 호출됨")
    try:
        result  = draw_psa_line()
        print("result", result)
        return result
    except Exception as e:
        print("error", str(e))
        return jsonify({"error": str(e)})
    
@app.route('/download_psa_result', methods=['GET'])
def download_psa_result():
    """
    PSA 선 그리기 결과 이미지 다운로드
    """
    file_path = os.path.join(RESULT_FOLDER, "psa_result.jpg")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "파일이 존재하지 않습니다."}), 404
    
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request():
    logging.info(f"📌 요청 수신: {request.method} {request.path}")

@app.route("/download/pdf")
def download_pdf():
    return send_file("/app/output_ppt.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9500, debug=True)
