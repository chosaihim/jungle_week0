from flask import Flask, render_template, session, request, jsonify, redirect

app = Flask(__name__)
app.secret_key = 'it_is_secret_zzz'

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.week0


@app.route('/')
def home():
    if 'userid' in session:
        return render_template("play.html")
    else:
        print('세션 off')

    return render_template("index.html")


@app.route('/api/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    user_id = request.form['userId']
    password = request.form['password']
    db.users.insert_one({'userid': user_id, 'password': password, 'volume': 0})
    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("index.html")

    user_id = request.form['userId']
    user_password = request.form['password']
    if db.users.find_one({'userid': user_id, 'password': user_password}) is not None:
        session['userid'] = request.form['userId']
    return jsonify({'result': 'success'})


@app.route('/api/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)