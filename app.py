from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import math
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from PIL import Image
import os
from flask_cors import CORS
import cv2
import numpy as np
import subprocess
import sys
import shutil
if sys.platform == "win32":
    import comtypes.client
    import pythoncom
    from comtypes.client import CreateObject

app = Flask(__name__)
CORS(app)

# 텍스트 프레임 양식 설정 함수
def TextFrame(ss, font_name='맑은 고딕', font_size=Pt(15), font_bold=True, ft_color=True, font_color=RGBColor(68, 84, 116)):
    for line in range(len(ss.text_frame.paragraphs)):
        ss.text_frame.paragraphs[line].font.name = font_name
        ss.text_frame.paragraphs[line].font.size = font_size
        ss.text_frame.paragraphs[line].font.bold = font_bold
        ss.text_frame.paragraphs[line].alignment = PP_ALIGN.CENTER
        if ft_color:
            ss.text_frame.paragraphs[line].font.color.rgb = font_color
    return ss

import os
import sys
import shutil
import subprocess

def convert_ppt_to_pdf(input_ppt, output_pdf):
    """
    PowerPoint 파일을 PDF로 변환하는 함수
    (Windows: pythoncom, Linux: LibreOffice 사용)
    
    :param input_ppt: 변환할 PPTX 파일의 절대 경로
    :param output_pdf: 변환된 PDF 파일이 저장될 절대 경로
    """
    input_ppt = os.path.abspath(input_ppt)
    output_pdf = os.path.abspath(output_pdf)

    print(f"📂 변환 시작: {input_ppt} -> {output_pdf}", flush=True)

    if sys.platform.startswith("win"):
        # Windows 환경: PowerPoint COM 객체 활용
        import comtypes.client
        import pythoncom

        pythoncom.CoInitializeEx(0)  # 멀티스레드 방식으로 COM 객체 초기화

        try:
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            powerpoint.Visible = 1  # PowerPoint 창을 보이도록 설정 (숨김 옵션 제거)

            print("🔄 PowerPoint PDF 변환 실행 중...", flush=True)

            # WithWindow=False 옵션 제거
            presentation = powerpoint.Presentations.Open(input_ppt, WithWindow=True)
            presentation.SaveAs(output_pdf, 32)  # 32 = PDF 변환 코드
            presentation.Close()

            if os.path.exists(output_pdf):
                print(f"✅ PDF 변환 성공: {output_pdf}", flush=True)
            else:
                raise FileNotFoundError(f"🚨 PDF 변환 실패: {output_pdf} 파일이 생성되지 않음")

        except Exception as e:
            print(f"❌ PDF 변환 중 오류 발생: {e}", flush=True)
        finally:
            powerpoint.Quit()
            pythoncom.CoUninitialize()

    else:
        # Linux 환경: LibreOffice 사용
        try:
            output_dir = os.path.dirname(output_pdf)
            base_name = os.path.splitext(os.path.basename(input_ppt))[0]  # 파일명 추출
            converted_pdf = os.path.join(output_dir, f"{base_name}.pdf")

            command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, input_ppt]
            print(f"🔄 LibreOffice 실행: {' '.join(command)}", flush=True)

            # LibreOffice 실행 (30초 타임아웃 추가)
            subprocess.run(command, check=True, timeout=30)

            # 변환된 파일 확인 후 이동
            if os.path.exists(converted_pdf):
                shutil.move(converted_pdf, output_pdf)
                print(f"✅ PDF 변환 성공: {output_pdf}", flush=True)
            else:
                raise FileNotFoundError(f"🚨 PDF 변환 실패: {output_pdf} 파일이 생성되지 않음")

        except subprocess.TimeoutExpired:
            print("⏳ PDF 변환이 너무 오래 걸려서 강제 종료됨!", flush=True)
        except Exception as e:
            print(f"❌ PDF 변환 중 오류 발생: {e}", flush=True)

# 옥수수 화이팅
# 🔹 1️⃣ 프론트엔드 (HTML) 서빙
@app.route('/')
def home():
    return render_template('index1.html')  # templates/index.html 제공

# 파일 저장 디렉토리 지정
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
print(f"📂 파일 업로드 디렉토리: {UPLOAD_FOLDER}")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(uploaded_file, filename, default_img=None):
    """
    파일을 저장하고, 저장되지 않으면 기본 이미지를 반환하는 함수.

    :param uploaded_file: Flask의 request.files에서 전달된 파일 객체
    :param filename: 저장할 파일 이름
    :param default_img: 기본 이미지 경로 (선택 사항)
    :return: 저장된 파일 경로 또는 기본 이미지 경로
    """
    if not uploaded_file or uploaded_file.filename == '':
        print(f"🚨 업로드된 파일이 없음, 기본 이미지 사용: {default_img}")
        return default_img if default_img else None  # 기본 이미지가 없으면 None 반환

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file_path = os.path.normpath(file_path)  # Windows에서 발생하는 \\ 이슈 방지

    try:
        uploaded_file.seek(0)  # 스트림 위치 초기화
        uploaded_file.save(file_path)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print(f"✅ {file_path} 파일 저장 완료 ({os.path.getsize(file_path)} bytes)")
            return file_path
        else:
            print(f"🚨 {file_path} 파일이 저장되지 않음, 기본 이미지 사용")
            return default_img if default_img else None
    except Exception as e:
        print(f"❌ 파일 저장 중 오류 발생: {e}, 기본 이미지 사용")
        return default_img if default_img else None
    

def create_first_slide(prs, df, df_raw, id_photo_path):
    temp_slide = prs.slides[0]
    shape_s = temp_slide.shapes

    #ppt table에 ceph 데이터 넣기
    for i in range(df.shape[0]):
        shape_s[7].table.cell(row_idx=i,col_idx =1).text = str(df.iloc[i,3])
        TextFrame(shape_s[7].table.cell(row_idx=i,col_idx =1),font_size=Pt(7),font_bold=False,ft_color=False)

    # Ceph 데이터 정리
    df = df.copy()
    df['Unnamed: 0'] = df['Unnamed: 0'].str.rstrip()
    ceph = {key: value for key, value in zip(df['Unnamed: 0'], df['Unnamed: 3'])}
    print("ceph:",ceph)

    # 수식 계산
    cosvalue = math.cos(math.radians(ceph['- AB<LOP']))
    a = 3.5 / 4.4 * cosvalue
    if ceph['APDI'] >= 81:
        if ceph['PMA'] < 27.5:
            IAPDI = 95 - 0.5 * ceph['PMA']
        else:
            IAPDI = 81
    else:
        IAPDI = 81 - a * (ceph['PMA'] - 27.5)

    IAPDI = round(IAPDI, 2)
    HGI = round(0.2 * ((ceph['MBL'] - ceph['ACBL']) * 2 + (ceph['UGA'] - 50) + 0.5 * (ceph['PCBA'] - 64)), 2)
    VGI = round(0.2 * ((ceph['FHR'] - 60) * 2 - (ceph['LGA'] - 75) + 0.5 * (ceph['ACBA'] - 7)), 2)
    APDL = round(0.4 * (ceph['APDI'] - IAPDI), 2)
    IODI = round(((80 - 0.3 * ceph['PMA'] - (0.776 - 0.008 * ceph['FMA']) * (ceph['FABA'] - 80))), 2)
    VDL = round(0.4849 * (ceph['ODI'] - IODI), 2)
    CFD = round(ceph['APDI'] + ceph['ODI'] - IAPDI - IODI, 2)

    # 고정 변수 설정
    fixed_var_dict = {
        8: 'C/C & Main problem',
        9: 'MPH:',
        11: f'HGI:{HGI}',
        13: f'VGI:{VGI}',
        17: f'IAPDI:{IAPDI}',
        19: f'2APDL:{APDL * 2}',
        20: f'IODI:{IODI}',
        22: f'VDL:{VDL}',
        24: 'CEPH RESULT',
        25: f'CFD:{CFD}',
        26: 'Extraction:'
    }

    for k, v in fixed_var_dict.items():
        shape_s[k].text = v
        TextFrame(shape_s[k], font_size=Pt(13), font_bold=True, ft_color=False)

    # 이름, 나이 등 정보 설정
    name = df_raw.iloc[3, 1]
    age = df_raw.iloc[3, 3]
    birth = df_raw.iloc[2, 3]
    gender = f'({df_raw.iloc[4, 1][0]})'

    soft_profile = 'S3' if ceph['FA`B`'] >= 83 else 'S1' if ceph['FA`B`'] >= 79 else 'S2'
    bony_profile = 'B3' if ceph['FABA'] >= 83 else 'B1' if ceph['FABA'] >= 79 else 'B2'
    denture_profile = 'D3' if 2 * APDL >= 2 else 'D1' if -1 <= 2 * APDL < 2 else 'D2'

    if ceph['Overbite'] > 3:
        nbt = 'dbt'
    elif -2 < ceph['Overbite'] <= 3:
        nbt = 'nbt'
    else:
        nbt = 'obt'

    if VDL > 1:
        skeletal_nbt = 'dbt'
    elif -4 < VDL <= 1:
        skeletal_nbt = 'nbt'
    else:
        skeletal_nbt = 'obt'

    shape_s[4].text = f"{gender} {name} {age} {birth}\n {soft_profile}.{bony_profile}.{denture_profile}.C1-{nbt}({skeletal_nbt})-RM(Rt)-Fx:Ex-Fx/1-Type IV"
    TextFrame(shape_s[4])

    # 이미지 처리
    with Image.open(id_photo_path) as img:
        width, height = img.size
        wpercent = 1.6 / float(width)
        new_height = round(float(height) * wpercent, 1)

        left = Inches(2.7)
        top = Inches(0.55)
        width = Inches(1.6)
        height = Inches(new_height)
        temp_slide.shapes.add_picture(id_photo_path, left, top, width, height)
    
    # HGI, VGI 값을 반환
    print(f"HGI: {HGI}, VGI: {VGI}")
    print("첫번째 슬라이드 완료")
    return HGI, VGI

def create_second_slide(prs, HGI, VGI, psa_name_path):
    # 두 번째 슬라이드 만들기
    temp_slide_1 = prs.slides[1] #2번째 슬라이드를 KOCO 프레임에서가지고 오기
    shape_s_1= temp_slide_1.shapes
    
    # PSA 이미지가 기본 이미지라면 복잡한 연산 생략
    if psa_name_path == "./static/default_image.jpg":
        print("🚨 PSA 이미지 없음 -> 기본 이미지로 대체하여 슬라이드 생성", flush=True)

        # 기본 이미지 처리
        # exp = "default_psa_result"
        img_psa = Image.open(psa_name_path)
        print("img_psa.size:", img_psa.size, flush=True, file=sys.stderr)

        # 이미지 크기 조정 및 삽입
        if img_psa.size[1] / img_psa.size[0] < 19.05 / 25.4:
            w = 10
            print("w:", w, flush=True, file=sys.stderr)
            width = Inches(w)
            print("w:", w, flush=True, file=sys.stderr)
            h = w * img_psa.size[1] / img_psa.size[0]
            height = Inches(h)
            left = Inches(0)
            top = Inches(((19.05 / 2.54) - h) / 2)
        else:
            h = 19.05 / 2.54
            height = Inches(h)
            w = h * img_psa.size[0] / img_psa.size[1]
            width = Inches(w)
            left = Inches((10 - w) / 2)
            top = Inches(0)

        print("w:", w, flush=True, file=sys.stderr)
        print("h:", h, flush=True, file=sys.stderr)
        shape_s_1.add_picture(psa_name_path, left, top, width, height)
        print("두번째 슬라이드 완료", flush=True, file=sys.stderr)
    
        return  # 여기서 함수 종료

    #psa 를 위해서 이미지 객체 만들기
    print("psa_name_path:", psa_name_path, flush=True, file=sys.stderr)
    psa_image = cv2.imread(psa_name_path, cv2.IMREAD_COLOR)
    psa_height, psa_width, psa_channels = psa_image.shape
    print("psa_width:", psa_width, flush=True, file=sys.stderr)
    print("psa_image.shape:", psa_image.shape, flush=True, file=sys.stderr)

    ### 이름 나온 곳 검은색으로 칠해주기

    x_start = int(psa_width)
    y_start = int(psa_height/4)

    image = cv2.rectangle(psa_image, (0,0), (x_start, y_start),(0,0,0),-1)


    x_start = int(psa_width/3)
    y_start = int(psa_height)
    image = cv2.rectangle(psa_image, (0,0), (x_start, y_start),(0,0,0),-1)

    # 초록색 색상 범위 설정
    lower_green = (30, 80, 80)
    upper_green = (70, 255, 255)


    # RGB 에서 HSV 로 색상지정방식 변경
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #마스크 씌우기
    img_mask = cv2.inRange(img_hsv, lower_green, upper_green)

    #사진상에서 초록색만 남기는 것(마스크를 씌움)
    img_result = cv2.bitwise_and(image, image, mask=img_mask)

    
    # 특정색상이 검출되지 않으면 이 부분은 건너뜀
    if img_result is None:
        print("❌ 특정 색상이 검출되지 않아 이미지 처리를 건너뜁니다.")
        return
    
    print("이미지색상 검출",flush=True, file=sys.stderr)
    

    nonzero_values = img_result.nonzero()
    if len(nonzero_values[0]) > 0 and len(nonzero_values[1]) > 0:
        d = nonzero_values[0][0]
        b = nonzero_values[0][-1]
        c = nonzero_values[1][0]
        a = nonzero_values[1][-1]
    else:
        print("🚨 이미지에서 초록색 픽셀을 찾을 수 없습니다.", flush=True, file=sys.stderr)
        d, b, c, a = 0, 0, 0, 0  # 기본값 설정

    # 하절치점의 좌표는 array 에서 columns 에 해당하는 [1]의 마지막 값이다 [-1] 결국 [1][-1] =a (하절치의 x 좌표)

    # 남은 하나 꼭짓점 좌표 구하기
    x0 = int((a+c)/2 - (np.sqrt(3)*(d-b))/2)
    y0 = int((b+d)/2 + (np.sqrt(3)*(c-a))/2)

    x1 = int((a+c)/2 + (np.sqrt(3)*(d-b))/2)
    y1 = int((b+d)/2 - (np.sqrt(3)*(c-a))/2)

    if x0 > x1:
        x = x0
    else:
        x = x1

    if y0 < y1:
        y = y0
    else:
        y = y1
        
    # 좌표 위치 묶어주기 
    pts = np.array([[a,b],[c,d],[x,y]],dtype=np.int32)
    image = cv2.imread(psa_name_path, cv2.IMREAD_COLOR)

    # 삼각형 그리기
    src = cv2.polylines(image, [pts], isClosed=True, color = (0,255,255))


    print('1')

    # 변 길이

    lim = int(np.sqrt((a-c)**2+(b-d)**2))

    # 원그리기1
    src = cv2.circle(image, (x,y), radius=lim, color = (0,255,255))

    # 원그리기 2
    src = cv2.circle(src, (a,b), radius=lim, color = (0,255,255))

    #화살표그리기(성장방향)
    psa_image = cv2.imread(psa_name_path, cv2.IMREAD_COLOR)
    #lateral_ceph = 'lateral_ceph.jpg'


    # img_lateral_ceph = cv2.imread(lateral_ceph, cv2.IMREAD_COLOR)
    s_x = 1150
    s_y = 200
    color = (0,0,255)
    pt1 = (s_x, s_y)

    #HGI, VGI 가 None 이 아니라면 화살표 그리고 None 이면 pass 하기
    if HGI is None or VGI is None:
        print("HGI, VGI 값이 없습니다.")
        pass
    else:
        pt2 = (int((s_x +(HGI*100)/4)), int((s_y - (VGI*100)/4)))
        img_arrow = cv2.arrowedLine(src, pt1,pt2, color= (0,0,255))

    # pt2 = (int((s_x +(HGI*100)/4)), int((s_y - (VGI*100)/4)))
    # img_arrow = cv2.arrowedLine(src, pt1,pt2, color= (0,0,255))


    # 결과이미지 저장하기
    psa_name = os.path.basename(psa_name_path)
    exp = psa_name.strip().split('.')[0]
    print("exp:",exp)
    if src is not None:
        save_path = f"{exp}_result.png"
        success = cv2.imwrite(save_path, src)
        if success:
            print(f"✅ 결과 이미지 저장 완료: {save_path}")
        else:
            print(f"❌ 이미지 저장 실패: {save_path}")
    else:
        print("❌ 저장할 이미지 데이터가 없습니다.")
    
        
    img_psa = Image.open(f"{exp}_result.png")
    if img_psa.size[1]/img_psa.size[0] < 19.05/25.4 :
        w = 10
        width = Inches(w)
        h = w * img_psa.size[1]/img_psa.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches(((19.05/2.54)-h)/2)
        
    else:
        h = 19.05/2.54
        height = Inches(h)
        w = h * img_psa.size[0]/img_psa.size[1]
        width = Inches(w)
        left = Inches((10-w)/2)
        top = Inches(0)
    shape_s_1.add_picture(f"{exp}_result.png",left, top, width, height)

    print("두번째 슬라이드 완료",flush=True, file=sys.stderr)

# 3번째 슬라이드 생성 함수 (구외사진)
def create_third_slide(prs, default_img):
    """
    구외사진 8장을 3번째 슬라이드에 추가하는 함수.
    빈 사진이 있으면 기본 이미지('./static/default_image.jpg')로 대체.

    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 파일 경로
    """
    print("📂 3번째 슬라이드 생성 시작...", flush=True, file=sys.stderr)
    # 파일 저장 후 경로 리스트 만들기
    photo_paths = []
    
    for idx in range(8):  # 총 8개의 사진이 필요
        uploaded_file = request.files.get(f'photo{idx+1}')  # Flask에서 안전하게 파일 가져오기
        print(f"📂 업로드된 파일 목록: {list(request.files.keys())}")
        saved_path = save_uploaded_file(uploaded_file, f'photo_{idx+1}.jpg', default_img="./static/default_image.jpg")
        photo_paths.append(saved_path)  # 정상적으로 저장된 파일만 추가

    print(f"🔍 최종 photo_paths: {photo_paths}")  # 디버깅용 출력
    # 제발^^
    # 3번째 슬라이드 가져오기
    temp_slide_2 = prs.slides[2]
    shape_s_2 = temp_slide_2.shapes

    # 이미지 배치 설정 (2행 x 4열)
    num_cols = 4  # 한 행에 4개씩 배치
    num_rows = 2  # 두 개의 행으로 배치

    # 슬라이드 크기에 맞게 이미지 크기 설정
    slide_width = 10  # 슬라이드 너비 (인치 단위)
    slide_height = 19.05 / 2.54  # 슬라이드 높이 (cm를 인치로 변환)
    img_height = slide_height / num_rows  # 한 행에 배치할 이미지 높이

    # 첫 번째 이미지를 불러와 비율 계산
    img_sample = Image.open(photo_paths[0])
    aspect_ratio = img_sample.size[0] / img_sample.size[1]  # 가로/세로 비율
    img_width = img_height * aspect_ratio  # 이미지 가로 크기

    # 중앙 정렬을 위한 시작 좌표 계산
    total_width = img_width * num_cols  # 전체 이미지 영역의 너비
    left_start = (slide_width - total_width) / 2  # 좌측 여백 계산

    # 이미지 삽입
    for idx, img_path in enumerate(photo_paths[:8]):  # 첫 8개만 사용
        row = idx // num_cols  # 행 계산 (0 or 1)
        col = idx % num_cols  # 열 계산 (0 ~ 3)

        left = Inches(left_start + col * img_width)  # 가로 위치
        top = Inches(row * img_height)  # 세로 위치

        shape_s_2.add_picture(img_path, left, top, width=Inches(img_width), height=Inches(img_height))

    print("✅ 3번째 슬라이드에 구외사진 추가 완료!")

def create_fourth_slide(prs, oral_default_img):
    """
    구내사진 5장을 4번째 슬라이드에 추가하는 함수.
    빈 사진이 있으면 기본 이미지로 대체.

    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 파일 경로
    """
    # 파일 저장 후 경로 리스트 만들기
    photo_paths = []
    for idx in range(5):  # 총 5개의 사진이 필요
        uploaded_file = request.files.get(f'oralPhoto{idx+1}')  # Flask에서 안전하게 파일 가져오기
        saved_path = save_uploaded_file(uploaded_file, f'oralPhoto_{idx+1}.jpg',  default_img="./static/oral_default.jpg")
        photo_paths.append(saved_path)  # 정상적으로 저장된 파일만 추가

    print(f"🔍 최종 photo_paths: {photo_paths}")  # 디버깅용 출력      


    # 4번째 슬라이드 가져오기
    temp_slide_3 = prs.slides[3]
    shape_s_3 = temp_slide_3.shapes

    # 이미지 크기 및 위치 설정
    h = 2.2  # 높이 설정 (인치 단위)
    height = Inches(h)
    w = h * Image.open(photo_paths[0]).size[0] / Image.open(photo_paths[0]).size[1]
    width = Inches(w)

    # 상악사진
    left = Inches((10 - 2 * w) / 2)
    top = Inches(1)
    shape_s_3.add_picture(photo_paths[0], left, top, width, height)

    # 하악사진
    left = Inches((10 - 2 * w) / 2 + w)
    shape_s_3.add_picture(photo_paths[1], left, top, width, height)

    # 교합 좌측
    left = Inches((10 - 3 * w) / 2)
    top = Inches(1 + h)
    shape_s_3.add_picture(photo_paths[2], left, top, width, height)

    # 교합 정면
    left = Inches((10 - 3 * w) / 2 + w)
    shape_s_3.add_picture(photo_paths[3], left, top, width, height)

    # 교합 우측
    left = Inches((10 - 3 * w) / 2 + 2 * w)
    shape_s_3.add_picture(photo_paths[4], left, top, width, height)

    print("✅ 4번째 슬라이드에 모든 이미지 추가 완료!")



def create_fifth_slide(prs, default_img):
    """
    Pano 이미지를 5번째 슬라이드에 추가하는 함수.
    만약 업로드된 Pano 이미지가 없거나 손상되었을 경우, 기본 이미지 사용.

    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 파일 경로
    """

    # Pano 이미지 업로드 확인
    pano_file = request.files.get('pano')  # Flask에서 request로 직접 가져옴

    if pano_file and pano_file.filename:
        # 파일 저장 후 경로 설정
        pano_path = save_uploaded_file(pano_file, 'pano.jpg')

        # 파일 유효성 검사 (파일이 존재하고 크기가 0보다 커야 함)
        if not os.path.exists(pano_path) or os.path.getsize(pano_path) == 0:
            print(f"🚨 Pano 이미지가 없거나 손상됨: {pano_path}, 기본 이미지 사용")
            pano_path = default_img  # 기본 이미지로 변경
        else:
            try:
                # 이미지 유효성 검사
                with Image.open(pano_path) as img:
                    img.verify()
                print(f"✅ 유효한 Pano 이미지 확인: {pano_path}")
            except Exception as e:
                print(f"🚨 유효하지 않은 Pano 이미지 파일: {pano_path}, 기본 이미지 사용")
                pano_path = default_img  # 기본 이미지로 변경
    else:
        print(f"🚨 Pano 이미지가 업로드되지 않음, 기본 이미지 사용")
        pano_path = default_img  # 기본 이미지로 변경

    # 5번째 슬라이드 가져오기
    temp_slide_4 = prs.slides[4]  # 슬라이드 인덱스는 0부터 시작하므로 5번째는 인덱스 4
    shape_s_4 = temp_slide_4.shapes

    # 이미지 열기
    img_pano = Image.open(pano_path)

    # 슬라이드 크기 (인치 단위)
    slide_width = 10
    slide_height = 19.05 / 2.54  # cm를 inch로 변환

    # 이미지 비율에 따라 크기 조정
    if img_pano.size[1] / img_pano.size[0] < slide_height / slide_width:
        w = slide_width
        width = Inches(w)
        h = w * img_pano.size[1] / img_pano.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches((slide_height - h) / 2)  # 중앙 정렬
    else:
        h = slide_height
        height = Inches(h)
        w = h * img_pano.size[0] / img_pano.size[1]
        width = Inches(w)
        left = Inches((slide_width - w) / 2)  # 중앙 정렬
        top = Inches(0)

    # 이미지 추가
    shape_s_4.add_picture(pano_path, left, top, width, height)

    print("✅ 5번째 슬라이드에 Pano 이미지 추가 완료!")

   
def create_sixth_slide(prs, default_img):
    """
    Lateral Ceph 이미지를 6번째 슬라이드에 추가하는 함수.
    만약 업로드된 Lateral Ceph 이미지가 없거나 손상되었을 경우, 기본 이미지 사용.

    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 파일 경로
    """

    # Lateral Ceph 이미지 업로드 확인
    lateral_ceph_file = request.files.get('lateral_ceph')  # Flask에서 request로 직접 가져옴

    if lateral_ceph_file and lateral_ceph_file.filename:
        # 파일 저장 후 경로 설정
        lateral_ceph_path = save_uploaded_file(lateral_ceph_file, 'lateral_ceph.jpg')

        # 파일 유효성 검사 (파일이 존재하고 크기가 0보다 커야 함)
        if not os.path.exists(lateral_ceph_path) or os.path.getsize(lateral_ceph_path) == 0:
            print(f"🚨 Lateral Ceph 이미지가 없거나 손상됨: {lateral_ceph_path}, 기본 이미지 사용")
            lateral_ceph_path = default_img  # 기본 이미지로 변경
        else:
            try:
                # 이미지 유효성 검사
                with Image.open(lateral_ceph_path) as img:
                    img.verify()
                print(f"✅ 유효한 Lateral Ceph 이미지 확인: {lateral_ceph_path}")
            except Exception as e:
                print(f"🚨 유효하지 않은 Lateral Ceph 이미지 파일: {lateral_ceph_path}, 기본 이미지 사용")
                lateral_ceph_path = default_img  # 기본 이미지로 변경
    else:
        print(f"🚨 Lateral Ceph 이미지가 업로드되지 않음, 기본 이미지 사용")
        lateral_ceph_path = default_img  # 기본 이미지로 변경

    # 6번째 슬라이드 가져오기
    temp_slide_5 = prs.slides[5]  # 슬라이드 인덱스는 0부터 시작하므로 6번째는 인덱스 5
    shape_s_5 = temp_slide_5.shapes

   # 이미지 열기
    img_pano = Image.open(lateral_ceph_path)

    # 슬라이드 크기 (인치 단위)
    slide_width = 10
    slide_height = 19.05 / 2.54  # cm를 inch로 변환

    # 이미지 비율에 따라 크기 조정
    if img_pano.size[1] / img_pano.size[0] < slide_height / slide_width:
        w = slide_width
        width = Inches(w)
        h = w * img_pano.size[1] / img_pano.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches((slide_height - h) / 2)  # 중앙 정렬
    else:
        h = slide_height
        height = Inches(h)
        w = h * img_pano.size[0] / img_pano.size[1]
        width = Inches(w)
        left = Inches((slide_width - w) / 2)  # 중앙 정렬
        top = Inches(0)

    # 이미지 추가
    shape_s_5.add_picture(lateral_ceph_path, left, top, width, height)

    print("✅ 6번째 슬라이드에 Lateral Ceph 이미지 추가 완료!")
   

def create_seventh_slide(prs, default_img):
    """
    Frontal Ceph 이미지를 7번째 슬라이드에 추가하는 함수.
    만약 업로드된 Frontal Ceph 이미지가 없거나 손상되었을 경우, 기본 이미지 사용.

    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 파일 경로
    """

    # Frontal Ceph 이미지 업로드 확인
    frontal_ceph_file = request.files.get('frontal_ceph')  # Flask에서 request로 직접 가져옴

    if frontal_ceph_file and frontal_ceph_file.filename:
        # 파일 저장 후 경로 설정
        frontal_ceph_path = save_uploaded_file(frontal_ceph_file, 'frontal_ceph.jpg')

        # 파일 유효성 검사 (파일이 존재하고 크기가 0보다 커야 함)
        if not os.path.exists(frontal_ceph_path) or os.path.getsize(frontal_ceph_path) == 0:
            print(f"🚨 Frontal Ceph 이미지가 없거나 손상됨: {frontal_ceph_path}, 기본 이미지 사용")
            frontal_ceph_path = default_img  # 기본 이미지로 변경
        else:
            try:
                # 이미지 유효성 검사
                with Image.open(frontal_ceph_path) as img:
                    img.verify()
                print(f"✅ 유효한 Frontal Ceph 이미지 확인: {frontal_ceph_path}")
            except Exception as e:
                print(f"🚨 유효하지 않은 Frontal Ceph 이미지 파일: {frontal_ceph_path}, 기본 이미지 사용")
                frontal_ceph_path = default_img  # 기본 이미지로 변경
    else:
        print(f"🚨 Frontal Ceph 이미지가 업로드되지 않음, 기본 이미지 사용")
        frontal_ceph_path = default_img  # 기본 이미지로 변경

    # 7번째 슬라이드 가져오기
    temp_slide_6 = prs.slides[6]  # 슬라이드 인덱스는 0부터 시작하므로 7번째는 인덱스 6
    shape_s_6 = temp_slide_6.shapes

    # 이미지 열기
    img_pano = Image.open(frontal_ceph_path)

    # 슬라이드 크기 (인치 단위)
    slide_width = 10
    slide_height = 19.05 / 2.54  # cm를 inch로 변환

    # 이미지 비율에 따라 크기 조정
    if img_pano.size[1] / img_pano.size[0] < slide_height / slide_width:
        w = slide_width
        width = Inches(w)
        h = w * img_pano.size[1] / img_pano.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches((slide_height - h) / 2)  # 중앙 정렬
    else:
        h = slide_height
        height = Inches(h)
        w = h * img_pano.size[0] / img_pano.size[1]
        width = Inches(w)
        left = Inches((slide_width - w) / 2)  # 중앙 정렬
        top = Inches(0)

    # 이미지 추가
    shape_s_6.add_picture(frontal_ceph_path, left, top, width, height)

    print("✅ 7번째 슬라이드에 Frontal Ceph 이미지 추가 완료!")




   
# PPT 작성 엔드포인트
@app.route('/dash_board', methods=['POST'])
def create_ppt():
    try:
        # 포스트 요청이 아닌 경우 405 에러 반환
        print("request.method:", request.method, flush=True, file=sys.stderr)
        print("request.files.keys():", list(request.files.keys()), flush=True, file=sys.stderr)
        print("request.form.keys():", list(request.form.keys()), flush=True, file=sys.stderr)

        if request.method != 'POST':
            return jsonify({"error": "Only POST requests are allowed."}), 405
        
        
        triangle = '화살표.png'
        print("용주야 사랑해",flush=True, file=sys.stderr)        

        # 파일 저장
        pano = request.files['pano']
        lateral_ceph_image = request.files['lateral_ceph']
        frontal_ceph_image = request.files['frontal_ceph']
        psa_name = request.files['psa']
        id_photo = request.files['photo4']

        # 파일 저장 (None이 되지 않도록 기본 이미지 적용)
        pano_path = save_uploaded_file(request.files.get('pano'), 'pano.jpg', default_img="./static/default_image.jpg")
        print("pano_path:",pano_path, flush=True, file=sys.stderr)
        lateral_ceph_path = save_uploaded_file(request.files.get('lateral_ceph'), 'lateral_ceph.jpg', default_img="./static/default_image.jpg")
        frontal_ceph_path = save_uploaded_file(request.files.get('frontal_ceph'), 'frontal_ceph.jpg', default_img="./static/default_image.jpg")
        psa_name_path = save_uploaded_file(request.files.get('psa'), 'psa_name.jpg', default_img="./static/default_image.jpg")
        id_photo_path = save_uploaded_file(request.files.get('photo4'), 'id_photo.jpg', default_img="./static/oral_default.jpg")
        print("id_photo_path:",id_photo_path, flush=True, file=sys.stderr)
        print("psa_name_path:",psa_name_path, flush=True, file=sys.stderr)

        
        excel_file = request.files['excel_data']
        file_type = request.form.get('file_type', 'pdf') #기본값은 pdf

        print("file_type:",file_type, flush=True, file=sys.stderr)
        
        # 엑셀 파일이 비어있는지 확인
        if excel_file and excel_file.filename != '': 
            excel_file_path = save_uploaded_file(excel_file, 'excel_data.xlsx')
            df_raw = pd.read_excel(excel_file_path)
            df = df_raw.iloc[7:]  # 7번째 행 이후의 데이터 사용
        else:
            df_raw, df, excel_file_path = None, None, None

        print("df_raw:",df_raw, flush=True, file=sys.stderr)


        # PPT 템
        # 현재 디렉터리에서 파일 경로를 생성
        ppt_template_path = os.path.join(os.getcwd(), 'koco_frame.pptx')

        # PPT 템플릿 로드
        prs = Presentation(ppt_template_path)
        
       # 첫 번째 슬라이드 만들기 (엑셀 파일이 있을 경우만)
        if df_raw is not None and not df_raw.empty:            
            # 슬라이드 생성
            HGI, VGI = create_first_slide(prs, df, df_raw, id_photo_path)
            print("HGI:",HGI, flush=True, file=sys.stderr)
        else:
            HGI, VGI = None, None  # 값이 없으면 이후 슬라이드에서 참고하지 않도록
            print("HGI:",HGI, flush=True, file=sys.stderr)
            print("VGI:",VGI, flush=True, file=sys.stderr)
                
         # 두 번째 슬라이드 만들기 (PSA 파일이 있을 경우만)
        print("두번째 슬라이드 시작",flush=True, file=sys.stderr)
        create_second_slide(prs, HGI, VGI, psa_name_path)       


        ####3번째 슬라이드 만들기(구외사진)
        create_third_slide(prs, default_img="./static/default_image.jpg")

        ####4번째 슬라이드 만들기(구내사진)
        create_fourth_slide(prs, oral_default_img="./static/oral_default.jpg")

        #### 5번째 슬라이드 만들기 (Pano 이미지)
        create_fifth_slide(prs, default_img="./static/default_image.jpg")
    
        ####6번째 슬라이드 만들기 (Lateral Ceph)
        create_sixth_slide(prs, default_img="./static/default_image.jpg")
       
        ####7번째 슬라이드 만들기 (Frontal Ceph)
        create_seventh_slide(prs, default_img="./static/default_image.jpg")

        # PPT 저장
        output_pptx = 'output_ppt.pptx'
        print("output_pptx:",output_pptx, flush=True, file=sys.stderr)
        prs.save(output_pptx)
        print("PPT 저장 완료", flush=True, file=sys.stderr)

    
        
        # 임시 파일 삭제
        
        # print("제발")
        # if os.path.exists(excel_file_path):
        #     os.remove(excel_file_path)
        #     print(f"임시 엑셀 파일 삭제: {excel_file_path}", flush=True, file=sys.stderr)
        # else:
        #     print(f"삭제할 엑셀 파일이 없습니다: {excel_file_path}", flush=True, file=sys.stderr)
        
        if file_type == 'pdf':
            print("PDF 변환 시작까지는 되는 듯",flush=True, file=sys.stderr)
            output_pdf = 'output_ppt.pdf'
            convert_ppt_to_pdf(output_pptx, output_pdf)  # PDF 변환 로직 (구현 필요)

            return send_file(output_pdf, as_attachment=True, mimetype='application/pdf')

        # PPTX 파일 전송
        return send_file(output_pptx, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')


    except Exception as e:
        return jsonify({"error": str(e)})



    
# 🔹 테스트페이지
@app.route('/koco')
def koco_page():
    return "순응교합연구회 만세!"  # templates/index.html 제공

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9500, debug=True)

