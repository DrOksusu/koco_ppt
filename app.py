from flask import Flask, request, jsonify, send_file, render_template, url_for
from flask_cors import CORS
from ppt_generator import create_ppt
from green_line import draw_psa_line
import os
from config import UPLOAD_FOLDER, RESULT_FOLDER
from werkzeug.utils import secure_filename
import logging
from flask import request


app = Flask(__name__)

CORS(app)

@app.route('/')
def home():

    return render_template('index1.html', login_url=url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html',
                           signup_url=url_for('signup'))  # signup_url 넘겨줌

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
