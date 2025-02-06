# 1️⃣ Python 3.9 기반 이미지 사용
FROM python:3.9

# 2️⃣ 작업 디렉토리 설정
WORKDIR /app

# 3️⃣ 패키지 목록 업데이트 및 LibreOffice 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libreoffice && \
    rm -rf /var/lib/apt/lists/*

# 4️⃣ 필요한 파이썬 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ 애플리케이션 코드 복사
COPY . .

# 6️⃣ Flask 서버 실행
CMD ["python", "app.py"]
