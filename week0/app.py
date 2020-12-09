from flask import Flask, render_template, session, request, jsonify
from flask_jwt_extended import *


app = Flask(__name__)

app.config.update(
   DEBUG = True,
   JWT_SECRET_KEY = "elgnuj"
)

jwt = JWTManager(app)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.week0

@app.route('/')
def home():
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

# @app.route('/api/play', methods=['GET'])
# def play():
#    return render_template("play.html")

@app.route('/api/login', methods=['POST', 'GET'])
def login():
   if request.method == 'GET':
      return render_template("play.html")

   user_id = request.form['userId']
   password = request.form['password']

   user = db.users.find_one({'userid': user_id})

   if(user == None):
      return jsonify({'result': 'fail_id'})
   elif(user_id == user['userid'] and password != user['password']):
      return jsonify({'result': 'fail_password'})
   elif(user_id == user['userid'] and password == user['password']):
      return jsonify(
         result="success",
         # 검증된 경우, access 토큰 반환
         access_token=create_access_token(identity=user_id,
                                          expires_delta=False)
      )
   return jsonify({'result': 'fail_id'})

@app.route('/api/play', methods=["GET"])
@jwt_required
def mypage():
	cur_user = get_jwt_identity()
	if cur_user is None:
		return "로그인 해주세요"
	else:
		return "어서오세요!" + cur_user + '님'

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)