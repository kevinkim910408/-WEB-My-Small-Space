from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta



app = Flask(__name__) # Flask 객체를 app이라는 변수에 할당
#config안의 속성들의 값을 조절
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA' # 로그인 토큰 만들때 secret key

# sparta@cluster0 (내 db폴더이름@내클러스터이름)
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


# main page
@app.route('/')
def home():
    # 생성된 쿠키 가져오기
    token_receive = request.cookies.get('mytoken')
    try: #쿠키를 이용해서 jwt 자유이용권 만듬
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 자유이용권에 등록된 유저 id를 가져오기
        user_info = db.users.find_one({"username": payload["id"]})
        # 유저 정보를 jinja로 가져다 쓸수있게 return 해줌
        return render_template('index.html', user_info=user_info)
    
    # 에러처리
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 페이지
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():
 
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': 'Wrong ID/PASSWORD'})

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # id 중복확인
    username_receive = request.form['username_give'] #request form으로 username을 받고
    # bool 값을 사용해서, db에 username이 있는지 체크
    exists = bool(db.users.find_one({"username": username_receive}))
    # bool 값을 넘겨줘서 있다 없다를 체크 가능
    return jsonify({'result': 'success', 'exists': exists})

# DB 에서 뉴스 받아오기
@app.route('/news', methods=["GET"])
def get_news():
    # 뉴스 리스트를 반환하는 API
    news_list = list(db.news.find({}, {'_id': False}))
    # news_list 라는 키 값에 맛집 목록을 담아 클라이언트에게 반환합니다.
    return jsonify({'result': 'success', 'news_list': news_list})

@app.route('/weather', methods=['GET'])
def show_diary():
    sample_receive = request.args.get('sample_give')
    print(sample_receive)
    return jsonify({'msg': 'GET 연결 완료!'})

@app.route('/weather', methods=['POST'])
def save_diary():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg': 'POST 요청 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)