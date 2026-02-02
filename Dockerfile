# 1️⃣ Debian Bullseye 기반 이미지 사용 (LibreOffice 7.x 안정 버전)
FROM debian:bullseye-slim

# 2️⃣ 작업 디렉토리 설정
WORKDIR /app

# 3️⃣ apt 재시도 설정 + Python 및 필수 시스템 패키지 설치
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries \
    && apt-get update \
    && apt-get install -y --no-install-recommends --fix-missing \
    python3 python3-pip python3-dev python3-tk \
    libreoffice-impress libreoffice-writer fonts-nanum \
    libgl1 libsm6 libxext6 libxrender1 libopenblas-dev \
    && fc-cache -fv \
    && mkdir -p /tmp/libreoffice_profile \
    && chmod 777 /tmp/libreoffice_profile \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

# 4️⃣ requirements.txt 복사 및 pip 업그레이드
COPY requirements.txt . 
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5️⃣ 애플리케이션 코드 복사
COPY . .

# 6️⃣ 환경 변수 설정 (Flask 실행을 위한 설정)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HOME=/tmp
ENV SAL_USE_VCLPLUGIN=svp

# 7️⃣ Flask 서버 실행
CMD ["python", "app.py"]

# 리눅스 기반으로 도커이미지 빌드
# docker build --no-cache --platform linux/amd64 -t oksusu2020/koco_final:20250209 .


# 9500 포트로 컨테이너 실행
# docker run -d -p 9500:9500 --name koco_container oksusu2020/koco_final:20250208


