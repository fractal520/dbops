from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from sqlalchemy.dialects.mysql.base import INTEGER
from . import db, login_manager


class Permission:
    '''
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08

    ADMINISTER = 0x80
    '''
    FOLLOW = 0x01
    DEAL_MONITOR = 0x02
    EDIT_DBINFO = 0x04
    DIAGNOSE = 0x08
    ASSIGNED_DB = 0x10
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.DEAL_MONITOR |
                     Permission.EDIT_DBINFO |
                     Permission.DIAGNOSE, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.DEAL_MONITOR |
                          Permission.EDIT_DBINFO |
                          Permission.DIAGNOSE |
                          Permission.ASSIGNED_DB, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'),
                      primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    # posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed_db = db.relationship('Follow',
                                  foreign_keys=[Follow.follower_id],
                                  backref=db.backref('follower_user', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')
    '''

    '''
    # comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    '''
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
    '''
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        # self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, dbinfo):
        if not self.is_following(dbinfo):
            f = Follow(follower_user=self, followed_db=dbinfo)
            db.session.add(f)

    def unfollow(self, dbinfo):
        f = self.followed_db.filter_by(db_id=dbinfo.db_id).first()
        if f:
            db.session.delete(f)

    def is_following(self, dbinfo):
        return self.followed_db.filter_by(
            db_id=dbinfo.db_id).first() is not None
    '''

    '''
    @property
    def followed_alarm_logs(self):
        return Alarm_log.query.join(Follow, Follow.db_id == Alarm_log.db_id).filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Ip_address(db.Model):
    __tablename__ = 'ip_addresses'
    ip_id = db.Column(db.Integer, primary_key=True)
    ip_address= db.Column(INTEGER(display_width=11, unsigned=True))
    instances = db.relationship('Instance', backref='ip_address', lazy='dynamic')
    hosts = db.relationship('Host', backref='ip_address', lazy='dynamic')

    @property
    def true_ip(self):
        return db.session.query(db.func.INET_NTOA(Ip_address.ip_address)).filter_by(ip_id=self.ip_id).first()[0]

    @true_ip.setter
    def true_ip(self, true_ip):
        self.ip_address = db.session.query(db.func.INET_ATON(true_ip)).first()[0]


class Host(db.Model):
    __tablename__ = 'hosts'
    host_id = db.Column(db.Integer, primary_key=True)
    host_name = db.Column(db.String(100))
    host_ip_id = db.Column(db.Integer, db.ForeignKey('ip_addresses.ip_id'))
    instances = db.relationship('Instance', backref='host', lazy='dynamic')


class Dbinst_role(db.Model):
    __tablename__ = 'dbinst_roles'
    dbinst_role_id = db.Column(db.SmallInteger, primary_key=True)
    db_type_id = db.Column(db.Integer, db.ForeignKey('dbtypes.db_type_id'))
    dbinst_role_name = db.Column(db.String(100))
    specify_role_instes = db.relationship('Instance', backref='dbinst_role', lazy='dynamic')


class Instance(db.Model):
    __tablename__ = 'instances'
    instance_id = db.Column(db.Integer, primary_key=True)
    instance_name = db.Column(db.String(100))
    access_ip_id = db.Column(db.Integer, db.ForeignKey('ip_addresses.ip_id'))
    access_port = db.Column(db.Integer)
    dbinst_role_id = db.Column(db.SmallInteger, db.ForeignKey('dbinst_roles.dbinst_role_id'))
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'))
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.host_id'))


class Dbtype(db.Model):
    __tablename__ = 'dbtypes'
    db_type_id = db.Column(db.Integer, primary_key=True)
    db_type_name = db.Column(db.String(20), unique=True, nullable=False)
    specify_type_dbs = db.relationship('Dbinfo', backref='dbtype', lazy='dynamic')
    specify_type_arches = db.relationship('Db_arch', backref='dbtype', lazy='dynamic')


class Db_arch(db.Model):
    __tablename__ = 'db_arches'
    db_arch_id = db.Column(db.SmallInteger, primary_key=True)
    db_type_id = db.Column(db.Integer, db.ForeignKey('dbtypes.db_type_id'))
    db_arch_name = db.Column(db.String(100))
    specify_arch_dbs = db.relationship('Dbinfo', backref='db_arch', lazy='dynamic')


class Dbinfo(db.Model):
    __tablename__ = 'dbinfos'
    db_id = db.Column(db.Integer, primary_key=True)
    dbname = db.Column(db.String(100))
    db_type_id = db.Column(db.Integer, db.ForeignKey('dbtypes.db_type_id'))
    db_arch_id = db.Column(db.SmallInteger, db.ForeignKey('db_arches.db_arch_id'))
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    instances = db.relationship('Instance', backref='dbinfo', lazy='dynamic')
    follower_users = db.relationship(
        'Follow',
        foreign_keys=[Follow.db_id],
        backref=db.backref('followed_db', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    alarm_logs = db.relationship('Alarm_log', backref='dbinfo', lazy='dynamic')
    alarm_thresholds = db.relationship('Alarm_threshold', backref='dbinfo', lazy='dynamic')
    schemas = db.relationship('Db_schema', backref='dbinfo', lazy='dynamic')

    def is_followed_by(self, user):
        return self.follower_users.filter_by(
            follower_id=user.id).first() is not None


class Db_schema(db.Model):
    __tablename__ = 'db_schemas'
    schema_id = db.Column(db.Integer, primary_key=True)
    schema_name = db.Column(db.String(100))
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'))


class Alarm_level(db.Model):
    __tablename__ = 'alarm_levels'
    level_id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(20))
    level_desc = db.Column(db.Text)
    alarm_logs = db.relationship('Alarm_log', backref='alarm_level', lazy='dynamic')
    alarm_thresholds = db.relationship('Alarm_threshold', backref='alarm_level', lazy='dynamic')


class Alarm_log(db.Model):
    __tablename__ = 'alarm_logs'
    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'))
    alarm_message = db.Column(db.Text)
    level_name = db.Column(db.String(20))
    level_id = db.Column(db.Integer, db.ForeignKey('alarm_levels.level_id'))
    check_id = db.Column(db.Integer, db.ForeignKey('check_items.check_id'))
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(db.SmallInteger, default=2)
    finish_time = db.Column(db.DateTime)


class Check_connectivity_log(db.Model):
    __tablename__ = 'check_connectivity_logs'
    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'))
    status = db.Column(db.String(20))
    check_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Check_connect_num_log(db.Model):
    __tablename__ = 'check_connect_num_logs'
    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'))
    connect_num = db.Column(db.Integer)
    max_num = db.Column(db.Integer)
    check_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @classmethod
    def get_history(cls, db_id, min_time):
        check_history = db.session.query(cls.check_time, cls.connect_num, cls.max_num).filter(cls.db_id == db_id, cls.check_time >= min_time).all()
        return check_history


class Check_item(db.Model):
    __tablename__ = 'check_items'
    check_id = db.Column(db.Integer, primary_key=True)
    check_name = db.Column(db.String(100))
    frequency = db.Column(db.SmallInteger)
    active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    class_of_log = db.Column(db.String(50))
    alarm_logs = db.relationship('Alarm_log', backref='check_item', lazy='dynamic')
    alarm_thresholds = db.relationship('Alarm_threshold', backref='check_item', lazy='dynamic')


class Alarm_threshold(db.Model):
    __tablename__ = 'alarm_thresholds'
    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('dbinfos.db_id'))
    check_id = db.Column(db.Integer, db.ForeignKey('check_items.check_id'))
    level_id = db.Column(db.Integer, db.ForeignKey('alarm_levels.level_id'))
    threshold = db.Column(db.Numeric(3, 2))
    active = db.Column(db.Boolean, default=True)
