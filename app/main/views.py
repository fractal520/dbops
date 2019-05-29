from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, EditDbinfoForm, EditInstForm, EditHostForm, EditSchemaForm
from .. import db
from .. import models
from ..models import Permission, Role, User, Post, Comment, Alarm_log, Dbinfo,\
    Dbtype, Check_item, Dbinst_role, Instance, Db_arch, Ip_address, Host, Db_schema
from ..decorators import admin_required, permission_required
import json
import time
from datetime import datetime

def nvl(var1, var2):
    if not var1:
        return var2
    else:
        return var1


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


@main.route('/databases/')
def databases():
    dbinfos = Dbinfo.query.order_by(Dbinfo.add_time.desc()).all()
    return render_template('dbinfo.html', dbinfos=dbinfos)


@main.route('/instances/')
def instances():
    dbinfos = Dbinfo.query.order_by(Dbinfo.add_time.desc()).all()
    return render_template('instance.html', dbinfos=dbinfos)


@main.route('/dbinfo/<instance_name>')
def dbinfo(instance_name):
    dbinfo = Dbinfo.query.filter_by(instacne_name=instance_name).first_or_404()
    return render_template('dbinfo.html', dbinfos=[dbinfo])


@main.route('/edit_alarm/<id>')
def edit_alarm(instance_name):
    dbinfo = Dbinfo.query.filter_by(instance_name=instance_name).first_or_404()
    return render_template('dbinfo.html', dbinfo=dbinfo)


@main.route('/db_alarm/<dbname>')
def dbsummary(dbname):
    dbinfo = Dbinfo.query.filter_by(dbname=dbname).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = dbinfo.alarm_logs.order_by(Alarm_log.create_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    alarm_logs = pagination.items
    return render_template('dbsummary.html', dbinfos=[dbinfo], alarm_logs=alarm_logs, pagination=pagination)


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
    EditDbinfoForm.add_inst.__dict__['kwargs']['default'] = True
    form = EditDbinfoForm(dbinfo)
    if form.validate_on_submit():
        dbinfo = Dbinfo(dbname=form.dbname.data,
                        dbtype=Dbtype.query.get(form.db_type.data),
                        db_arch=Db_arch.query.get(form.db_arch.data)
                        )
        db.session.add(dbinfo)
        db.session.commit
        flash('A new db  has been added.')
        if form.add_inst.data:
            db_id = Dbinfo.query.filter_by(dbname=form.dbname.data).first().db_id
            return redirect(url_for('.add_inst', db_id=db_id))
        return redirect(url_for('.databases'))
    return render_template('edit_dbinfo.html', form=form, dbinfo=dbinfo)


@main.route('/edit-dbinfo/<int:db_id>', methods=['GET', 'POST'])
@login_required
def edit_dbinfo(db_id):
    dbinfo = Dbinfo.query.get_or_404(db_id)
    EditDbinfoForm.add_inst.__dict__['kwargs']['default'] = False
    form = EditDbinfoForm(dbinfo=dbinfo)
    if form.validate_on_submit():
        dbinfo.dbname = form.dbname.data
        dbinfo.dbtype = Dbtype.query.get(form.db_type.data)
        dbinfo.db_arch = Db_arch.query.get(form.db_arch.data)
        db.session.add(dbinfo)
        flash('The dbinfo has been updated.')
        if form.add_inst.data:
            return redirect(url_for('.add_inst', db_id=db_id))
        return redirect(url_for('.databases'))
    form.dbname.data = dbinfo.dbname
    form.db_type.data = dbinfo.db_type_id
    form.db_arch.data = dbinfo.db_arch_id
    return render_template('edit_dbinfo.html', form=form, dbinfo=dbinfo)


@main.route('/add-inst', methods=['GET', 'POST'])
@login_required
def add_inst():
    db_id = request.args.get('db_id', type=int)
    inst = Instance()
    form = EditInstForm(inst)
    if form.validate_on_submit():
        host_ip_addr = nvl(
            Ip_address.query.filter_by(ip_address=db.session.query(
                db.func.INET_ATON(form.host_ip.data)).first()[0]).first(),
            Ip_address(true_ip=form.host_ip.data))
        host = nvl(
            Host.query.filter_by(host_name=form.host_name.data).first(),
            Host(host_name=form.host_name.data))
        host.ip_address = host_ip_addr
        if form.inst_ip.data:
            inst_ip_addr = nvl(
                Ip_address.query.filter_by(ip_address=db.session.query(
                    db.func.INET_ATON(form.inst_ip.data)).first()[0]).first(),
                Ip_address(true_ip=form.inst_ip.data))
        else:
            inst_ip_addr = host_ip_addr
        inst = Instance(instance_name=form.instance_name.data,
                        dbinst_role=Dbinst_role.query.get(
                            form.dbinst_role.data),
                        ip_address=inst_ip_addr,
                        access_port=form.access_port.data,
                        db_id=db_id,
                        host=host
                        )
        db.session.add(host_ip_addr)
        db.session.add(host)
        db.session.add(inst_ip_addr)
        db.session.add(inst)
        db.session.commit
        flash('A new instance  has been added.')
        if form.cont_add.data:
            return redirect(url_for('.add_inst', db_id=db_id))
        return redirect(url_for('.instances'))
    return render_template('edit_instance.html', form=form, inst=inst)


@main.route('/edit-dbinst/<int:inst_id>', methods=['GET', 'POST'])
@login_required
def edit_dbinst(inst_id):
    inst = Instance.query.get_or_404(inst_id)
    form = EditInstForm(inst=inst)
    if form.validate_on_submit():
        host_ip_addr = nvl(
            Ip_address.query.filter_by(ip_address=db.session.query(
                db.func.INET_ATON(form.host_ip.data)).first()[0]).first(),
            Ip_address(true_ip=form.host_ip.data))
        host = nvl(
            Host.query.filter_by(host_name=form.host_name.data).first(),
            Host(host_name=form.host_name.data))
        host.ip_address = host_ip_addr
        inst_ip_addr = nvl(
            Ip_address.query.filter_by(ip_address=db.session.query(
                db.func.INET_ATON(form.inst_ip.data)).first()[0]).first(),
            Ip_address(true_ip=form.inst_ip.data))
        inst.instance_name = form.instance_name.data
        inst.dbinst_role = Dbinst_role.query.get(form.dbinst_role.data)
        inst.access_port = form.access_port.data
        inst.host = host
        inst.ip_address = inst_ip_addr
        db.session.add(host_ip_addr)
        db.session.add(host)
        db.session.add(inst_ip_addr)
        db.session.add(inst)
        flash('The instance has been updated.')
        return redirect(url_for('.instances'))
    form.instance_name.data = inst.instance_name
    form.dbinst_role.data = inst.dbinst_role_id
    form.host_name.data = inst.host.host_name
    form.host_ip.data = inst.host.ip_address.true_ip
    form.inst_ip.data = inst.ip_address.true_ip
    form.access_port.data = inst.access_port
    return render_template('edit_instance.html', form=form, inst=inst)


@main.route('/hosts/', methods=['GET', 'POST'])
@login_required
def hosts():
    hosts = Host.query.order_by(Host.host_id.desc()).all()
    return render_template('host.html', hosts=hosts)


@main.route('/edit-host/<int:host_id>', methods=['GET', 'POST'])
@login_required
def edit_host(host_id):
    host = Host.query.get_or_404(host_id)
    form = EditHostForm()
    if form.validate_on_submit():
        host_ip_addr = nvl(
            Ip_address.query.filter_by(ip_address=db.session.query(
                db.func.INET_ATON(form.host_ip.data)).first()[0]).first(),
            Ip_address(true_ip=form.host_ip.data))
        host.ip_address = host_ip_addr
        host.host_name = form.host_name.data
        db.session.add(host_ip_addr)
        db.session.add(host)
        flash('The host has been updated.')
        return redirect(url_for('.hosts'))
    form.host_name.data = host.host_name
    form.host_ip.data = host.ip_address.true_ip
    return render_template('edit_host.html', form=form)


@main.route('/schemas/', methods=['GET', 'POST'])
@login_required
def schemas():
    dbinfos = Dbinfo.query.order_by(Dbinfo.add_time.desc()).all()
    return render_template('schema.html', dbinfos=dbinfos)


@main.route('/add-schema/<int:db_id>', methods=['GET', 'POST'])
@login_required
def add_schema(db_id):
    db_schema = Db_schema()
    form = EditSchemaForm()
    if form.validate_on_submit():
        db_schema = Db_schema(schema_name=form.schema_name.data,
                           db_id=db_id)
        db.session.add(db_schema)
        db.session.commit
        flash('A new db\'s schema has been added.')
        return redirect(url_for('.schemas'))
    return render_template('edit_schema.html', form=form, db_schema=db_schema)


@main.route('/edit-schema/<int:schema_id>', methods=['GET', 'POST'])
@login_required
def edit_schema(schema_id):
    db_schema = Db_schema.query.get_or_404(schema_id)
    form = EditSchemaForm()
    if form.validate_on_submit():
        db_schema.schema_name = form.schema_name.data
        db.session.add(db_schema)
        flash('The db\'s schema has been updated.')
        return redirect(url_for('.schemas'))
    form.schema_name.data = db_schema.schema_name
    return render_template('edit_schema.html', form=form, db_schema=db_schema)


@main.route('/chart/<int:check_id>/<int:db_id>')
def chart(check_id, db_id):
    return render_template('chart2.html', check_id=check_id, db_id=db_id)


@main.route('/chart/getdata')
def chart_get_data():
    check_id = request.args.get('check_id', type=int)
    db_id = request.args.get('db_id', type=int)
    check_item = Check_item.query.get_or_404(check_id)
    class_of_log = check_item.class_of_log
    check_name = check_item.check_name
    class_name = getattr(models, class_of_log)
    dbname = Dbinfo.query.get_or_404(db_id).dbname
    cur_time = datetime.utcnow()
    min_time = datetime(cur_time.year, cur_time.month, cur_time.day, 0, 0, 0)
    nums = class_name.get_history(db_id=db_id, min_time=min_time)
    if nums:
        max_num = max([num.max_num for num in nums])
    else:
        max_num = None
    dataset = {
        'check_name': check_name,
        'dbname': dbname,
        'max_num': max_num,
        'data': [[time.mktime(num.check_time.timetuple()) * 1000,
                  num.connect_num] for num in nums]}
    json_data = json.dumps({'datasets': [dataset]})
    return (json_data)


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
    flash('You are now following %s.' % dbname)
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
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
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
