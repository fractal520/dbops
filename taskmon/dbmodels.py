import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


Base = declarative_base()
conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()


class Dbinfo(Base):
    __tablename__ = 'dbinfos'
    db_id = sa.Column(sa.Integer, primary_key=True)
    dbname = sa.Column(sa.String(100))
    ip = sa.Column(INTEGER(display_width=11, unsigned=True))
    port = sa.Column(sa.Integer)
    instance_name = sa.Column(sa.String(100))
    schema_name = sa.Column(sa.String(100))
    db_type_id = sa.Column(sa.Integer, sa.ForeignKey('dbtypes.db_type_id'))
    add_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    alarm_logs = relationship('Alarm_log', backref='dbinfo', lazy='dynamic')
    alarm_thresholds = relationship('Alarm_threshold', backref='dbinfo', lazy='dynamic')

    @property
    def true_ip(self):
        return session.query(sa.func.INET_NTOA(Dbinfo.ip)).filter_by(db_id=self.db_id).first()

    @true_ip.setter
    def true_ip(self, true_ip):
        self.ip = session.query(sa.func.INET_ATON(true_ip)).first()[0]

    def __repr__(self):
        return '<Dbinfo %r>' % self.dbname


class Dbtype(Base):
    __tablename__ = 'dbtypes'
    db_type_id = sa.Column(sa.Integer, primary_key=True)
    db_type_name = sa.Column(sa.String(20), unique=True, nullable=False)
    specify_type_dbs = relationship('Dbinfo', backref='dbtype', lazy='dynamic')


class Alarm_level(Base):
    __tablename__ = 'alarm_levels'
    level_id = sa.Column(sa.Integer, primary_key=True)
    level_name = sa.Column(sa.String(20))
    level_desc = sa.Column(sa.Text)
    alarm_logs = relationship('Alarm_log', backref='alarm_level', lazy='dynamic')
    alarm_thresholds = relationship('Alarm_threshold', backref='alarm_level', lazy='dynamic')


class Alarm_log(Base):
    __tablename__ = 'alarm_logs'
    id = sa.Column(sa.Integer, primary_key=True)
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))
    alarm_message = sa.Column(sa.Text)
    level_name = sa.Column(sa.String(20))
    level_id = sa.Column(sa.Integer, sa.ForeignKey('alarm_levels.level_id'))
    check_id = sa.Column(sa.Integer, sa.ForeignKey('check_items.check_id'))
    create_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    status = sa.Column(sa.SmallInteger, default=2)
    finish_time = sa.Column(sa.DateTime)


class Check_connectivity_log(Base):
    __tablename__ = 'check_connectivity_logs'
    id = sa.Column(sa.Integer, primary_key=True)
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))
    status = sa.Column(sa.String(20))
    check_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)


class Check_connect_num_log(Base):
    __tablename__ = 'check_connect_num_logs'
    id = sa.Column(sa.Integer, primary_key=True)
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))
    connect_num = sa.Column(sa.Integer)
    max_num = sa.Column(sa.Integer)
    check_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)


class Check_item(Base):
    __tablename__ = 'check_items'
    check_id = sa.Column(sa.Integer, primary_key=True)
    check_name = sa.Column(sa.String(100))
    frequency = sa.Column(sa.SmallInteger)
    active = sa.Column(sa.Boolean, default=True)
    description = sa.Column(sa.Text)
    alarm_logs = relationship('Alarm_log', backref='check_item', lazy='dynamic')
    alarm_thresholds = relationship('Alarm_threshold', backref='check_item', lazy='dynamic')


class Alarm_threshold(Base):
    __tablename__ = 'alarm_thresholds'
    id = sa.Column(sa.Integer, primary_key=True)
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))
    check_id = sa.Column(sa.Integer, sa.ForeignKey('check_items.check_id'))
    level_id = sa.Column(sa.Integer, sa.ForeignKey('alarm_levels.level_id'))
    threshold = sa.Column(sa.Numeric(3, 2))
    active = sa.Column(sa.Boolean, default=True)
