from enum import unique
from tokenize import String
from typing import Text
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField,ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime 
from wtforms.widgets import TextArea
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
# Create a Flask Instance
app = Flask(__name__)
# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/insideOut'
# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class users(db.Model,UserMixin):
	Uid = db.Column(db.Integer, primary_key=True)
	Username = db.Column(db.String(100), nullable = False, unique = True)
	Name = db.Column(db.String(200), nullable=False)
	Email = db.Column(db.String(120), nullable=False, unique=True)
	FavoriteColor=db.Column(db.String(120))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	PasswordHashed = db.Column(db.String(180), nullable=False)

	def get_id(self):
		return (self.Uid)
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
class Posts(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(255))
	content=db.Column(db.Text) #TextArea
	author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default = datetime.utcnow)
	slug = db.Column(db.String(255))
# Create a Form Class
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("UserName", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favoriteColor = StringField("Favorite Colour")
	password = PasswordField("Password",validators=[DataRequired(),EqualTo('password2',message="Passwords must match!")])
	password2 = PasswordField("Confirm Password",validators=[DataRequired()])
	submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")

class PostForm(FlaskForm):
	title = StringField("Title",validators=[DataRequired()])
	content = StringField("Content",validators=[DataRequired()], widget=TextArea())
	author = StringField("Author",validators=[DataRequired()])
	slug = StringField("Slug",validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	username = StringField("UserName",validators=[DataRequired()])
	password = PasswordField("Password", validators = [DataRequired()])
	submit = SubmitField("Submit") 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
	return users.query.get(int(user_id))
# Create Model
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

@app.route('/dashboard',methods=['POST','GET'])
@login_required
def dashboard():
	return render_template('dashboard.html')
@app.route('/add_post',methods=['GET','POST'])
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''

		db.session.add(post)
		db.session.commit()
		flash("Post added successfully")
	return render_template("add_post.html",form=form)
@app.route('/posts')
def posts():
	#Grabbing all the posts from the database
	posts = Posts.query.order_by(Posts.date_posted)
	
	return render_template('post.html',
				posts=posts)

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



#def index():
#	return "<h1>Hello World!</h1>"

# FILTERS!!!
#safe
#capitalize
#lower
#upper
#title
#trim
#striptags

@app.route('/update/<int:Uid>',methods=['POST','GET'])
def update(Uid):
	form = UserForm()
	record_to_update = users.query.get_or_404(Uid)
	if request.method == 'POST':
		record_to_update.Name = request.form['name']
		record_to_update.Email = request.form['email']
		record_to_update.FavoriteColor = request.form['favoriteColor']
		record_to_update.Username = request.form['username']
		try:
			db.session.commit()
			flash("User Updated Successfully")
			return render_template("updateUser.html",
                    form=form,
                    record_to_update=record_to_update)
		except:
			flash("User could not be updated")
			return render_template("updateUser.html",
                    form=form,
                    record_to_update=record_to_update)
	else:
		return render_template("updateUser.html",
                    form=form,
                    record_to_update=record_to_update)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = users.query.filter_by(Email=form.email.data).first()
		if user is None:
			hashedPwd = generate_password_hash(form.password.data)
			print(hashedPwd)
			user = users(Name=form.name.data,Username=form.username.data, Email=form.email.data, FavoriteColor=form.favoriteColor.data, PasswordHashed = hashedPwd)
            #Inserting An record to mySQL
			db.session.add(user)
			db.session.commit()
		else:
			flash('User repeated')
		
		name = form.name.data
		form.name.data = ''
		form.username.data = ''

		form.email.data = ''	
		form.favoriteColor.data = ''
		form.password.data = ''

		flash("User Added Successfully!")
	our_users = users.query.order_by(users.date_added)
	return render_template("add_user.html", 
		form=form,
		name=name,
		our_users=our_users)

@app.route('/delete/<int:Uid>')
def delete(Uid):
	name = None
	form = UserForm()
	try:
		user_to_delete = users.query.get_or_404(Uid)
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("Successfully deleted")
	except:
		flash("unable to delete")
		
	our_users = users.query.order_by(users.date_added)

	return redirect("/user/add")

# Create a route decorator
@app.route('/')
def index():
	first_name = "John"
	stuff = "This is bold text"

	favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
	return render_template("index.html", 
		first_name=first_name,
		stuff=stuff,
		favorite_pizza = favorite_pizza)

# localhost:5000/user/John
@app.route('/user/<name>')

def user(name):
	return render_template("user.html", user_name=name)

# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")
		
	return render_template("name.html", 
		name = name,
		form = form)

if __name__=='__main__':
    app.run(debug=True)
