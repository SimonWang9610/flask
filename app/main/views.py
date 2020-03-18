from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import request, current_app
import os

from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm
# equals to 'import app.__init__'
from .. import db
from ..models import Role, User, Permission, Post
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    # create PostFrom
    form = PostForm()
    # store the content into the database
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        # store the new post into database
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    # posts are ordered by timestamp and in descending order
    # display posts in separated pages, each page is allowed to show 'FLASK_POSTS_PER_PAGE' posts
    # which can be visited by '/?page=WANT_TO_PAGE_NUMBER'
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    '''
    user page
    :return: user.html
    '''
    user = User.query.filter_by(username=username).first_or_404()
    # display user's posts in the profile page
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''
    create EditProfileForm
    :return: edited profile
    '''
    form = EditProfileForm()
    if form.validate_on_submit():

        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        # commit new profile in database
        db.session.add(current_user)
        db.session.commit()

        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    # show new profile in user's profile page
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():

        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data

        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated!')

        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me

    return render_template('edit_profile.html', form=form, user=user)

@main.route('/post/<int:id>')
def post(id):
    '''
    show posts
    :return: posts
    '''
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    '''
    for edit old posts
    :return: edited posts
    '''
    post = Post.query.get_or_404(id)
    # only author and administrators can access old posts
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        os.abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated!')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user!')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are following this user!')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}.'.format(username))
    return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user!')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of', endpoint='.followers',
                           pagination=pagination, follows=follows)

