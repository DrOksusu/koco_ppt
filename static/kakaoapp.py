import os
import requests
from flask import Flask, redirect, request, session, url_for, jsonify, render_template
import json

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 세션에서 사용할 secret key 설정 (환경변수에서 읽거나 기본값 사용)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')

# 🔑 카카오 API 관련 상수들 (환경변수 또는 하드코딩된 기본값)
KAKAO_CLIENT_ID = os.environ.get('KAKAO_CLIENT_ID', 'ccb9d48d7702c55ca74794e105af647b') #naturem-clinic api
KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI', 'http://localhost:9000/kakao')
KAKAO_AUTH_URL = 'https://kauth.kakao.com/oauth/authorize'
KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
KAKAO_USER_URL = 'https://kapi.kakao.com/v2/user/me'
KAKAO_FRIENDS_URL = 'https://kapi.kakao.com/v1/api/talk/friends'
KAKAO_SEND_URL = 'https://kapi.kakao.com/v1/api/talk/friends/message/default/send'


# 🔸 홈 화면
@app.route('/')
def home():
    user = session.get('user')  # 세션에 저장된 사용자 정보 가져오기
    if user:
        # 로그인 되어 있으면 사용자 정보와 친구목록 보기 링크 표시
        html = f"""
        <h1>카카오 로그인 성공</h1>
        <p>이름: {user.get('properties', {}).get('nickname')}</p>
        <p>이메일: {user.get('kakao_account', {}).get('email')}</p>    
        <p><a href="/friends">친구 목록</a></p>
        <a href="/logout">로그아웃</a>
        """
        return html
    else:
        # 로그인 안 되어 있으면 로그인 링크 표시
        return '<a href="/login">카카오 로그인</a>'


# 🔸 카카오 로그인 요청
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
    # 세션에서 사용자 정보 제거
    session.pop('user', None)
    session.pop('access_token', None)
    return redirect(url_for('home'))


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


# # 🔸 앱 실행 (개발 서버 실행)
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=9000, debug=True)
