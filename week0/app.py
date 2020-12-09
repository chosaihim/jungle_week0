from flask import Flask, render_template, session, request, jsonify
from flask_jwt_extended import *



app = Flask(__name__)


from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

app = Flask(__name__)

# app.config['JWT_SECRET_KEY'] = 'elgnuj'  # Change dthis!

app.config.update(
   DEBUG = True,
   JWT_SECRET_KEY='elgnuj',
   # JWT_COOKIE_SECURE = False, # https를 통해서만 cookie가 갈 수 있는지 (production 에선 True)
   JWT_TOKEN_LOCATION = ['cookies'],
   JWT_ACCESS_COOKIE_PATH = '/', # access cookie를 보관할 url (Frontend 기준)
   JWT_REFRESH_COOKIE_PATH = '/', # refresh cookie를 보관할 url (Frontend 기준)
   # # CSRF 토큰 역시 생성해서 쿠키에 저장할지
   # # (이 경우엔 프론트에서 접근해야하기 때문에 httponly가 아님)
   JWT_COOKIE_CSRF_PROTECT = False
)

jwt = JWTManager(app)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.week0

@app.route('/')
@jwt_optional
def home():
   cur_user = get_jwt_identity()
   print(cur_user)
   if cur_user is not None:
      return render_template("play.html")
   return render_template("index.html")

@app.route('/api/register', methods=['POST', 'GET'])
def register():
   if request.method == 'GET':
      return render_template("register.html")

   user_id = request.form['userId']
   password = request.form['password']

   user = db.users.find_one({'userid': user_id})
   #해당 아이디 이미 있으면 fail
   if(user != None):
      return jsonify({'result': 'fail'})

   db.users.insert_one({'userid': user_id, 'password': password, 'volume':0})

   return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST', 'GET'])
def login():
   if request.method == 'GET':
      return render_template("index.html")

   user_id = request.form['userId']
   password = request.form['password']
   user = db.users.find_one({'userid': user_id})

   if(user == None):
      return jsonify({'result': 'fail_id'})
   elif(user_id == user['userid'] and password != user['password']):
      return jsonify({'result': 'fail_password'})
   elif(user_id == user['userid'] and password == user['password']):
      access_token = create_access_token(identity=user_id,
                                         expires_delta=False)
      refresh_token = create_refresh_token(identity=user_id,
                                         expires_delta=False)
      resp = jsonify({'result': 'success'})
      set_access_cookies(resp, access_token)
      set_refresh_cookies(resp, refresh_token)
      return resp

@app.route('/api/play', methods=["POST"])
@jwt_required
def play():
   cur_user = get_jwt_identity()
   if cur_user is None:
   	print("로그인 해주세요")
   else:
      print('로그인 유저', cur_user)
      return render_template("play.html")

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)