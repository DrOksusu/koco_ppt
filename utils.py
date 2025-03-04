import os
import shutil
import subprocess
from flask import request
import sys
from config import UPLOAD_FOLDER
if sys.platform == "win32":
    import comtypes.client
    import pythoncom
    from comtypes.client import CreateObject




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
        print("🔄 COM 초기화 완료", flush=True)

        try:
            #  powerpoint Type Library 강제로드
            comtypes.client.GetModule("C:/Program Files/Microsoft Office/root/Office16/MSPPT.OLB")
            print("🔄 PowerPoint COM 인터페이스 로드 완료")           

            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            print("🔄 PowerPoint COM 객체 생성", flush=True)
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
            # 💡 올바른 순서: PowerPoint 종료 → COM 해제
            if 'powerpoint' in locals():  # 객체가 생성된 경우에만 종료
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