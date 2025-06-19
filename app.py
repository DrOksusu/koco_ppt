from flask import Flask, request, jsonify, send_file, render_template, url_for, redirect, session
from flask_cors import CORS
from ppt_generator import create_ppt
from green_line import draw_psa_line
import os
from config import UPLOAD_FOLDER, RESULT_FOLDER
from werkzeug.utils import secure_filename
import logging
from flask import request
import requests
import json


# 🔑 카카오 API 관련 상수들 (환경변수 또는 하드코딩된 기본값)
KAKAO_CLIENT_ID = os.environ.get('KAKAO_CLIENT_ID', 'ccb9d48d7702c55ca74794e105af647b') #naturem-clinic api
KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI', 'https://koco.me/kakao')
KAKAO_AUTH_URL = 'https://kauth.kakao.com/oauth/authorize'
KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
KAKAO_USER_URL = 'https://kapi.kakao.com/v2/user/me'
KAKAO_FRIENDS_URL = 'https://kapi.kakao.com/v1/api/talk/friends'
KAKAO_SEND_URL = 'https://kapi.kakao.com/v1/api/talk/friends/message/default/send'


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'koco')  # 세션에 사용할 비밀 키 설정



@app.route('/')
def home():
    user = session.get('user')  # 세션에서 사용자 정보 가져오기

    if user:
        # 로그인된 사용자라면 사용자 정보도 템플릿에 전달
        return render_template(
            'index1.html',
            user=user,
            login_url=url_for('login')
        )
    else:
        # 로그인되지 않은 경우는 로그인 URL만 전달
        return render_template(
            'index1.html',
            user=None,
            login_url=url_for('login')
        )

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/login')
def login():
    # 카카오 인증 URL로 리디렉트, scope에 친구 및 메시지 권한 포함
    kakao_auth_url = (
        f"{KAKAO_AUTH_URL}?response_type=code"
        f"&client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&scope=friends%20talk_message"
    )
    return redirect(kakao_auth_url)

# 🔸 카카오 인증 후 리디렉트되는 콜백 처리
@app.route('/kakao')
def oauth():    
    code = request.args.get('code')  # 인가 코드 가져오기
    if not code:
        return '인증 코드가 없습니다.', 400

    # 토큰 요청 payload 구성
    data = {
        'grant_type': 'authorization_code',
        'client_id': KAKAO_CLIENT_ID,
        'redirect_uri': KAKAO_REDIRECT_URI,
        'code': code
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # access_token 요청
    token_response = requests.post(KAKAO_TOKEN_URL, data=data, headers=headers)
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    if not access_token:
        # 토큰 요청 실패 시 에러 반환
        return f"토큰 요청 실패: {token_json}", 400

    # 사용자 정보 요청 (access_token을 Authorization 헤더로 사용)
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(KAKAO_USER_URL, headers=headers)
    user_json = user_response.json()

    # 세션에 사용자 정보와 토큰 저장
    session['user'] = user_json
    session['access_token'] = access_token

    # 홈으로 리디렉트
    return redirect(url_for('home'))


# 🔸 로그아웃
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('access_token', None)

    # 카카오 로그아웃도 같이 요청
    kakao_logout_url = (
        f"https://kauth.kakao.com/oauth/logout"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&logout_redirect_uri=https://koco.me"
    )
    return redirect(kakao_logout_url)



# 🔸 친구 목록 보기
@app.route('/friends')
def friends():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))  # 로그인 안 되어 있으면 로그인 페이지로

    access_token = session.get('access_token')
    if not access_token:
        return 'Access token이 없습니다. 다시 로그인 해주세요.', 401

    # 친구 목록 요청
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(KAKAO_FRIENDS_URL, headers=headers)

    if response.status_code != 200:
        return f"친구 목록 요청 실패: {response.text}", response.status_code

    friends_data = response.json()
    friends_list = friends_data.get('elements', [])  # 친구 목록

    # 템플릿에 친구 목록 전달
    return render_template('friends.html', friends=friends_list)


# 🔸 메시지 전송 요청 처리
@app.route('/send_message', methods=['POST'])
def send_message():
    access_token = session.get('access_token')
    if not access_token:
        error = 'Access token이 없습니다. 다시 로그인 해주세요.'
        return render_friends_with_error(error)

    # 선택된 친구 UUID 배열
    uuids = request.form.getlist('uuids')
    message = request.form.get('message', '안녕하세요!')

    if not uuids:
        error = '최소 한 명의 친구를 선택해야 합니다.'
        return render_friends_with_error(error)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # 메시지 템플릿 구성
    payload = {
        'receiver_uuids': json.dumps(uuids),  # 친구 UUID 목록
        'template_object': json.dumps({
            'object_type': 'text',
            'text': message,
            'link': {
                'web_url': 'https://www.kakao.com',
                'mobile_web_url': 'https://www.kakao.com'
            },
            'button_title': '카카오'
        })
    }

    try:
        # 메시지 전송 API 요청
        response = requests.post(KAKAO_SEND_URL, headers=headers, data=payload)
        result = response.json()
        if response.status_code != 200:
            error = f"메시지 전송 실패: {result.get('msg', response.text)}"
            return render_friends_with_error(error)
    except Exception as e:
        # 네트워크 오류 등 예외 처리
        error = f"메시지 전송 중 오류 발생: {str(e)}"
        return render_friends_with_error(error)

    # 성공 시 친구 목록과 함께 결과 표시
    friends_response = requests.get(KAKAO_FRIENDS_URL, headers={'Authorization': f'Bearer {access_token}'})
    friends_list = friends_response.json().get('elements', []) if friends_response.status_code == 200 else []

    return render_template('friends.html', friends=friends_list, result=result)


# 🔸 메시지 전송 실패 시 오류와 함께 친구 목록 렌더링
def render_friends_with_error(error):
    access_token = session.get('access_token')
    friends_list = []

    if access_token:
        friends_response = requests.get(KAKAO_FRIENDS_URL, headers={'Authorization': f'Bearer {access_token}'})
        if friends_response.status_code == 200:
            friends_list = friends_response.json().get('elements', [])

    return render_template('friends.html', friends=friends_list, error=error)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot-password.html')

@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
    return render_template('mypage.html')

      

@app.route('/dash_board', methods=['POST'])
def generate_ppt():
    try:
        result = create_ppt(request)
        return result
    except Exception as e:
        return jsonify({"error": str(e)})   




@app.before_request
def log_request():
    logging.info(f"📌 요청 수신: {request.method} {request.path}")

@app.route("/download/pdf")
def download_pdf():
    return send_file("/app/output_ppt.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9500, debug=True)
