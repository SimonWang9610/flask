from flask import jsonify, request, url_for, g
from flask import current_app

from . import api
from.errors import forbidden
from .decorators import permission_required

from .. import db
from ..models import Post
from ..models import Permission


@api.route('/posts/')
def get_posts():
    # display all posts in different page
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PERPAGE'], error_out=False
    )
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', pahe=page+1)

    return jsonify({'posts': [post.to_json() for post in posts],
                    'prev_url': prev,
                    'next_url': next,
                    'count': pagination.total})

@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    # request.json: get json of the new post
    # Post.from_json(): convert json to the object of Post so as to add it into database
    post = Post.from_json(request.json)
    # set author as current_user
    post.author = g.current_use
    db.session.add(post)
    db.session.commit()
    # display the new post as json format
    return jsonify(post.to_json(), 201, {'Location': url_for('api.get_post', id=post.id)})

@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    # get the specific post
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
        not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permission!')
    # change post.body as the new content of the request
    # add and commit the edited post in database
    post.body = request.json.get('body', post.bdy)
    db.session.add(post)
    db.session.commit()
    # display the edited post as json format
    return jsonify(post.to_json())

