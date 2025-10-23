import os
import pandas as pd
from pptx import Presentation
from flask import send_file
from utils import save_uploaded_file, convert_ppt_to_pdf # 사용자 정의 함수
from config import UPLOAD_FOLDER
import sys
from pptx.util import Pt, Inches
from flask import request, jsonify, send_file
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import math
from PIL import Image
import cv2
import numpy as np
import json
from datetime import datetime, timedelta
import random
import traceback




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

def create_ppt(request):
    """ PPT 생성하는 메인 함수 """
    print("request.method:", request.method, flush=True, file=sys.stderr)
    print("request.files.keys():", list(request.files.keys()), flush=True, file=sys.stderr)
   

    if request.method != 'POST':
        return jsonify({"error": "Only POST requests are allowed."}), 405
    
    
    triangle = '화살표.png'
    print("용주야 사랑해",flush=True, file=sys.stderr)        

    # 파일 저장
    # pano = request.files['pano']
    # lateral_ceph_image = request.files['lateral_ceph']
    # frontal_ceph_image = request.files['frontal_ceph']
    # psa_name = request.files['psa']
    # id_photo = request.files['photo4']

    # 파일 저장 (None이 되지 않도록 기본 이미지 적용)
    pano_path = save_uploaded_file(request.files.get('pano'), 'pano.jpg', default_img="./static/default_image.jpg")
    lateral_ceph_path = save_uploaded_file(request.files.get('lateral_ceph'), 'lateral_ceph.jpg', default_img="./static/default_image.jpg")
    frontal_ceph_path = save_uploaded_file(request.files.get('frontal_ceph'), 'frontal_ceph.jpg', default_img="./static/default_image.jpg")
    psa_path = save_uploaded_file(request.files.get('psa'), 'psa.jpg', default_img="./static/default_image.jpg")  # ✅ PSA (2번째 슬라이드)
    frontal_ax_path = save_uploaded_file(request.files.get('frontal_ax'), 'frontal_ax.jpg', default_img="./static/default_image.jpg")  # ✅ Frontal Ax (11번째 슬라이드)
    id_photo_path = save_uploaded_file(request.files.get('photo4'), 'id_photo.jpg', default_img="./static/oral_default.jpg")
    pso_path = save_uploaded_file(request.files.get('pso'), 'pso.jpg', default_img="./static/default_image.jpg")  # ✅ PSO (10번째 슬라이드)
    print("frontal_ceph_path:",frontal_ceph_path)
    print("frontal_ax_path:",frontal_ax_path)

    excel_file = request.files.get('excel_data')
    print("excel_file:",excel_file, flush=True, file=sys.stderr)
    ceph_dict_raw = request.form.get('totalData')
    # ceph_add_raw= request.form.get('excel_add')
    print("ceph_dict_raw:",ceph_dict_raw, flush=True, file=sys.stderr)
    
   # 2. JSON 문자열 → 파이썬 객체로 파싱
    try:
        # ceph_dict_raw가 None이 아니고 문자열일 경우만 파싱 시도
        if ceph_dict_raw:
            ceph = json.loads(ceph_dict_raw)   # 리스트 형태
            print("ceph:", ceph, flush=True, file=sys.stderr)
        else:
            ceph = []  # 기본 빈 리스트로 설정
            print("⚠️ ceph_dict_raw가 None이거나 비어있습니다. 빈 리스트로 대체합니다.", flush=True, file=sys.stderr)

       
    except json.JSONDecodeError:
        print("🚨 JSON 변환 오류: ceph_dict_raw 또는 ceph_add_raw가 올바른 JSON 형식이 아닙니다.", flush=True, file=sys.stderr)
        ceph = []
        ceph_add = {}
   

    except Exception as e:
        print(f"🚨 ceph 병합 중 오류 발생: {e}", flush=True, file=sys.stderr)


    file_type = request.form.get('file_type', 'pdf') #기본값은 pdf

    print("file_type:",file_type, flush=True, file=sys.stderr)
    
    # 현재 디렉터리에서 파일 경로를 생성
    ppt_template_path = os.path.join(os.getcwd(), 'koco_frame.pptx')

    # PPT 템플릿 로드
    prs = Presentation(ppt_template_path)

    # 엑셀 파일이 비어있는지 확인
    if excel_file and excel_file.filename != '': 
        excel_file_path = save_uploaded_file(excel_file, 'excel_data.xlsx')
        df_raw = pd.read_excel(excel_file_path)
        df = df_raw.iloc[7:]  # 7번째 행 이후의 데이터 사용
        df = df.copy()  # 원본 보호
        df['Unnamed: 0'] = df['Unnamed: 0'].str.rstrip()  # 공백 제거
        ceph ={}        
        ceph = {key: value for key, value in zip(df['Unnamed: 0'], df['Unnamed: 3'])}
        print("📌 엑셀 데이터:", ceph, flush=True, file=sys.stderr)        
        HGI, VGI = create_first_slide(prs, ceph, id_photo_path, df_raw)
        print("HGI:",HGI, flush=True, file=sys.stderr)

    # ✅ 엑셀 파일이 없지만 ceph_dict가 존재하는 경우
    elif ceph:
        try:
            # ceph = json.loads(ceph_dict)  # JSON 문자열을 딕셔너리로 변환
            print("📌 ceph_dict에서 변환된 ceph:", ceph, flush=True, file=sys.stderr)
            HGI, VGI = create_first_slide(prs, ceph, id_photo_path, None)
            print("HGI:",HGI, flush=True, file=sys.stderr)
        except json.JSONDecodeError:
            print("🚨 JSON 변환 오류: ceph_dict가 올바른 JSON 형식이 아닙니다.", flush=True, file=sys.stderr)
            ceph = None  # 변환 실패 시 None 설정
            df_raw, df, excel_file_path = None, None, None
        
    # ✅ 엑셀 파일도 없고 ceph_dict도 없는 경우
    else:
        df_raw, df, excel_file_path, ceph = None, None, None, None
        print("🚨 엑셀 파일과 ceph_dict 둘 다 없습니다.", flush=True, file=sys.stderr)
        HGI, VGI = None, None  # 값이 없으면 이후 슬라이드에서 참고하지 않도록
        print("HGI:",HGI, flush=True, file=sys.stderr)
        print("VGI:",VGI, flush=True, file=sys.stderr)       
    
    
    
    #### 두 번째 슬라이드 만들기 (PSA 파일이 있을 경우만)
    print("두번째 슬라이드 시작",flush=True, file=sys.stderr)
    create_second_slide(prs, HGI, VGI, psa_path)       


    ####3번째 슬라이드 만들기(구외사진)
    create_third_slide(prs, default_img="./static/default_image.jpg")

    ####4번째 슬라이드 만들기(구내사진)
    create_fourth_slide(prs, oral_default_img="./static/oral_default.jpg")

    #### 5번째 슬라이드 만들기 (Pano 이미지)
    create_fifth_slide(prs, pano_path)

    ####6번째 슬라이드 만들기 (Lateral Ceph)
    create_sixth_slide(prs, lateral_ceph_path)
    
    ####7번째 슬라이드 만들기 (Frontal Ceph)
    create_seventh_slide(prs, frontal_ceph_path)

    ####8번째 슬라이드 만들기 (자세사진)
    create_eighth_slide(prs, default_img="./static/posture_default.jpg")

    ####9번째 슬라이드 만들기 (자세사진추가)
    create_ninth_slide(prs, default_img="./static/posture_default.jpg")

    ###10번째 슬라이드 만들기 (PSO 결과)
    create_tenth_slide(prs, pso_path)

    ###11번째 슬라이드 만들기 (Frontal Ax. 결과)
    create_eleventh_slide(prs, frontal_ax_path)



    # PPT 저장
    output_pptx = 'output_ppt.pptx'
    print("output_pptx:",output_pptx, flush=True, file=sys.stderr)
    prs.save(output_pptx)
    print("PPT 저장 완료", flush=True, file=sys.stderr)   
    
    
    if file_type == 'pdf':
        print("PDF 변환 시작까지는 되는 듯",flush=True, file=sys.stderr)
        output_pdf = 'output_ppt.pdf'
        convert_ppt_to_pdf(output_pptx, output_pdf)  # PDF 변환 로직 (구현 필요)
         # ✅ 파일이 존재하는지 확인
        if not os.path.exists(output_pdf):
            print(f"🚨 파일이 존재하지 않습니다: {output_pdf}", flush=True)
            return "파일이 존재하지 않습니다", 404

        # ✅ 파일 크기 확인
        file_size = os.path.getsize(output_pdf)
        print(f"📌 PDF 파일 크기: {file_size} bytes", flush=True)

        # ✅ 헤더 설정 확인
        response = send_file(output_pdf, as_attachment=True, mimetype='application/pdf')
        response.headers["Content-Length"] = file_size  # 크기 지정

        print(f"✅ PDF 응답 반환 성공: {output_pdf}", flush=True)
        return response

        #return send_file(output_pdf, as_attachment=True, mimetype='application/pdf')

    # PPTX 파일 전송
    return send_file(output_pptx, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')


def create_first_slide(prs, ceph, id_photo_path, df_raw = None):   # 2️⃣ Ceph 데이터 정리 및 딕셔너리 생성
    
      
      

    # 🔹 키 변형을 매핑하는 딕셔너리 (예: "PSA" ↔ "psa" ↔ "Psa")
    alias_map = {        
        "A - N /Ppn": "A point-N-perp",
        "FA`B`" : "FA'B'",
        "Ramus ht" : "Ramus height",
        "Y-Axis" : "Y-axis",
        "N-S-B" : "N-S-BaA",
        "- AB<LOP" : "AB<LOP",        
        "Naperp-A" : "A point-N-perp",
        "Y-angle" : "Y-axis",
        "Y-axis angle" : "Y-axis",
        "Na-S-BaA" : "N-S-BaA",
        "L.Lip E-line" : "E-line",
        "Overbite" : "Incisor Overbite",
        "Overjet" : "Incisor Overjet",
        "APDL" : "2APDL",

    }
    print("📌 Alias 매핑:", alias_map)

    # 📌 ceph 딕셔너리를 alias_map을 적용하여 변형
    ceph_standardized = {alias_map.get(k, k): v for k, v in ceph.items()}
    ceph = ceph_standardized.copy()  # 원본 보호를 위해 복사본 사용
    # 딕셔너리 값을 변수처럼 globals()에 추가

    print("📌 Ceph 데이터 (표준화 적용):", ceph_standardized)  

    

    # 3️⃣ PPT 불러오기
    
    temp_slide = prs.slides[0]  # 첫 번째 슬라이드 선택
    shape_s = temp_slide.shapes  # 슬라이드 내 모든 객체 가져오기

    # 4️⃣ 테이블 선택 (shape_s[7]에 테이블이 있다고 가정)
    table = shape_s[7].table  

   # 5️⃣ 첫 번째 열과 비교하여 일치하는 경우 두 번째 열 업데이트
    for i in range(0, len(table.rows)):  # 첫 번째 행(헤더 제외)
        key = table.cell(i, 0).text.strip() # 첫 번째 열 (계측 지표)
        
        # 🔹 alias_map에서 변형된 키를 찾음
        standardized_key = alias_map.get(key, key)
        print("🔑 표준화된 키:", standardized_key)

        # ✅ ceph_standardized에 존재하면 해당 값 입력, 없으면 "자료없음" 입력
        table.cell(i, 1).text = str(ceph.get(standardized_key, "자료없음"))        
        
        # 텍스트 스타일 적용
        TextFrame(table.cell(i, 1), font_size=Pt(7), font_bold=False, ft_color=True)  # 🔹 텍스트 스타일 적용

    print("테이블 업데이트 완료")

    

    try:
        # ✅ 기본값 설정 (오류 발생 시 사용)
        DEFAULT_VALUES = {
            'AB<LOP': 0, 'APDI': 81, 'PMA': 27.5, 'MBL': 0, 'ACBL': 0,
            'UGA': 50, 'PCBA': 64, 'FHR': 60, 'LGA': 75, 'ACBA': 7,
            'FMA': 0, 'FABA': 80, 'ODI': 0
        }

        # ✅ ceph 값이 없으면 기본값 사용
        def get_ceph_value(key):
            return ceph.get(key, DEFAULT_VALUES.get(key, 0))
        
        print("📌 Ceph 데이터:", ceph)
        

        # # ✅ 값 계산
        # cosvalue = math.cos(math.radians(get_ceph_value('AB<LOP')))
        # a = 3.5 / 4.4 * cosvalue
        # pmaval = get_ceph_value('PMA')
        # apdival = get_ceph_value('APDI')

        # if apdival >= 81:
        #     IAPDI = 95 - 0.5 * pmaval if pmaval < 27.5 else 81
        # else:
        #     IAPDI = 81 - a * (pmaval - 27.5)

        #IAPDI = round(IAPDI, 2)
        IAPDI = ceph.get('IAPDI', 0)
        print("IAPDI:",IAPDI, flush=True, file=sys.stderr)        

        # HGI = round(0.2 * ((get_ceph_value('MBL') - get_ceph_value('ACBL')) * 2 +
        #                     (get_ceph_value('UGA') - 50) +
        #                     0.5 * (get_ceph_value('PCBA') - 64)), 2)
        HGI = ceph.get('HGI', 0)

        # VGI = round(0.2 * ((get_ceph_value('FHR') - 60) * 2 -
        #                     (get_ceph_value('LGA') - 75) +
        #                     0.5 * (get_ceph_value('ACBA') - 7)), 2)
        VGI = ceph.get('VGI', 0)

        # APDL = round(0.4 * (get_ceph_value('APDI') - IAPDI), 2)
        APDL = (ceph.get('2APDL', 0))/2

        # IODI = round(((80 - 0.3 * get_ceph_value('PMA') -
        #             (0.776 - 0.008 * get_ceph_value('FMA')) *
        #             (get_ceph_value('FABA') - 80))), 2)
        IODI = ceph.get('IODI', 0)

        # VDL = round(0.4849 * (get_ceph_value('ODI') - IODI), 2)
        VDL = ceph.get('VDL', 0)

        # CFD = round(get_ceph_value('APDI') + get_ceph_value('ODI') - IAPDI - IODI, 2)
        CFD = ceph.get('CFD', 0)

        # ✅ 고정 변수 설정
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

        # ✅ 슬라이드 업데이트
        for k, v in fixed_var_dict.items():
            shape_s[k].text = v
            TextFrame(shape_s[k], font_size=Pt(13), font_bold=True, ft_color=False)

    except Exception as e:
        print("🚨 오류 발생: 코드 실행을 건너뜁니다.", flush=True)
        print(traceback.format_exc(), flush=True)

    
    # ✅ 기본값 설정
    DEFAULT_NAME = "순응교합"
    DEFAULT_AGE = "20"
    DEFAULT_BIRTH = (datetime.today() - timedelta(days=20*365)).strftime("%Y-%m-%d")  # 오늘 날짜에서 20년 전
    DEFAULT_GENDER = random.choice(["Male", "Female"])  # Male 또는 Female 중 랜덤 선택

    # ✅ df_raw가 None이 아닐 경우, 기존 데이터 사용
    if df_raw is not None:
        try:
            name = df_raw.iloc[3, 1] if not pd.isna(df_raw.iloc[3, 1]) else DEFAULT_NAME
            age = df_raw.iloc[3, 3] if not pd.isna(df_raw.iloc[3, 3]) else DEFAULT_AGE
            birth = df_raw.iloc[2, 3] if not pd.isna(df_raw.iloc[2, 3]) else DEFAULT_BIRTH
            gender = f'({df_raw.iloc[4, 1][0]})' if not pd.isna(df_raw.iloc[4, 1]) else DEFAULT_GENDER
        except Exception as e:
            print(f"🚨 데이터 추출 중 오류 발생: {e}")
            name, age, birth, gender = DEFAULT_NAME, DEFAULT_AGE, DEFAULT_BIRTH, DEFAULT_GENDER
    else:
        # ✅ df_raw가 None이면 기본값 사용
        name, age, birth, gender = DEFAULT_NAME, DEFAULT_AGE, DEFAULT_BIRTH, DEFAULT_GENDER

    # ✅ 최종 값 출력 (디버깅 용도)
    print(f"📌 이름: {name}, 나이: {age}, 생년월일: {birth}, 성별: {gender}")

    

    try:
        # ✅ 기본값 설정 (오류 발생 시 사용)
        DEFAULT_VALUES = {
            'FA`B`': 80, 'FABA': 80, 'Overbite': 0, 'APDL': 0
        }

        # ✅ ceph 값이 없으면 기본값 사용
        def get_ceph_value(key):
            return ceph.get(key, DEFAULT_VALUES.get(key, 0))

        # ✅ Soft, Bony, Denture Profile 계산
        try:
            soft_profile = 'S3' if get_ceph_value('FA`B`') >= 83 else 'S1' if get_ceph_value('FA`B`') >= 79 else 'S2'
            bony_profile = 'B3' if get_ceph_value('FABA') >= 83 else 'B1' if get_ceph_value('FABA') >= 79 else 'B2'
            denture_profile = 'D3' if 2 * APDL >= 2 else 'D1' if -1 <= 2 * APDL < 2 else 'D2'
        except Exception:
            soft_profile, bony_profile, denture_profile = "S2", "B2", "D2"

        # ✅ Normal / Deep / Open Bite 판별
        try:
            overbite_val = get_ceph_value('Overbite')
            if overbite_val > 3:
                nbt = 'dbt'
            elif -2 < overbite_val <= 3:
                nbt = 'nbt'
            else:
                nbt = 'obt'
        except Exception:
            nbt = "nbt"  # 기본값

        # ✅ Skeletal NBT 판별
        try:
            if VDL > 1:
                skeletal_nbt = 'dbt'
            elif -4 < VDL <= 1:
                skeletal_nbt = 'nbt'
            else:
                skeletal_nbt = 'obt'
        except Exception:
            skeletal_nbt = "nbt"  # 기본값

        # ✅ 텍스트 업데이트 (오류 발생 시 건너뜀)
        try:
            shape_s[4].text = f"{gender} {name} {age} {birth}\n {soft_profile}.{bony_profile}.{denture_profile}.C1-{nbt}({skeletal_nbt})-RM(Rt)-Fx:Ex-Fx/1-Type IV"
            TextFrame(shape_s[4])
        except (KeyError, IndexError):
            print(f"🚨 shape_s[4]에서 오류 발생: 텍스트 업데이트 건너뜀.", flush=True)

        # ✅ 이미지 처리 (오류 발생 시 건너뜀)
        try:
            with Image.open(id_photo_path) as img:
                width, height = img.size
                wpercent = 1.6 / float(width)
                new_height = round(float(height) * wpercent, 1)

                left = Inches(2.7)
                top = Inches(0.55)
                width = Inches(1.6)
                height = Inches(new_height)

                temp_slide.shapes.add_picture(id_photo_path, left, top, width, height)
        except Exception:
            print(f"🚨 ID 사진을 추가하는 중 오류 발생: {id_photo_path}를 찾을 수 없음.", flush=True)

        # ✅ HGI, VGI 값을 반환
        print(f"HGI: {HGI}, VGI: {VGI}")
        print("첫 번째 슬라이드 완료")
        return HGI, VGI

    except Exception as e:
        print("🚨 전체 코드 실행 중 오류 발생! 이 블록을 건너뜁니다.", flush=True)
        print(traceback.format_exc(), flush=True)
        return None, None  # 오류 발생 시 기본값 반환
    
def create_second_slide(prs, HGI, VGI, default_img):
     
     """
    psa 이미지를 2번째 슬라이드에 추가하는 함수.
    만약 업로드된 Pano 이미지가 없거나 손상되었을 경우, 기본 이미지 사용.

    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 파일 경로
    """
     # Pano 이미지 업로드 확인
     psa_file = request.files.get('psa')  # Flask에서 request로 직접 가져옴

     if psa_file and psa_file.filename:
        # 파일 저장 후 경로 설정
        psa_path = save_uploaded_file(psa_file, 'psa.jpg')

        # 파일 유효성 검사 (파일이 존재하고 크기가 0보다 커야 함)
        if not os.path.exists(psa_path) or os.path.getsize(psa_path) == 0:
            print(f"🚨 PSA 이미지가 없거나 손상됨: {psa_path}, 기본 이미지 사용")
            psa_path = default_img  # 기본 이미지로 변경
        else:
            try:
                # 이미지 유효성 검사
                with Image.open(psa_path) as img:
                    img.verify()
                print(f"✅ 유효한 PSA 이미지 확인: {psa_path}")
            except Exception as e:
                print(f"🚨 유효하지 않은 PSA 이미지 파일: {psa_path}, 기본 이미지 사용")
                psa_path = default_img  # 기본 이미지로 변경
     else:
        print(f"🚨 PSA 이미지가 업로드되지 않음, 기본 이미지 사용")
        psa_path = default_img  # 기본 이미지로 변경

    

     # 2번째 슬라이드 가져오기
     temp_slide_1 = prs.slides[1]  # 슬라이드 인덱스는 0부터 시작하므로 5번째는 인덱스 4
     shape_s_1 = temp_slide_1.shapes

     # 이미지 열기
     img_psa = Image.open(psa_path)

     # 슬라이드 크기 (인치 단위)
     slide_width = 10
     slide_height = 19.05 / 2.54  # cm를 inch로 변환

     # 이미지 비율에 따라 크기 조정
     if img_psa.size[1] / img_psa.size[0] < slide_height / slide_width:
        w = slide_width
        width = Inches(w)
        h = w * img_psa.size[1] / img_psa.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches((slide_height - h) / 2)  # 중앙 정렬
     else:
        h = slide_height
        height = Inches(h)
        w = h * img_psa.size[0] / img_psa.size[1]
        width = Inches(w)
        left = Inches((slide_width - w) / 2)  # 중앙 정렬
        top = Inches(0)

     # 이미지 추가
     shape_s_1.add_picture(psa_path, left, top, width, height)

     print("✅ 2번째 슬라이드에 PSA 이미지 추가 완료!")

     
     


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
        print(f"🖼 {idx+1}번째 이미지: {img_path}, 위치: ({left}, {top}), 크기: {img_width} x {img_height}")

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




def create_eighth_slide(prs, default_img):
    """
    자세사진 4장을 8번째 슬라이드에 가로로 나란히 정렬하여 추가하는 함수.
    각 사진의 너비는 2.25인치로 고정, 높이는 원본 비율 유지.
    슬라이드 왼쪽 여백 0.5인치, 오른쪽 여백 0.5인치.
    """    
    print("📂 8번째 슬라이드 생성 시작...", flush=True, file=sys.stderr)

    # 자세 사진 파일 경로 리스트 만들기
    photo_paths = []
    for idx in range(4):
        uploaded_file = request.files.get(f'posturePhoto{idx+1}')
        saved_path = save_uploaded_file(uploaded_file, f'posturePhoto_{idx+1}.jpg', default_img)
        photo_paths.append(saved_path)

    # 8번째 슬라이드 가져오기
    slide = prs.slides[7]
    shape_s_7 = slide.shapes

    # ✅ 기본 세팅
    fixed_width_inch = 2.25
    left_margin_inch = 0.5
    slide_height_inch = prs.slide_height.inches  # 보통 7.5 inch

    # ✅ 이미지 삽입
    for idx, img_path in enumerate(photo_paths):
        try:
            # 이미지 열어서 비율 계산
            with Image.open(img_path) as img:
                img_width_px, img_height_px = img.size
                aspect_ratio = img_height_px / img_width_px  # 세로 / 가로

                # 고정된 가로 길이 → 세로 계산
                img_width = Inches(fixed_width_inch)
                img_height = Inches(fixed_width_inch * aspect_ratio)

                # 위치 계산
                left = Inches(left_margin_inch + idx * fixed_width_inch)
                top = Inches((slide_height_inch - fixed_width_inch * aspect_ratio) / 2)

                shape_s_7.add_picture(img_path, left, top, width=img_width, height=img_height)
                print(f"✅ 이미지 {idx+1} 추가 완료: {img_path}", flush=True, file=sys.stderr)

        except Exception as e:
            print(f"❌ 이미지 추가 실패: {img_path} | 오류: {e}", flush=True, file=sys.stderr)

    print("✅ 8번째 슬라이드 이미지 배치 완료!", flush=True, file=sys.stderr)



def create_ninth_slide(prs, default_img):
    """
    자세사진 5~8번을 9번째 슬라이드에 가로로 나란히 정렬하여 추가하는 함수.
    각 사진의 너비는 2.25인치로 고정, 높이는 원본 비율 유지.
    슬라이드 왼쪽 여백 0.5인치, 오른쪽 여백 0.5인치.
    
    :param prs: 프레젠테이션 객체
    :param default_img: 기본 이미지 경로
    """
    
    print("📂 9번째 슬라이드 생성 시작...", flush=True, file=sys.stderr)

    # ✅ 자세 사진 5~8번 (index: 5,6,7,8 → 파일명: posturePhoto5 ~ posturePhoto8)
    photo_paths = []
    for idx in range(5, 9):  # 5,6,7,8
        uploaded_file = request.files.get(f'posturePhoto{idx}')
        saved_path = save_uploaded_file(uploaded_file, f'posturePhoto_{idx}.jpg', default_img)
        photo_paths.append(saved_path)

    # ✅ 9번째 슬라이드 가져오기 (슬라이드는 0-based index → 인덱스 8)
    slide = prs.slides[8]
    shape_s_8 = slide.shapes

    # ✅ 고정된 이미지 가로 너비 및 마진 설정
    fixed_width_inch = 2.25
    left_margin_inch = 0.5
    slide_height_inch = prs.slide_height.inches  # 보통 7.5인치

    # ✅ 이미지 삽입
    for i, img_path in enumerate(photo_paths):
        try:
            with Image.open(img_path) as img:
                img_width_px, img_height_px = img.size
                aspect_ratio = img_height_px / img_width_px

                # 고정된 가로 너비 → 세로는 비율로 계산
                img_width = Inches(fixed_width_inch)
                img_height = Inches(fixed_width_inch * aspect_ratio)

                # 위치 계산 (가로 정렬, 세로 중앙)
                left = Inches(left_margin_inch + i * fixed_width_inch)
                top = Inches((slide_height_inch - (fixed_width_inch * aspect_ratio)) / 2)

                shape_s_8.add_picture(img_path, left, top, width=img_width, height=img_height)
                print(f"✅ 이미지 {i+5} 추가 완료: {img_path}", flush=True, file=sys.stderr)

        except Exception as e:
            print(f"❌ 이미지 추가 실패: {img_path} | 오류: {e}", flush=True, file=sys.stderr)

    print("✅ 9번째 슬라이드 이미지 배치 완료!", flush=True, file=sys.stderr)

def create_tenth_slide(prs, pso_path):
    """ 10번째 슬라이드에 PSO 이미지를 추가하는 함수 """

    # 10번째 슬라이드 가져오기
    temp_slide_9 = prs.slides[9]  # 인덱스 9 = 10번째 슬라이드
    shape_s_9 = temp_slide_9.shapes

    # 이미지 열기
    img_pso = Image.open(pso_path)

    # 슬라이드 크기 (인치 단위)
    slide_width = 10
    slide_height = 19.05 / 2.54  # cm → inch 변환

    # 이미지 비율에 따라 크기 조정
    if img_pso.size[1] / img_pso.size[0] < slide_height / slide_width:
        w = slide_width
        width = Inches(w)
        h = w * img_pso.size[1] / img_pso.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches((slide_height - h) / 2)
    else:
        h = slide_height
        height = Inches(h)
        w = h * img_pso.size[0] / img_pso.size[1]
        width = Inches(w)
        left = Inches((slide_width - w) / 2)
        top = Inches(0)

    # 이미지 추가
    shape_s_9.add_picture(pso_path, left, top, width, height)

    print("✅ 10번째 슬라이드에 PSO 이미지 추가 완료!")

def create_eleventh_slide(prs, frontal_ax_path):
    """ 11번째 슬라이드에 Frontal Ax 이미지를 추가하는 함수 """

    # 11번째 슬라이드 가져오기
    temp_slide_10 = prs.slides[10]  # 인덱스 10 = 11번째 슬라이드
    shape_s_10 = temp_slide_10.shapes

    # 이미지 열기
    img_frontal_ax = Image.open(frontal_ax_path)

    # 슬라이드 크기 (인치 단위)
    slide_width = 10
    slide_height = 19.05 / 2.54  # cm → inch 변환

    # 이미지 비율에 따라 크기 조정
    if img_frontal_ax.size[1] / img_frontal_ax.size[0] < slide_height / slide_width:
        w = slide_width
        width = Inches(w)
        h = w * img_frontal_ax.size[1] / img_frontal_ax.size[0]
        height = Inches(h)
        left = Inches(0)
        top = Inches((slide_height - h) / 2)
    else:
        h = slide_height
        height = Inches(h)
        w = h * img_frontal_ax.size[0] / img_frontal_ax.size[1]
        width = Inches(w)
        left = Inches((slide_width - w) / 2)
        top = Inches(0)

    # 이미지 추가
    shape_s_10.add_picture(frontal_ax_path, left, top, width, height)

    print("✅ 11번째 슬라이드에 Frontal Ax 이미지 추가 완료!")
