# app.py
import os
from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    redirect,
    url_for,
    render_template
)
from flask_sqlalchemy import SQLAlchemy
from face_verify import (register, verify)
app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    face = db.Column(db.Text(), unique=True, nullable=False)

    def __init__(self, username, face):
        self.username = username
        self.face = face

    @property
    def serialize(self):
       return {
           'id' : self.id,
           'username' : self.username,
           "face" : self.face
       }
db.drop_all()
db.create_all()
db.session.commit()
print("create")
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/users")
def users():
    return jsonify(json_list=[i.serialize for i in User.query.all()])

@app.route('/register', methods=['GET', 'POST'])
def registerFace():
    if request.method == 'POST':
        try:
            user = User.query.filter(User.username == request.form.get('name')).first()
            if user:
                return render_template('register.html', error = "User already exist.")
            face_as_list = register(request.form.get('face'))
            user = User(request.form.get('name'), face_as_list)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            return render_template('register.html', error = "Something goes wrong. Try again.")
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter(User.username == request.form.get('name')).first()
        if user:
            try:
                print("login")
                login = verify(request.form.get('face'), [user.face])
            except Exception as e:
                print(e)
                return render_template('login.html', errorMessage = "Something goes wrong. Try again.")
            if login:
                return render_template('login.html', successMessage = "Login successfully")
            else:
                return render_template('login.html', errorMessage = "Authorization failed")
        else:
            return render_template('login.html', errorMessage = "User with this name not found")
        return render_template('login.html')
    return render_template('login.html')  

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
    
