import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from flask import jsonify
from config import UPLOAD_FOLDER, RESULT_FOLDER
from flask import request, jsonify, send_file

# 전역 변수
points = []  # 마우스로 찍은 좌표 저장
image = None  # 이미지 변수
window_name = "Draw Line"  # OpenCV 창 이름
save_button = None  # 저장 버튼 (선택한 후 활성화)

def draw_psa_line():
    """
    사용자가 업로드한 이미지와 선택한 좌표를 받아서 PSA 선을 그린 후 반환하는 API
    """
    # ✅ 1. 이미지와 좌표 데이터 받기
    if "image" not in request.files or "points" not in request.form:
        return jsonify({"error": "이미지 또는 좌표 데이터가 없습니다."}), 400

    image_file = request.files["image"]
    points_str = request.form["points"]  # JSON 문자열 형태

    # ✅ 2. JSON 문자열을 리스트로 변환
    try:
        points = eval(points_str)  # 문자열을 리스트로 변환
        if not isinstance(points, list) or len(points) < 2:
            return jsonify({"error": "잘못된 좌표 데이터"}), 400
    except Exception as e:
        return jsonify({"error": f"좌표 데이터 파싱 오류: {str(e)}"}), 400

    # ✅ 3. 이미지 저장 후 OpenCV로 읽기
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    image_file.save(image_path)

    image = cv2.imread(image_path)
    if image is None:
        return jsonify({"error": "이미지를 불러올 수 없습니다."}), 400

    # ✅ 4. 초록색 선 그리기 (첫 번째와 두 번째 좌표 사용)
    start_point = tuple(map(int, points[0]))  # (x1, y1)
    end_point = tuple(map(int, points[1]))  # (x2, y2)
    color = (0, 255, 0)  # 초록색
    thickness = 1

    cv2.line(image, start_point, end_point, color, thickness)

    # ✅ 5. 처리된 이미지 저장
    output_filename = f"processed_{image_file.filename}"
    output_path = os.path.join(RESULT_FOLDER, output_filename)
    cv2.imwrite(output_path, image)

    #  처리된 이미지 직접 반환
    return send_file(output_path, mimetype="image/jpeg")

    # ✅ 6. JSON 응답으로 이미지 URL 반환
    return jsonify({
        "message": "✅ PSA 선 그리기 완료",
        "processed_image_url": f"/download/{output_filename}"
    }), 200

