import comtypes.client
import os

def convert_ppt_to_pdf(ppt_path, pdf_path):
    """
    PPT 파일을 PDF로 변환하는 함수
    (Windows 환경에서 MS PowerPoint와 comtypes 설치 필요)

    :param ppt_path: 변환할 PPT 파일의 경로
    :param pdf_path: 출력될 PDF 파일 경로
    """
    # PowerPoint 애플리케이션 객체를 생성 (COM 객체)
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1  # 파워포인트를 실제로 표시할지 여부 (1이면 표시)

    # PPT 파일 열기 (WithWindow=False로 하면 백그라운드에서 열림)
    presentation = powerpoint.Presentations.Open(ppt_path, WithWindow=False)

    # 파일 형식 32 -> PDF로 저장
    # (Office VBA에서 상수 msoSaveAsPDF가 32에 해당함)
    presentation.SaveAs(pdf_path, 32)

    # 열어둔 프레젠테이션 닫기
    presentation.Close()
    # PowerPoint 종료
    powerpoint.Quit()

    # PDF가 정상적으로 생성되었는지 확인
    if os.path.exists(pdf_path):
        print(f"PDF 변환 완료: {pdf_path}")
    else:
        print("PDF 변환 실패 혹은 파일 경로 확인 필요")

# 사용 예시
if __name__ == "__main__":
    # PPT 파일 경로
    input_ppt = r"D:\pythonProject\koco_final\koco_project\backend\output_ppt.pptx"
    # PDF 파일로 저장할 경로
    output_pdf = r"D:\pythonProject\koco_final\koco_project\backend\output_pdf.pdf"

    convert_ppt_to_pdf(input_ppt, output_pdf)
