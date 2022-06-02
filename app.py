from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField,ValidationError, DateField, IntegerField, RadioField
from wtforms.validators import DataRequired, EqualTo, Length,Email,InputRequired
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime 
from wtforms.widgets import TextArea
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user

app = Flask(__name__)  # __name__ is a variable that can be accessed by any python file
#render_template is used to load different HTML Pages stored in templates folder.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/project'
app.config['SECRET_KEY'] = "jdhsjjhhjshjkhskdsj"

db = SQLAlchemy(app)
migrate = Migrate(app,db)

class User(db.Model):
    Id = db.Column(db.Integer,primary_key = True)
    Username = db.Column(db.String(200), nullable = False, unique = True)
    Name = db.Column(db.String(200), nullable = False)
    Email = db.Column(db.String(200),nullable = False)
    PasswordHashed = db.Column(db.String(300),nullable = False)
    Phone = db.Column(db.String(12),nullable=True)
    UserType = db.Column(db.String(10))
    Date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def get_id(self):
        return (self.Id)
    @property
    def password(self):
        raise AttributeError ('Password is not readable')

    @password.setter
    def password(self,password):
        self.PasswordHashed = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.PasswordHashed,password)
        # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

class RegisterForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])
    name = StringField("Name",validators=[DataRequired()])
    email = StringField("Email",validators=[Email(),DataRequired()])
    phone = StringField("Phone",validators=[Length(10,12)])
    userType = RadioField("User Type", choices=['Participant','Organizer','Admin'],validators=[InputRequired()])
    password = PasswordField("Password",validators=[DataRequired(),EqualTo('password2',message="Passwords must match!")])
    password2 = PasswordField("Re-enter Password",validators=[DataRequired()])
    submit = SubmitField("Submit")

#WTF FORMS TYPES
# BooleanField
	# DateField
	# DateTimeField
	# DecimalField
	# FileField
	# HiddenField
	# MultipleField
	# FieldList
	# FloatField
	# FormField
	# IntegerField
	# PasswordField
	# RadioField
	# SelectField
	# SelectMultipleField
	# SubmitField
	# StringField
	# TextAreaField

	## Validators
	# DataRequired
	# Email
	# EqualTo
	# InputRequired
	# IPAddress
	# Length
	# MacAddress
	# NumberRange
	# Optional
	# Regexp
	# URL
	# UUID
	# AnyOf
	# NoneOf
class LoginForm(FlaskForm):
	username = StringField("UserName",validators=[DataRequired()])
	password = PasswordField("Password", validators = [DataRequired()])
	submit = SubmitField("Submit") 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/register',methods = ['POST','GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email = form.email.data,Username = form.username.data).first()
        if user is None:
            hashedPwd = generate_password_hash(form.password.data)
            user = User(Username=form.username.data, Name=form.name.data, Email=form.email.data, PasswordHashed=hashedPwd, Phone=form.phone.data, UserType = form.userType.data)
            db.session.add(user)
            db.session.commit()
            flash('User has successfully registered')
            flash('You can login now')
            return redirect('login')

        else:
            flash('User is already registered')
            return redirect('login')
    
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''	
        form.password.data = ''
    
    return render_template('register.html', form = form)

@app.route('/login',methods =['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit:
		user = users.query.filter_by(Username=form.username.data).first()
		if user:
			#Checking hash
			if check_password_hash(user.PasswordHashed,form.password.data):
				login_user(user)
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password")
		else:
			flash("This user doesnt exist")		

	return render_template('login.html',
		form = form)

@app.route('/')#It is a decorator (what URL to be accessed)
def index():
    firstName = "John"
    stuff = "This is bold text"
    favoritePizza = ["Pepperoni" , "Cheese" , "Chilli" , 41]
    return render_template("index.html",
        firstName = firstName,
        stuff =stuff,
        favoritePizza=favoritePizza)

#Creating custom error pages
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)

def page_not_found(e):
    return render_template("500.html") 

if __name__=='__main__':
    app.run(debug=True)