from flask import Flask, render_template, session, request, jsonify
from flask_jwt_extended import *
from werkzeug.security import check_password_hash, generate_password_hash




app = Flask(__name__)


from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

app = Flask(__name__)

app.config.update(
   DEBUG = True,
   JWT_SECRET_KEY='jungle',
   # JWT_COOKIE_SECURE = False, # https를 통해서만 cookie가 갈 수 있는지 (production 에선 True)
   JWT_TOKEN_LOCATION = ['cookies'],
   JWT_ACCESS_COOKIE_PATH = '/', # access cookie를 보관할 url (Frontend 기준)
   JWT_REFRESH_COOKIE_PATH = '/', # refresh cookie를 보관할 url (Frontend 기준)
   # # CSRF 토큰 역시 생성해서 쿠키에 저장할지(이 경우엔 프론트에서 접근해야하기 때문에 httponly가 아님)
   JWT_COOKIE_CSRF_PROTECT = False,

)

jwt = JWTManager(app)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.week0

@app.route('/')
@jwt_optional
def home():
   cur_user = get_jwt_identity()
   if cur_user is not None:
      return render_template("play.html")
   return render_template("index.html")

@app.route('/api/register', methods=['POST', 'GET'])
def register():
   if request.method == 'GET':
      return render_template("register.html")

   user_id = request.form['userId']
   password = request.form['password']
   password_hash = generate_password_hash(password, 'sha256')

   user = db.users.find_one({'userid': user_id})
   #해당 아이디 이미 있으면 fail
   if(user != None):
      return render_template("register.html")

   db.users.insert_one({'userid': user_id, 'password': password_hash, 'vol1': 0.5, 'vol2': 0.5, 'vol3': 0.5, 'vol4': 0.5})

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
   elif(user_id == user['userid'] and not check_password_hash(user['password'], password)):
      return jsonify({'result': 'fail_password'})
   elif(user_id == user['userid'] and check_password_hash(user['password'], password)):
      access_token = create_access_token(identity=user_id,
                                         expires_delta=False)
      refresh_token = create_refresh_token(identity=user_id,
                                         expires_delta=False)
      resp = jsonify({'result': 'success'})
      set_access_cookies(resp, access_token)
      set_refresh_cookies(resp, refresh_token)
      return resp

@app.route('/api/logout', methods=['POST'])
def logout():
    resp = jsonify({'result': 'success'})
    unset_jwt_cookies(resp)
    return resp

@app.route('/api/save', methods=['POST'])
@jwt_required
def save():

   userid = get_jwt_identity()

   print("userid = ", userid)
   vol1 = request.form['vol1']
   vol2 = request.form['vol2']
   vol3 = request.form['vol3']
   vol4 = request.form['vol4']

   print("volumes: ", vol1, vol2, vol3, vol4)

   db.users.update_one({'userid': userid}, {'$set': {'vol1': vol1}})
   db.users.update_one({'userid': userid}, {'$set': {'vol2': vol2}})
   db.users.update_one({'userid': userid}, {'$set': {'vol3': vol3}})
   db.users.update_one({'userid': userid}, {'$set': {'vol4': vol4}})

   return jsonify({'result': 'success'})

@app.route('/api/play', methods=["POST"])
@jwt_required
def play():
   cur_user = get_jwt_identity()
   if cur_user is None:
   	print("로그인 해주세요")
   else:
      print('로그인 유저', cur_user)

      user = db.users.find_one({'userid': cur_user})

      return render_template("play.html", _vol1 = user['vol1'], _vol2 = user['vol2'], _vol3 = user['vol3'], _vol4 = user['vol4'])

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)