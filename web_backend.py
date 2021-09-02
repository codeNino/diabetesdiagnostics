from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
import bcrypt, os
import warnings, requests
warnings.filterwarnings("ignore")
from flask_login import login_required, LoginManager, logout_user,login_user
from flask_session import Session, SqlAlchemySessionInterface
from flask_migrate import Migrate
from datetime import datetime
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class ConfigClass(object):

     
    SECRET_KEY = environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = environ.get('SESSION_TYPE')


    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

# Setup Flask-SQLALchemy
db = SQLAlchemy()    

# Setup Flask and load app.config
    
def create_app():
    
    app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
    
    app.config.from_object(__name__+'.ConfigClass')

    db.init_app(app)

    
    sess = Session()
    sess.init_app(app)
    #SqlAlchemySessionInterface(app, db, "session", "sess_")

    return app

app = create_app()

class User(db.Model):

    __tablename__ = 'patients_data'

    Id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Created_On = db.Column(db.DateTime, default= datetime.now())
    Last_Login = db.Column(db.DateTime, nullable=True)
    Admin = db.Column(db.Boolean, default= False)

    #user auth info
    Email = db.Column(db.String(), unique=True)

    Password = db.Column(db.LargeBinary())
    #user personal info
    FirstName = db.Column(db.String())
    LastName = db.Column(db.String())
    #user health features
    Height = db.Column(db.Float)
    Weight = db.Column(db.Float)
    BMI = db.Column(db.Float)
    Pregnancy = db.Column(db.Integer())
    Age = db.Column(db.Integer())
    Blood_Pressure = db.Column(db.Float, nullable=True)
    Glucose_level = db.Column(db.Float, nullable=True)

    def __init__(self, Email, Password, FirstName, LastName, Height, Weight, BMI, Pregnancy, Age):
        self.Email = Email
        self.Password = Password
        self.FirstName = FirstName
        self.LastName = LastName
        self.Height = Height
        self.Weight = Weight
        self.Pregnancy = Pregnancy
        self.Age = Age
        self.authenticated = None
        self.BMI = BMI
    

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
            if session['email'] == environ.get('ADMIN_EMAIL'):
                return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('landing_page'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if "email" in session:
            if session['email'] == environ.get('ADMIN_EMAIL'):
                return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('landing_page'))


admin = Admin(app, index_view=MyAdminIndexView())

admin.add_view(MyModelView(User, db.session))



# migrate = Migrate()
# migrate.init_app(app, db)


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
            
            if email == environ.get('ADMIN_EMAIL') and pwd == environ.get('ADMIN_PWD'):
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
                    existing_user.Last_Login = datetime.now()

                    db.session.commit()

                    if existing_user.Admin == True:
                        session['email'] = existing_user.Email
                        return redirect('/admin')

                    else:
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
            height = float(data['height'])
            weight = float(data['weight'])

            existing_user = db.session.query(User).filter(User.Email == email).first()

            if existing_user is None and passwd_1 == passwd_2:
                
                user = User(Email= email.lower(),
                      Password= bcrypt.hashpw(passwd_1.encode('utf8'), bcrypt.gensalt()),
                          FirstName = f_name.upper(),
                                LastName = l_name.upper(),
                                Height = height,
                                Weight = weight,
                         BMI = weight/(height**2),
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
    bp = user.Blood_Pressure
    glucose = user.Glucose_Level

    data = {
              "Age": age,
              "Pregnancy": pregnancy,
              "BMI": bmi,
              "Blood Pressure": bp,
              "Glucose": glucose
            }

    response = requests.post(url="http://0.0.0.0:5002/detect", json= data)

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
        if request.args.get('type') == 'refresh':
            return redirect(url_for('home_page'))



@app.route("/logout")
@login_required
def logout():

    logout_user()
    session.clear()

    return redirect(url_for('landing_page'))
		



if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)