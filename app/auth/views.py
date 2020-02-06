from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user
from flask_login import logout_user, login_required

from . import auth
from ..models import User
from .forms import LoginForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # load user information from the database by 'email'
        user = User.query.filter_by(email=form.email.data).first()
        # verify user's password
        if user is not None and user.verify_password(form.password.data):
            # record the user as logged in for the user session
            login_user(user, form.remember_me)
            # achieve the redirected address 'next'
            next = request.args.get('next')
            # prevent a malicious redirect
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        # if email and password are invalid, show a flash message
        flash('Invalid username or password!')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('main.index'))