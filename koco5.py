import pandas as pd
import numpy as np
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches
import cv2
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
import win32com.client as win32




# 엑셀파일읽어오기
df_raw = pd.read_excel('opda_sample.xlsx',sheet_name = 0)

# 값만 있는 파일
df = df_raw.iloc[7:]

# ppt 양식 불러오기
prs = Presentation('koco_frame.pptx')

# 이미지 이름 써주기
id_photo = '측모.jpg'
psa_name = 'psa_sample2.png'
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

# 측모엑스레이 저장하기
lateral_ceph_image = "lateral_ceph.jpg"


# 양식 입력 함수
def TextFrame(ss,font_name = '맑은 고딕', font_size = Pt(15), font_bold = True, ft_color = True, font_color = RGBColor(68, 84, 116)):
    for line in range(len(ss.text_frame.paragraphs)):
        ss.text_frame.paragraphs[line].font.name = font_name
        ss.text_frame.paragraphs[line].font.size = font_size
        ss.text_frame.paragraphs[line].font.bold = font_bold
        ss.text_frame.paragraphs[line].alignment = PP_ALIGN.CENTER
        if ft_color == True:
            ss.text_frame.paragraphs[line].font.color.rgb = font_color
    return ss

### 슬라이드 양식복사
temp_slide = prs.slides[0]
shape_s = temp_slide.shapes




#ppt table에 ceph 데이터 넣기
for i in range(df.shape[0]):
    shape_s[7].table.cell(row_idx=i,col_idx =1).text = str(df.iloc[i,3])
    TextFrame(shape_s[7].table.cell(row_idx=i,col_idx =1),font_size=Pt(7),font_bold=False,ft_color=False)

#ceph 수치의 공백 없애기(특히 오른쪽)
df['Unnamed: 0'] = df['Unnamed: 0'].str.rstrip()

# ceph data를 dict로 바꾸기 (변수 활용하기 위해서)
ceph = {}
for key, value in zip(df['Unnamed: 0'],df['Unnamed: 3']):
    ceph[key] = value

# ceph 이름 찾을 때  ceph.keys()

## 수식만들기

import math


#### IAPDI
cosvalue = math.cos(math.radians(ceph['- AB<LOP']))
a = 3.5/4.4 * cosvalue
if ceph['APDI'] >= 81:
    if ceph['PMA'] < 27.5 :
        IAPDI = 95 - 0.5*ceph['PMA']
    elif ceph['PMA'] > 27.5 :
        IAPDI = 81

elif ceph['APDI'] < 81:
    IAPDI = 81-a*(ceph['PMA']-27.5)

def Round_ceph(a):
    return round(a,2)

IAPDI = Round_ceph(IAPDI)
#IAPDI = round(IAPDI,1)

#### HGI,VGI, 2APDL, IODI, VDL, CFD
#round_list = [HGI, VGI, APDL, IODI, VDL, CFD]
HGI = 0.2*((ceph['MBL']-ceph['ACBL'])*2+(ceph['UGA']-50)+0.5*(ceph['PCBA']-64))
VGI = 0.2*((ceph['FHR']-60)*2-(ceph['LGA']-75)+0.5*(ceph['ACBA']-7))
APDL = 0.4*(ceph['APDI'] - IAPDI)
IODI = ((80-0.3*ceph['PMA']-(0.776-0.008*ceph['FMA'])*(ceph['FABA']-80)))
VDL = 0.4849*(ceph['ODI']-IODI)
CFD = ceph['APDI'] + ceph['ODI'] - IAPDI - IODI


HGI = round(HGI,2)
VGI = round(VGI,2)
APDL = round(APDL,2)
IODI = round(IODI,2)
VDL = round(VDL,2)
CFD = round(CFD,2)
#### 

#### 변수 변경하는 란!!!
# 고정변수
fixed_var_dict = {8 : 'C/C & Main problem',
9 : 'MPH:',
11 : f'HGI:{HGI}',
13 : f'VGI:{VGI}',

17 : f'IAPDI:{IAPDI}',
19 : f'2APDL:{APDL*2}',
20 : f'IODI:{IODI}',
22 : f'VDL:{VDL}',

24 : 'CEPH RESULT',

25 : f'CFD:{CFD}',
26 : 'Extraction:'}


# 입력 및 폰트 양식 설정
for k, v in fixed_var_dict.items():
    shape_s[k].text = v
    TextFrame(shape_s[k],font_size=Pt(13),font_bold=True,ft_color = False)

# 제목 인적사항
name = df_raw.iloc[3,1]
age = df_raw.iloc[3,3]
birth = df_raw.iloc[2,3]
gender = f'({df_raw.iloc[4,1][0]})'

#soft_profile 값 정하기
if ceph['FA`B`'] >= 83:
    soft_profile = 'S3'
elif ceph['FA`B`'] >= 79:
    soft_profile = 'S1'
else : soft_profile = 'S2'

#bony_profile 값 정하기
if ceph['FABA'] >= 83:
    bony_profile = 'B3'
elif ceph['FABA'] >= 79:
    bony_profile = 'B1'
else : bony_profile = 'B2'

#denture_profile
if 2*APDL >=2:
    denture_profile = 'D3'
elif -1 <= 2*APDL <2:
    denture_profile = 'D1'
else : denture_profile = 'D2'

#nbt
if ceph['Overbite'] > 3:
    nbt = 'dbt'
elif -2 < ceph['Overbite'] <= 3 :
    nbt = 'nbt'
else : nbt = 'obt'

#skeletal_nbt
if VDL >  1:
    skeletal_nbt = 'dbt'
elif -4 < VDL <= 1:
    skeletal_nbt = 'nbt'
else : skeltal_nbt = 'obt'


# 제목 입력
shape_s[4].text = f'{" ".join([gender,name,age,birth])} \n {soft_profile}.{bony_profile}.{denture_profile}.C1-{nbt}({skeletal_nbt})-RM(Rt)-Fx:Ex-Fx/1-Type IV'

# 양식설정
TextFrame(shape_s[4])

from PIL import Image

######### 이미지 리사이즈
# 이미지 불러오기
img = Image.open(id_photo)
width, height = img.size
wpercent = 1.6/float(width) 
new_height =  round(float(height)*float(wpercent),1)
# img.save(id_photo)

######### 사진 집어넣기
left = Inches(2.7)
top = Inches(0.55)
width = Inches(1.6)
height = Inches(new_height)

shape_s.add_picture(id_photo,left,top,width,height)

### 화살표 집어넣기
# img_triangle = cv2.imread(triangle, cv2.IMREAD_COLOR)
# s_x = 1150
# s_y = 200
# color = (0,0,255)
# pt1 = (s_x, s_y)
# pt2 = (int((s_x +(HGI*100)/4)), int((s_y - (VGI*100)/4)))
# img_arrow = cv2.arrowedLine(img_triangle, pt1,pt2, color= (0,0,255))

# 결과이미지 저장하기

# exp = triangle.strip().split('.')[0]
# print(exp)
# cv2.imwrite(f"{exp}_result.png",img_triangle)

# shape = temp_slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(1), Inches(1), Inches(2), Inches(1))
# shape.rotation = -45
# # set the fill color of the arrow shape
# fill = shape.fill
# fill.solid()
# fill.fore_color.rgb = RGBColor(255, 255, 255) # white color

# def calculate_angle(x1, y1, x2, y2):
#     x_diff = x2 - x1
#     y_diff = y2 - y1
#     angle_in_radians = math.atan2(y_diff, x_diff)
#     angle_in_degrees = math.degrees(angle_in_radians)
#     return angle_in_degrees

# calculate_angle(0,0,4,4)

# print(1000)



def draw_arrow(slide_name, find_shape_name, x, y):
    slide = slide_name

    for i, s in enumerate(slide.shapes):
        if s.name == find_shape_name:
            shape = slide.shapes[i]
            break
    
    # 입력위치
    x_loc = shape.left + shape.width
    y_loc = shape.top + shape.height 


    # HGI와 VDL 좌표의 각도 구하기
    angle_rad = math.atan2(y, x)
    angle_deg = math.degrees(angle_rad)


    # 0.2인치 짜리 화살표 입력
    width = Inches(float(HGI/4))
    height = Inches(float(VGI/4))
    
    shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x_loc, y_loc- height, width, height)
    shape.rotation = int(angle_deg)

# 도형 이름을 이용해 위치 찾기
find_shape_name = '삼각형'

draw_arrow(temp_slide, find_shape_name, x=HGI, y= VGI )



####2번째 슬라이드 만들기(PSA)

#psa 를 위해서 이미지 객체 만들기
psa_image = cv2.imread(f"{psa_name}", cv2.IMREAD_COLOR)
psa_height, psa_width, psa_channels = psa_image.shape
print(psa_width)
print(psa_image.shape)

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
image = cv2.imread(f"{psa_name}", cv2.IMREAD_COLOR)

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
psa_image = cv2.imread(f"{psa_name}", cv2.IMREAD_COLOR)
#lateral_ceph = 'lateral_ceph.jpg'


# img_lateral_ceph = cv2.imread(lateral_ceph, cv2.IMREAD_COLOR)
s_x = 1150
s_y = 200
color = (0,0,255)
pt1 = (s_x, s_y)
pt2 = (int((s_x +(HGI*100)/4)), int((s_y - (VGI*100)/4)))
img_arrow = cv2.arrowedLine(src, pt1,pt2, color= (0,0,255))


# 결과이미지 저장하기

exp = psa_name.strip().split('.')[0]
print(exp)
cv2.imwrite(f"{exp}_result.png",src)

# 2번째 슬라이드 만들기

temp_slide_1 = prs.slides[1] #2번째 슬라이드를 KOCO 프레임에서가지고 오기
shape_s_1= temp_slide_1.shapes
# for idx, value in enumerate(shape_s_1):
#     #shape_s_2[idx].text = f'{idx},{value.name}'
#     print(idx, value.name)
    
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

### 3번째 슬라이드 양식복사
temp_slide_2 = prs.slides[2]
shape_s_2= temp_slide_2.shapes
# for idx, value in enumerate(shape_s_1):
#         shape_s_1[idx].text = f'{idx},{value.name}'
#         print(idx, value.name)


#정면편하게사진
img_1 = Image.open(eofrontal_rest)
h = (19.05/2.54)/2
height = Inches(h)
w = h*(img_1.size[0]/img_1.size[1])
width = Inches(w)
left = Inches((10-4*w)/2)
top = Inches(0)
shape_s_2.add_picture('정면편하게.jpg',left, top, width, height)

#정면똑바로사진
img_2 = Image.open(eofrontal)
left = Inches((10-4*w)/2 + w)
shape_s_2.add_picture('정면똑바로.jpg',left, top, width, height)

#측모45사진
img_3 = Image.open(eofrontal45)
left = Inches((10-4*w)/2 + 2*w)
shape_s_2.add_picture('측모45.jpg',left, top, width, height)

#측모사진
img_4 = Image.open(eolateral)
left = Inches((10-4*w)/2 + 3*w)
shape_s_2.add_picture('측모.jpg',left, top, width, height)

#정면편하게스마일
img_5 = Image.open(eofrontal_smile)
left = Inches((10-4*w)/2)
top = Inches(h)
shape_s_2.add_picture('정면편하게스마일.jpg',left, top, width, height)

#정면똑바로스마일
img_6 = Image.open(eofrontal_smile)
left = Inches((10-4*w)/2+w)
top = Inches(h)
shape_s_2.add_picture('정면똑바로스마일.jpg',left, top, width, height)

#측모45스마일
img_7 = Image.open(eofrontal_smile)
left = Inches((10-4*w)/2+2*w)
top = Inches(h)
shape_s_2.add_picture('측모45스마일.jpg',left, top, width, height)

#측모스마일
img_8 = Image.open(eofrontal_smile)
left = Inches((10-4*w)/2+3*w)
top = Inches(h)
shape_s_2.add_picture('측모스마일.jpg',left, top, width, height)

### 4번째 슬라이드 양식복사
temp_slide_3 = prs.slides[3]
shape_s_3= temp_slide_3.shapes
# for idx, value in enumerate(shape_s_1):
#         shape_s_1[idx].text = f'{idx},{value.name}'
#         print(idx, value.name)



#상악사진
img_upper = Image.open(ioupper)
h = 2.2
height = Inches(h)
w = h*img_upper.size[0]/img_upper.size[1]
width = Inches(w)
left = Inches((10-2*w)/2)
top = Inches(1)
shape_s_3.add_picture('상악사진.jpg',left, top, width, height)

#하악사진
img_lower = Image.open(iolower)
left = Inches((10-2*w)/2 + w)
shape_s_3.add_picture('하악사진.jpg',left, top, width, height)

#교합좌측
img_left = Image.open(ioleft)
left = Inches((10-3*w)/2)
top = Inches(1+h)
shape_s_3.add_picture('교합좌측.jpg',left, top, width, height)

#교합정면
img_frontal = Image.open(iofrontal)
left = Inches((10-3*w)/2 + w)
shape_s_3.add_picture('교합정면.jpg',left, top, width, height)

#교합우측
img_right = Image.open(ioright)
left = Inches((10-3*w)/2 + 2*w)
shape_s_3.add_picture('교합우측.jpg',left, top, width, height)





### 5번째 슬라이드 양식복사(lateral_ceph 엑스레이)
temp_slide_4 = prs.slides[4]
shape_s_4= temp_slide_4.shapes

img_lateral_ceph = Image.open(lateral_ceph_image)
w = 10
width = Inches(w)
h = (img_lateral_ceph.size[1]/img_lateral_ceph.size[0])*10
height = Inches(h)
left = Inches(0)
top = Inches(((19.05/2.54)-h)/2)
shape_s_4.add_picture(lateral_ceph_image ,left, top, width, height)

prs.save('koco_test.pptx')

