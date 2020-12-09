from flask import Flask, render_template, session, request, jsonify
from flask_jwt_extended import *



app = Flask(__name__)


from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

# NOTE: This is just a basic example of how to enable cookies. This is
#       vulnerable to CSRF attacks, and should not be used as is. See
#       csrf_protection_with_cookies.py for a more complete example!


app = Flask(__name__)

# Configure application to store JWTs in cookies. Whenever you make
# a request to a protected endpoint, you will need to send in the
# access or refresh JWT via a cookie.
app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# Set the cookie paths, so that you are only sending your access token
# cookie to the access endpoints, and only sending your refresh token
# to the refresh endpoint. Technically this is optional, but it is in
# your best interest to not send additional cookies in the request if
# they aren't needed.
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

# Disable CSRF protection for this example. In almost every case,
# this is a bad idea. See examples/csrf_protection_with_cookies.py
# for how safely store JWTs in cookies
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# Set the secret key to sign the JWTs with
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

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

# @app.route('/api/play', methods=['GET'])
# def play():
#    return render_template("play.html")

@app.route('/api/login', methods=['POST', 'GET'])
def login():
   if request.method == 'GET':
      return render_template("index.html")

   user_id = request.form['userId']
   password = request.form['password']
   user = db.users.find_one({'userid': user_id})

   # cur_user = get_jwt_identity()

   # 이미 토큰이 발급되었고, 유효하다면 로그인 성공 반환
   # if cur_user != None:
   #    print('토큰잇음')
   #    return jsonify(
   #       result="success",
   #       access_token=create_access_token(identity=user_id,
   #                                        expires_delta=False)
   #    )

   if(user == None):
      return jsonify({'result': 'fail_id'})
   elif(user_id == user['userid'] and password != user['password']):
      return jsonify({'result': 'fail_password'})
   elif(user_id == user['userid'] and password == user['password']):
      access_token = create_access_token(identity=user_id,
                                         expires_delta=False)
      resp = jsonify({'login': True})
      set_access_cookies(resp, access_token)
      cur_user = get_jwt_identity()
      # print(cur_user)

      return jsonify(
         result="success",
         resp = "token"
      )
   return jsonify({'result': 'fail_id'})

@app.route('/api/play', methods=["POST"])
@jwt_required
def play():
   # user_id = request.form['token']
   # print(user_id)
   cur_user = get_jwt_identity()
   print('로그인 유저',cur_user)
   if cur_user is None:
   	print("로그인 해주세요")
   else:
      return render_template("play.html")




# cur_user = get_jwt_identity()
	# if cur_user is None:
	# 	return "로그인 해주세요"
	# else:
	# 	return render_template("play.html")

# @app.errorhandler(401)
# def custom_401(error):
#     return Response('<Why access is denied string goes here...>', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)