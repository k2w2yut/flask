from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.picture import upload_to_s3, getS3URL

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.engine.execute(
        'SELECT p.id, title, body, created, author_id, username, picture_file'
        ' FROM posts p JOIN users u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    posts_dict = []
    for post in posts:
        d = dict(post)

        if d['picture_file']:
            d['signed_url'] = getS3URL(d['picture_file'])
        posts_dict.append(d)
    return render_template('blog/index.html', posts=posts_dict)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = get_db().engine.execute(
        'SELECT p.id, title, body, created, author_id, username, picture_file'
        ' FROM posts p JOIN users u ON p.author_id = u.id'
        ' WHERE p.id = \'{}\''.format(id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None


        if not title:
            error = 'Title is required.'

        pic_key = None
        if 'picture' in request.files:
            picture = request.files['picture']
            pic_key = upload_to_s3(picture)


        if error is not None:
            flash(error)
        else:
            db = get_db()
            if pic_key:
                db.engine.execute(
                    'INSERT INTO posts (title, body, author_id, picture_file)'
                    ' VALUES (\'{}\', \'{}\', \'{}\',\'{}\')'.format(title, body, g.user['id'],pic_key)
                )
            else:
                db.engine.execute(
                    'INSERT INTO posts (title, body, author_id)'
                    ' VALUES (\'{}\', \'{}\', \'{}\')'.format(title, body, g.user['id'])
                )
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.engine.execute(
                'UPDATE posts SET title = \'{}\', body = \'{}\' WHERE id = \'{}\''.format(title, body, id)
            )
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.engine.execute('DELETE FROM posts WHERE id = \'{}\''.format(id,))
    db.session.commit()
    return redirect(url_for('blog.index'))
