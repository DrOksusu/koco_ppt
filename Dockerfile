# 1️⃣ Python 3.9 기반 이미지 사용
FROM python:3.9

# 2️⃣ 작업 디렉토리 설정
WORKDIR /app

# 3️⃣ 필수 시스템 패키지 설치 (의존성 문제 해결)
RUN apt-get update && apt-get upgrade -y 

RUN apt-get install -y --no-install-recommends \
    libreoffice-common \
    libreoffice \    
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libglib2.0-dev \
    libsm6 \
    libxext6 \
    libxrender1 \
    libatlas-base-dev 

RUN rm -rf /var/lib/apt/lists/*

# 4️⃣ requirements.txt 복사 및 pip 업그레이드
COPY requirements.txt . 
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5️⃣ 애플리케이션 코드 복사
COPY . .

# 6️⃣ 환경 변수 설정 (Flask 실행을 위한 설정)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production  

# 7️⃣ Flask 서버 실행
CMD ["python", "app.py"]

# 리눅스 기반으로 도커이미지 빌드
# docker build --no-cache --platform linux/amd64 -t oksusu2020/koco_final:20250209 .


# 9500 포트로 컨테이너 실행
# docker run -d -p 9500:9500 --name koco_container oksusu2020/koco_final:20250208


