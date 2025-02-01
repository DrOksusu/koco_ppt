from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import math
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from PIL import Image
import os
import comtypes.client
from flask_cors import CORS
import pythoncom
from comtypes.client import CreateObject
import cv2
import numpy as np



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

def convert_ppt_to_pdf(input_ppt, output_pdf):
    """
    PowerPoint 파일을 PDF로 변환하는 함수
    :param input_ppt: 변환할 PPTX 파일의 절대 경로
    :param output_pdf: 변환된 PDF 파일이 저장될 절대 경로
    """
    pythoncom.CoInitialize()  # 🔥 COM 객체 초기화 (Flask 같은 멀티스레드 환경에서 필수)

    try:
        # PowerPoint 애플리케이션 객체 생성
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1  # 1 = 표시, 0 = 백그라운드 실행 가능

        # 절대 경로 변환 (PowerPoint가 상대 경로를 잘 인식하지 못할 수 있음)
        input_ppt = os.path.abspath(input_ppt)
        output_pdf = os.path.abspath(output_pdf)

        print(f"📂 변환 시작: {input_ppt} -> {output_pdf}")

        # PPT 파일 열기
        presentation = powerpoint.Presentations.Open(input_ppt, WithWindow=False)

        # PDF로 저장 (32: msoSaveAsPDF)
        presentation.SaveAs(output_pdf, 32)
        presentation.Close()

        # PowerPoint 종료
        powerpoint.Quit()

        # 변환 성공 여부 확인
        if os.path.exists(output_pdf):
            print(f"✅ PDF 변환 성공: {output_pdf}")
        else:
            raise FileNotFoundError(f"🚨 PDF 변환 실패: {output_pdf} 파일이 생성되지 않음")

    except Exception as e:
        print(f"❌ PDF 변환 중 오류 발생: {e}")
    finally:
        pythoncom.CoUninitialize()  # 🚀 COM 객체 해제

# 🔹 1️⃣ 프론트엔드 (HTML) 서빙
@app.route('/')
def home():
    return render_template('index1.html')  # templates/index.html 제공

# 파일 저장 디렉토리 지정
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 파일 저장 함수
def save_uploaded_file(uploaded_file, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(file_path)
    return file_path

def create_first_slide(prs, df, df_raw, id_photo_path):
    temp_slide = prs.slides[0]
    shape_s = temp_slide.shapes

    #ppt table에 ceph 데이터 넣기
    for i in range(df.shape[0]):
        shape_s[7].table.cell(row_idx=i,col_idx =1).text = str(df.iloc[i,3])
        TextFrame(shape_s[7].table.cell(row_idx=i,col_idx =1),font_size=Pt(7),font_bold=False,ft_color=False)

    # Ceph 데이터 정리
    df['Unnamed: 0'] = df['Unnamed: 0'].str.rstrip()
    ceph = {key: value for key, value in zip(df['Unnamed: 0'], df['Unnamed: 3'])}

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
    return HGI, VGI

def create_second_slide(prs, HGI, VGI, psa_name_path):
    # 두 번째 슬라이드 만들기
    temp_slide_1 = prs.slides[1] #2번째 슬라이드를 KOCO 프레임에서가지고 오기
    shape_s_1= temp_slide_1.shapes

    #psa 를 위해서 이미지 객체 만들기
    psa_image = cv2.imread(psa_name_path, cv2.IMREAD_COLOR)
    psa_height, psa_width, psa_channels = psa_image.shape
    print("psa_width:", psa_width)
    print("psa_image.shape:", psa_image.shape)

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

    # 두 좌표
    d = img_result.nonzero()[0][0]
    b = img_result.nonzero()[0][-1]
    print('2')
    c = img_result.nonzero()[1][0]
    a = img_result.nonzero()[1][-1]

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
    pt2 = (int((s_x +(HGI*100)/4)), int((s_y - (VGI*100)/4)))
    img_arrow = cv2.arrowedLine(src, pt1,pt2, color= (0,0,255))


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
        left = Inches((10-w)/2)
        top = Inches(0)
    shape_s_1.add_picture(f"{exp}_result.png",left, top, width, height)


# PPT 작성 엔드포인트
@app.route('/dash_board', methods=['POST'])
def create_ppt():
    try:
        # ㅍ스트 요청이 아닌 경우 405 에러 반환
        if request.method != 'POST':
            return jsonify({"error": "Only POST requests are allowed."}), 405
        
        # 요청 데이터 받기
        if 'photo4' not in request.files or 'excel_data' not in request.files:
            return jsonify({"error": "Both 'id_photo' and 'excel_data' files are required."}), 400
        
        
        triangle = '화살표.png'

        # 구외사진 저장하기
        eofrontal_rest = '정면편하게.jpg'
        eofrontal = '정면똑바로.jpg'
        eofrontal45 = '측모45.jpg'
        eolateral = '측모.jpg'
        eofrontal_smile = '정면편하게스마일.jpg'
        eofrontal_upright = '정면똑바로스마일.jpg'
        eofrontal45_smile = '측모45스마일.jpg'
        eolateral_smile = '측모스마일.jpg'

        # 구내사진 저장하기
        ioupper = '상악사진.jpg'
        iolower = '하악사진.jpg'
        iofrontal = '교합정면.jpg'
        ioright = '교합우측.jpg'
        ioleft = '교합좌측.jpg'

        # 파일 저장
        pano = request.files['pano']
        lateral_ceph_image = request.files['lateral_ceph']
        frontal_ceph_image = request.files['frontal_ceph']
        psa_name = request.files['psa']

        eofrontal_rest = request.files['photo1']
        eofrontal = request.files['photo2']
        eofrontal45 = request.files['photo3']
        id_photo = request.files['photo4']
        eofrontal_smile = request.files['photo5']
        eofrontal_upright = request.files['photo6']
        eofrontal45_smile = request.files['photo7']
        eolateral = request.files['photo8']

        ioupper = request.files['oralPhoto1']
        iolower = request.files['oralPhoto2']
        iofrontal = request.files['oralPhoto3']
        ioright = request.files['oralPhoto4']
        ioleft = request.files['oralPhoto5']



        excel_file = request.files['excel_data']
        file_type = request.form.get('file_type', 'pdf') #기본값은 pdf

        # 파일 저장

        pano_path = save_uploaded_file(pano, 'pano.jpg')
        lateral_ceph_image_path = save_uploaded_file(lateral_ceph_image, 'lateral_ceph_image.jpg')
        frontal_ceph_image_path = save_uploaded_file(frontal_ceph_image, 'frontal_ceph_image.jpg')
        psa_name_path = save_uploaded_file(psa_name, 'psa_name.jpg')
        eofrontal_rest_path = save_uploaded_file(eofrontal_rest, 'eofrontal_rest.jpg')
        eofrontal_path = save_uploaded_file(eofrontal, 'eofrontal.jpg')
        eofrontal45_path = save_uploaded_file(eofrontal45, 'eofrontal45.jpg')
        id_photo_path = save_uploaded_file(id_photo, 'id_photo.jpg')
        eofrontal_smile_path = save_uploaded_file(eofrontal_smile, 'eofrontal_smile.jpg')
        eofrontal_upright_path = save_uploaded_file(eofrontal_upright, 'eofrontal_upright.jpg')
        eofrontal45_smile_path = save_uploaded_file(eofrontal45_smile, 'eofrontal45_smile.jpg')
        eolateral_path = save_uploaded_file(eolateral, 'eolateral.jpg')
        ioupper_path = save_uploaded_file(ioupper, 'ioupper.jpg')
        iolower_path = save_uploaded_file(iolower, 'iolower.jpg')
        iofrontal_path = save_uploaded_file(iofrontal, 'iofrontal.jpg')
        ioright_path = save_uploaded_file(ioright, 'ioright.jpg')
        ioleft_path = save_uploaded_file(ioleft, 'ioleft.jpg')
        excel_file_path = save_uploaded_file(excel_file, 'excel_data.xlsx')      


        
        # 엑셀 데이터 로드
        df_raw = pd.read_excel(excel_file_path)
        df = df_raw.iloc[7:]

        # PPT 템플릿 로드
        # 현재 디렉터리에서 파일 경로를 생성
        ppt_template_path = os.path.join(os.getcwd(), 'koco_frame.pptx')

        # PPT 템플릿 로드
        prs = Presentation(ppt_template_path)
        
        # 첫 번째 슬라이드 만들기
        HGI, VGI = create_first_slide(prs, df, df_raw, id_photo_path)

        ####2번째 슬라이드 만들기(PSA)
        create_second_slide(prs, HGI, VGI, psa_name_path)

        

        # PPT 저장
        output_pptx = 'output_ppt.pptx'
        prs.save(output_pptx)

        
        # 임시 파일 삭제
        try:
            if os.path.exists(id_photo_path):
                os.remove(id_photo_path)
            if os.path.exists(excel_file_path):
                os.remove(excel_file_path)
        except PermissionError as e:
            print(f"PermissionError: {e}")

        if file_type == 'pdf':
            output_pdf = 'output_ppt.pdf'
            convert_ppt_to_pdf(output_pptx, output_pdf)  # PDF 변환 로직 (구현 필요)

            return send_file(output_pdf, as_attachment=True, mimetype='application/pdf')

        # PPTX 파일 전송
        return send_file(output_pptx, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')


    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
