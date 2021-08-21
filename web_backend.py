from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
import bcrypt, os
import warnings, requests
warnings.filterwarnings("ignore")
from flask_login import login_required, LoginManager, logout_user,login_user
from flask_session import Session
from flask_migrate import Migrate
from datetime import datetime
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView


class ConfigClass(object):

     
    SECRET_KEY = 'hiahuwhqsj qk2uhu3ih29h232jid j 2iugu32gibdbi i2 dug ucn cewuui33 '

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:oluwanino7@localhost:5432/patients"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = 'mongodb'


    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    
# Setup Flask and load app.config
    
app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
    
app.config.from_object(__name__+'.ConfigClass')

# Setup Flask-SQLALchemy
db = SQLAlchemy()
db.init_app(app)

#admin = Admin(app)




class User(db.Model):

    __tablename__ = 'patients_data'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    logdate = db.Column(db.DateTime, default= datetime.now())

    #user auth info
    Email = db.Column(db.String())

    Password = db.Column(db.LargeBinary())
    #user personal info
    FirstName = db.Column(db.String())
    LastName = db.Column(db.String())
    #user features
    BMI = db.Column(db.Float())
    Pregnancy = db.Column(db.Integer())
    Age = db.Column(db.Integer())

    def __init__(self, Email, Password, FirstName, LastName, BMI, Pregnancy, Age):
        self.Email = Email
        self.Password = Password
        self.FirstName = FirstName
        self.LastName = LastName
        self.BMI = BMI
        self.Pregnancy = Pregnancy
        self.Age = Age
        self.authenticated = None
    

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email to satisfy Flask-Login's requirements."""
        return self.Email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
   


class MyModelView(ModelView):
    def is_accessible(self):
        if "email" in session:
            if session['email'] == 'lordnino7@gmail.com':
                return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('landing_page'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if "email" in session:
            if session['email'] == 'lordnino7@gmail.com':
                return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('landing_page'))


admin = Admin(app, index_view=MyAdminIndexView())

admin.add_view(MyModelView(User, db.session))



migrate = Migrate()
migrate.init_app(app, db)



#Initiate session
sess = Session()
sess.init_app(app)

#load login manager

login_manager = LoginManager()
login_manager.init_app(app)




@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.Email == user_id).first()

def login_required(func):
    def secure_function():
        if "email" not in session:
            return redirect(url_for("login"))
        return func()
    secure_function.__name__ = func.__name__

    return secure_function



@app.route('/')
def landing_page():
    if "email" in session:
        if session['email'] != 'lordnino7@gmail.com':
            return redirect(url_for('home_page'))
        else:
            return redirect('admin')
    return render_template('signin.html')

    

@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form['signin']== 'signin':


            data = request.form.to_dict()

            email = data['email']
            pwd = data['pass']
            
            if email == 'lordnino7@gmail.com' and pwd == 'holuwarnino':
                session['email'] = email
                return redirect('/admin')

            existing_user = db.session.query(User).filter(User.Email == email).first()

            if existing_user is not None:
                passwd = existing_user.Password
                if bcrypt.checkpw(pwd.encode('utf-8'), passwd):
                    existing_user.authenticated = True
                    existing_user.active = True
                    login_user(existing_user, remember=True)
                    session['logged_in'] = True
                    session['email'] = existing_user.Email


                    return redirect(url_for('home_page'))
                else:
                    error = "! Invalid Password"
                    return render_template('signin.html', error = error)

            while existing_user == None:
                error = "! Username does not exist "
                return render_template('signin.html', error = error)


    elif request.method == "GET":

        if request.args.get('type') == 'Sign up':

            return redirect(url_for('signup'))


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def register():
    if request.method == "POST":
        if request.form['sign up'] == 'sign up':
            
            data = request.form.to_dict()
        
            email = data['email']
            passwd_1 = data['pass1']
            passwd_2 = data['pass2']
            f_name = data['firstname']
            l_name = data['lastname']
            age = int(data['age'])
            preg = int(data['pregnancy'])
            bmi = float(data['bmi'])

            existing_user = db.session.query(User).filter(User.Email == email).first()

            if existing_user is None and passwd_1 == passwd_2:
                
                user = User(Email= email.lower(),
                      Password= bcrypt.hashpw(passwd_1.encode('utf8'), bcrypt.gensalt()),
                          FirstName = f_name.upper(),
                                LastName = l_name.upper(),
                         BMI = bmi,
                           Age = age,
                               Pregnancy = preg,
                             )
                db.session.add(user)
                db.session.commit()
                user.authenticated = True
                login_user(user, remember=True)
                session['logged_in'] = True
                session['email'] = user.get_id()
                return redirect(url_for('home_page'))

            elif existing_user is not None:

                details = " ! Username already taken "
                return render_template('signup.html', error = details)

            elif passwd_1 != passwd_2:
                details = "! Password must match "
                return render_template('signup.html', error = details)
            

    elif request.method == "GET":

        if request.args.get('type') == 'sign in':

            return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def home_page():
    user_id = session['email']
    user = load_user(user_id)
    user.active = True
    user_info = user

    age = user.Age
    pregnancy = user.Pregnancy
    bmi = user.BMI
    bp = None
    glucose = None

    data = {
              "Age": age,
              "Pregnancy": pregnancy,
              "BMI": bmi,
              "Blood Pressure": bp,
              "Glucose": glucose
            }

    response = requests.post(url="http://127.0.0.1:5002/detect", json= data)

    response = response.json()['pred']

    return render_template('index.html', information=user_info, more_info=data, prediction = response)


@app.route("/dashboard",methods = ['GET'])
def signout():
    if request.method == "GET":

         if request.args.get('type') == 'sign out':

            
             logout_user()
             session.clear()

             return redirect(url_for('landing_page'))

def refresh():
    if request.method == "GET":
        if request.args.get('type') == 'refreh':
            return redirect(url_for('home_page'))



@app.route("/logout")
@login_required
def logout():

    logout_user()
    session.clear()

    return redirect(url_for('landing_page'))
		



if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)