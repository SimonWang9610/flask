from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user
from flask_login import logout_user, login_required
from flask_login import current_user

from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    1. initialise the LoginForm
    2. display 'login.html'
    3. ensure the submitted form is validated
    4. query user from database
    5. verify password
    '''
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
            # make sure pages are in the server to prevent a malicious redirect
            if next is None or not next.startswith('/'):
                next = url_for('main.index')

            return redirect(next)

        flash('Invalid username or password!')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('main.index'))
'''
1. add a new user in database
2. generate a token used to send confirmation email
'''
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to your email!')

        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired!')

    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email!')

    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        # receive the last visit time before every request
        current_user.ping()
        if not current_user.confirmed \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


