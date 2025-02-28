import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from flask import jsonify
from config import UPLOAD_FOLDER, RESULT_FOLDER
from flask import request, jsonify, send_file
import numpy as np

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

   # ✅ 5. 빨간색 선 양쪽(전방 & 후방)으로 50% 연장 후 그리기 (첫 번째와 세 번째 좌표 사용)
    start_point2 = np.array(points[0])  # (x1, y1) - 기존 시작점
    end_point2 = np.array(points[2])  # (x3, y3) - 기존 끝점

    # 🔹 벡터 계산 (방향: 기존 시작점 → 기존 끝점)
    vector = end_point2 - start_point2  # ✅ 벡터 = (x3 - x1, y3 - y1)

    # 🔹 벡터를 50% 확장 (양쪽으로 연장)
    extend_factor = 0.5  # 전체 길이의 50%만큼 연장
    extended_start = start_point2 - vector * extend_factor  # ✅ 후방으로 연장
    extended_end = end_point2 + vector * extend_factor  # ✅ 전방으로 연장

    # 🔹 정수 좌표로 변환
    extended_start = tuple(map(int, extended_start))
    extended_end = tuple(map(int, extended_end))

    red_color = (0, 0, 255)  # 빨간색
    cv2.line(image, extended_start, extended_end, red_color, thickness)

    # ✅ 6. 파란색 수직선 추가 (4번째 좌표에서 시작, 교차점에서 끝)
    center_point = np.array(points[3])  # (x4, y4) - 4번째 좌표

    # 🔹 빨간색 선과 수직 방향 벡터 (-dy, dx)
    perpendicular_vector = np.array([-vector[1], vector[0]])  # 수직 방향

    # 🔹 빨간색 선과 교차하는 점 찾기
    # 점 (x4, y4)에서 빨간색 선까지의 수직 거리 = 기존 벡터 길이의 50%만큼 이동
    intersect_factor = np.dot((center_point - start_point2), vector) / np.dot(vector, vector)  
    intersection_point = start_point2 + vector * intersect_factor  # 빨간색 선과의 교차점

    # 🔹 정수 좌표 변환
    intersection_point = tuple(map(int, intersection_point))
    center_point = tuple(map(int, center_point))  # 4번째 좌표는 시작점 그대로 유지

    blue_color = (255, 0, 0)  # 파란색
    cv2.line(image, center_point, intersection_point, blue_color, thickness)

    # ✅ 7. 처리된 이미지 저장
    output_filename = f"processed_{image_file.filename}"
    output_path = os.path.join(RESULT_FOLDER, output_filename)
    cv2.imwrite(output_path, image)

    # ✅ 8. 처리된 이미지 직접 반환
    return send_file(output_path, mimetype="image/jpeg")