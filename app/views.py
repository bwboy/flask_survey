from flask import Flask, render_template, flash, redirect, session, url_for, request, g, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm#, EditForm
from models import User, ROLE_USER, ROLE_ADMIN
# #from datetime import datetime
# #from emails import follower_notification
# #from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

# @app.route('/create_acct')
# def create_acct():
# 	return render_template("create_acct.html")

@app.route('/create_acct' , methods=['GET','POST'])
def create_acct():
	if request.method == 'GET':
		return render_template('create_acct.html')
	user = User(request.form['username'] , request.form['passwd'])
	db.session.add(user)
	db.session.commit()
	flash('You will be sent an email to verify your account')
	return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    passwd = request.form['passwd']
    registered_user = User.query.filter_by(username=username,passwd=passwd).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        #add attempt to a log organized by time
        #userid passwd event time  event = failed, success, retrieve passwd
        #retrieve passwd as event
        #login attempts, failed
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/')
@app.route('/index')
# @login_required
def index():
	user = g.user
	return render_template ("index.html",
		title = "Home", 
		user = user)

@app.route('/about')
def about():
	return render_template("about.html",
		title = "About")

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

# @app.route('/login', methods = ['GET', 'POST'])
# @oid.loginhandler
# def login():
# 	if g.user is not None and g.user.is_authenticated():		#if g is not anonymous
# 		return redirect(url_for('index'))
# 	form = LoginForm()
# 	if form.validate_on_submit():
# 		flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
# 		session['remember_me'] = form.remember_me.data
# 		return oid.try_login(form.openid.data, ask_for = ['username', 'email'])
# 	return render_template("login.html",
# 		title = "Login",
# 		form = form,
# 		providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):		#resp = response from openid
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email = resp.email).first()
	
	if user is None:
		username = resp.username
		if username is None or username == "":
			username = resp.email.split('@')[0]
		user = User(username = username, email = resp.email, role = ROLE_USER)
		db.session.add(user)
		db.session.commit()
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
	g.user = current_user

@app.route('/logout')
def logout():
	#double check if the 
	logout_user()
	return redirect(url_for('index'))

@app.errorhandler(404)
def internal_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # db.session.rollback()
    return render_template('500.html'), 500

