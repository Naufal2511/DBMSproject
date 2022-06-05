from cv2 import DrawMatchesFlags_DRAW_OVER_OUTIMG
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField,ValidationError, DateField, IntegerField, RadioField, DateTimeField
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

class User(db.Model,UserMixin):
    Id = db.Column(db.Integer,primary_key = True)
    Username = db.Column(db.String(200), nullable = False, unique = True)
    Name = db.Column(db.String(200), nullable = False)
    Email = db.Column(db.String(200),nullable = False)
    PasswordHashed = db.Column(db.String(300),nullable = False)
    Phone = db.Column(db.String(12),nullable=True)
    UserType = db.Column(db.String(100),nullable = False)
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

class Events(db.Model,UserMixin):
    Id = db.Column(db.Integer,primary_key = True)
    EventName = db.Column(db.String(200),nullable = False)
    EventPrize = db.Column(db.String(200),nullable = False)
    EventDateTime = db.Column(db.DateTime,default=datetime.utcnow)
    EventVenue = db.Column(db.String(200),nullable = False)
    EventRules = db.Column(db.String(500),nullable=False)
    EventType = db.Column(db.String(100),nullable=False)
    EventContact = db.Column(db.String(100),nullable = False)
    def get_id(self):
        return (self.Id)

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

class AddEventForm(FlaskForm):
    eventname = StringField("Event Name",validators=[DataRequired()])
    eventtype = RadioField("Event Type", choices=['Technical','Non-technical'],validators=[InputRequired()])
    eventrules = StringField("Event Instructions",validators=[DataRequired()], widget=TextArea())
    eventvenue = StringField("Event Venue",validators=[DataRequired()])
    eventdatetime = DateField("Event date", validators=[DataRequired()])
    eventprize = StringField("Prize", validators=[DataRequired()])
    eventcontact = StringField("Contact", validators=[DataRequired(), Length(10,12)] )
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
        user = User.query.filter_by(Username=form.username.data).first()
        if user:
            #Checking hash
            if check_password_hash(user.PasswordHashed,form.password.data):
                login_user(user)
                print("Hi")
                # return redirect(url_for('redirectUsers'))
                if(user.UserType == 'Participant'):
                    flash("Redirecting to Participant page")
                    return redirect(url_for('dashboard_participant')) 
                if(user.UserType == 'Organizer'):
                    flash("Redirecting to Organiser page")  
                    return redirect(url_for('dashboard_organiser'))
                if(user.UserType == 'Admin'):
                    flash("Redirecting to Admin Page")
                    return redirect(url_for('dashboard_admin'))
            else:
                flash("Wrong Password")
        else:
            flash("This user doesnt exist")		

    return render_template('login.html',
		form = form)

# @app.route('/redirectUsers')
# def redirectUsers():
#     if(current_user.UserType == 'Participant'):
#         return redirect(url_for('dashboard_participant')) 
#     if(current_user.UserType == 'Organiser'):
#         return redirect(url_for('dashboard_organiser')) 

@app.route('/event_participant')
@login_required
def eventsPT():
    events = Events.query.filter_by(EventType = 'Technical')
    return render_template('eventsPT.html',
        events = events)

@app.route('/dashboard_participant')
@login_required
def dashboard_participant():
    if(current_user.is_authenticated):
        return render_template("dashboardP.html")
    else:
        return redirect('login')
    
@app.route('/dashboard_organiser')
@login_required
def dashboard_organiser():
    if(current_user.is_authenticated):
        return render_template("dashboardO.html")
    else:
        return redirect('login')

@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if(current_user.is_authenticated):
        events = Events.query.all()
        return render_template("dashboardA.html",
            events = events)
    else:
        return redirect('login')

@app.route('/add_event',methods=['POST','GET'])
@login_required
def add_event():
    print("Hi")
    if(current_user.UserType == 'Admin'):
        form = AddEventForm()
        if form.validate_on_submit():
            event = Events.query.filter_by(EventName=form.eventname.data).first()
            if event is None:
                event = Events(EventName=form.eventname.data,EventType=form.eventtype.data,
                    EventRules=form.eventrules.data,EventVenue=form.eventvenue.data,
                    EventDateTime = form.eventdatetime.data, EventPrize = form.eventprize.data,
                    EventContact = form.eventcontact.data)
                form.eventname.data = ''
                form.eventrules.data = ''
                form.eventvenue.data = ''
                form.eventdatetime.data = datetime.now()
                form.eventprize.data = ''
                form.eventcontact.data = ''

                db.session.add(event)
                db.session.commit()
                flash("Event added successfully")
                return redirect(url_for("dashboard_admin"))
            else:
                flash("Event already exists ! Try updating it")
        return render_template("add_event.html", form= form)
    else:
        flash("You should be an admin to edit")
        return redirect('home.html')

@app.route('/update/<int:Id>',methods=['POST','GET'])
def update(Id):
    form = AddEventForm()
    record_to_update = Events.query.get_or_404(Id)
    if request.method == 'POST':
        record_to_update.EventName = request.form['eventname']
        record_to_update.EventVenue = request.form['eventvenue']
        record_to_update.EventRules = request.form['eventrules']
        record_to_update.EventDateTime = request.form['eventdatetime']
        record_to_update.EventContact = request.form['eventcontact']
        try:
            db.session.commit()
            flash("Event Updated Successfully")
            return render_template("eventupdate.html",
                    form=form,
                    record_to_update=record_to_update)
        except:
            flash("Event could not be updated")
            return render_template("eventupdate.html",
                    form=form,
                    record_to_update=record_to_update)
    else:
        return render_template("eventupdate.html",
                    form=form,
                    record_to_update=record_to_update)
@app.route('/delete/<int:Id>')
def delete(Id):
	try:
		event_to_delete = Events.query.get_or_404(Id)
		db.session.delete(event_to_delete)
		db.session.commit()
		flash("Successfully deleted")
	except:
		flash("unable to delete")
		
	return redirect(url_for("dashboard_admin"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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