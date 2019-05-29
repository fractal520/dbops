import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


Base = declarative_base()
conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()


class Ip_address(Base):
    __tablename__ = 'ip_addresses'
    ip_id = sa.Column(sa.Integer, primary_key=True)
    ip_address= sa.Column(INTEGER(display_width=11, unsigned=True))
    instances = relationship('Instance', backref='ip_address', lazy='dynamic')
    hosts = relationship('Host', backref='ip_address', lazy='dynamic')

    @property
    def true_ip(self):
        return session.query(sa.func.INET_NTOA(Ip_address.ip_address)).filter_by(ip_id=self.ip_id).first()[0]

    @true_ip.setter
    def true_ip(self, true_ip):
        self.ip_address = session.query(sa.func.INET_ATON(true_ip)).first()[0]


class Host(Base):
    __tablename__ = 'hosts'
    host_id = sa.Column(sa.Integer, primary_key=True)
    host_name = sa.Column(sa.String(100))
    host_ip_id = sa.Column(sa.Integer, sa.ForeignKey('ip_addresses.ip_id'))
    instances = relationship('Instance', backref='host', lazy='dynamic')


class Dbinst_role(Base):
    __tablename__ = 'dbinst_roles'
    dbinst_role_id = sa.Column(sa.SmallInteger, primary_key=True)
    db_type_id = sa.Column(sa.Integer, sa.ForeignKey('dbtypes.db_type_id'))
    dbinst_role_name = sa.Column(sa.String(100))
    specify_role_instes = relationship('Instance', backref='inst_role', lazy='dynamic')


class Instance(Base):
    __tablename__ = 'instances'
    instance_id = sa.Column(sa.Integer, primary_key=True)
    instance_name = sa.Column(sa.String(100))
    access_ip_id = sa.Column(sa.Integer, sa.ForeignKey('ip_addresses.ip_id'))
    access_port = sa.Column(sa.Integer)
    dbinst_role_id = sa.Column(sa.SmallInteger, sa.ForeignKey('dbinst_roles.dbinst_role_id'))
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))
    host_id = sa.Column(sa.Integer, sa.ForeignKey('hosts.host_id'))


class Dbtype(Base):
    __tablename__ = 'dbtypes'
    db_type_id = sa.Column(sa.Integer, primary_key=True)
    db_type_name = sa.Column(sa.String(20), unique=True, nullable=False)
    specify_type_dbs = relationship('Dbinfo', backref='dbtype', lazy='dynamic')
    specify_type_arches = relationship('Db_arch', backref='dbtype', lazy='dynamic')


class Db_arch(Base):
    __tablename__ = 'db_arches'
    db_arch_id = sa.Column(sa.SmallInteger, primary_key=True)
    db_type_id = sa.Column(sa.Integer, sa.ForeignKey('dbtypes.db_type_id'))
    db_arch_name = sa.Column(sa.String(100))
    specify_arch_dbs = relationship('Dbinfo', backref='db_arch', lazy='dynamic')


class Dbinfo(Base):
    __tablename__ = 'dbinfos'
    db_id = sa.Column(sa.Integer, primary_key=True)
    dbname = sa.Column(sa.String(100))
    db_type_id = sa.Column(sa.Integer, sa.ForeignKey('dbtypes.db_type_id'))
    db_arch_id = sa.Column(sa.SmallInteger, sa.ForeignKey('db_arches.db_arch_id'))
    add_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    instances = relationship('Instance', backref='dbinfo', lazy='dynamic')
    alarm_logs = relationship('Alarm_log', backref='dbinfo', lazy='dynamic')
    alarm_thresholds = relationship('Alarm_threshold', backref='dbinfo', lazy='dynamic')
    schemas = relationship('Db_schema', backref='dbinfo', lazy='dynamic')

    def __repr__(self):
        return '<Dbinfo %r>' % self.dbname


class Db_schema(Base):
    __tablename__ = 'db_schemas'
    schema_id = sa.Column(sa.Integer, primary_key=True)
    schema_name = sa.Column(sa.String(100))
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))


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
    class_of_log = sa.Column(sa.String(50))
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
