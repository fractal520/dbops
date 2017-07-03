from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, EditDbinfoForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Alarm_log, Dbinfo, Dbtype, Check_connect_num_log
from ..decorators import admin_required, permission_required
import json
import time


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s^rParameters: %s^rDuration: %fs^rContext: %s^r'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.EDIT_DBINFO) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_alarm_logs
    else:
        query = Alarm_log.query
    pagination = query.order_by(Alarm_log.create_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    alarm_logs = pagination.items
    return render_template('index.html', form=form, alarm_logs=alarm_logs,
                           show_followed=show_followed, pagination=pagination)

@main.route('/monitor', methods=['GET', 'POST'])
def monitor():
    form = PostForm()
    if current_user.can(Permission.EDIT_DBINFO) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_alarm_logs
    else:
        query = Alarm_log.query
    pagination = query.order_by(Alarm_log.create_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    alarm_logs = pagination.items
    return render_template('index.html', form=form, alarm_logs=alarm_logs,
                           show_followed=show_followed, pagination=pagination)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)

@main.route('/dbinfo/')
def dbsinfo():
    dbinfos = Dbinfo.query.order_by(Dbinfo.add_time.desc()).all()
    return render_template('dbinfo.html', dbinfos=dbinfos)

@main.route('/dbinfo/<instance_name>')
def dbinfo(instance_name):
    dbinfo = Dbinfo.query.filter_by(instacne_name=instance_name).first_or_404()
    return render_template('dbinfo.html', dbinfos=[dbinfo])

@main.route('/edit_alarm/<id>')
def edit_alarm(instance_name):
    dbinfo = Dbinfo.query.filter_by(instance_name=instance_name).first_or_404()
    return render_template('dbinfo.html', dbinfo=dbinfo)

@main.route('/dbsummary/<dbname>')
def dbsummary(dbname):
    dbinfo = Dbinfo.query.filter_by(dbname=dbname).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = dbinfo.alarm_logs.order_by(Alarm_log.create_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    alarm_logs = pagination.items
    return render_template('dbsummary.html',dbinfos=[dbinfo],alarm_logs=alarm_logs,pagination=pagination)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
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
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/add-db', methods=['GET', 'POST'])
@login_required
def add_dbinfo():
    dbinfo = Dbinfo()
    form = EditDbinfoForm(dbinfo)
    if form.validate_on_submit():
        dbinfo = Dbinfo(dbname=form.dbname.data,
                        true_ip=form.true_ip.data,
                        port=form.port.data,
                        instance_name=form.instance_name.data,
                        schema_name=form.schema_name.data,
                        dbtype=Dbtype.query.get(form.db_type.data)
                        )
        db.session.add(dbinfo)
        db.session.commit
        flash('A new db  has been added.')
        return redirect(url_for('.dbsinfo'))
    return render_template('edit_dbinfo.html', form=form, dbinfo=dbinfo)


@main.route('/edit-dbinfo/<int:db_id>', methods=['GET', 'POST'])
@login_required
def edit_dbinfo(db_id):
    dbinfo = Dbinfo.query.get_or_404(db_id)
    form = EditDbinfoForm(dbinfo=dbinfo)
    if form.validate_on_submit():
        dbinfo.dbname = form.dbname.data
        dbinfo.true_ip = form.true_ip.data
        dbinfo.port = form.port.data
        dbinfo.instance_name = form.instance_name.data
        dbinfo.schema_name = form.schema_name.data
        dbinfo.dbtype = Dbtype.query.get(form.db_type.data)
        db.session.add(dbinfo)
        flash('The dbinfo has been updated.')
        return redirect(url_for('.dbsinfo'))
    form.dbname.data = dbinfo.dbname
    form.true_ip.data = dbinfo.true_ip[0]
    form.port.data = dbinfo.port
    form.instance_name.data = dbinfo.instance_name
    form.schema_name.data = dbinfo.schema_name
    form.db_type.data = dbinfo.db_type_id
    return render_template('edit_dbinfo.html', form=form, dbinfo=dbinfo)


@main.route('/chart/<int:db_id>')
def chart(db_id):
    '''
    connect_nums = Check_connect_num_log.query.filter_by(db_id=db_id).all()
    data = jsonify({'connect_nums': [connect_num.to_json() for connect_num in connect_nums]})
    '''
    num = db.session.execute('select check_time,connect_num from check_connect_num_logs where db_id=6')
    ones = [[time.mktime(i[0].timetuple()), i[1]] for i in num.fetchall()]
    print (ones)
    return render_template('chart.html', data=json.dumps(ones))


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<dbname>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(dbname):
    dbinfo = Dbinfo.query.filter_by(dbname=dbname).first()
    if dbinfo is None:
        flash('Invalid db.')
        return redirect(url_for('.index'))
    if current_user.is_following(dbinfo):
        flash('You are already following this db.')
        return redirect(url_for('.dbsummary', dbname=dbname))
    current_user.follow(dbinfo)
    flash('You are now following %s.' % username)
    return redirect(url_for('.dbsummary', dbname=dbname))


@main.route('/unfollow/<dbname>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(dbname):
    dbinfo = Dbinfo.query.filter_by(dbname=dbname).first()
    if dbinfo is None:
        flash('Invalid db.')
        return redirect(url_for('.index'))
    if not current_user.is_following(dbinfo):
        flash('You are not following this user.')
        return redirect(url_for('.dbsummary', dbname=dbname))
    current_user.unfollow(dbinfo)
    flash('You are not following %s anymore.' % dbname)
    return redirect(url_for('.dbsummary', dbname=dbname))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.ASSIGNED_DB)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.ASSIGNED_DB)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.ASSIGNED_DB)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
