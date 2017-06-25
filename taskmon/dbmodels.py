import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.orm import sessionmaker, relationship, backref
from datetime import datetime


Base = declarative_base()
conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()

class Dbinfo(Base):
    __tablename__ = 'dbinfos'
    db_id = sa.Column(sa.Integer, primary_key=True)
    dbname = sa.Column(sa.String(100))
    ip = sa.Column(INTEGER(display_width=11,unsigned = True))
    port = sa.Column(sa.Integer)
    instance_name = sa.Column(sa.String(100))
    schema_name = sa.Column(sa.String(100))
    db_type = sa.Column(sa.String(20), sa.ForeignKey('dbtypes.db_type_name'))
    add_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    monitor_logs = relationship('Monitor_log',backref='dbinfo',lazy='dynamic')

    @property
    def true_ip(self):
        return session.query(sa.func.INET_NTOA(Dbinfo.ip)).filter_by(db_id=self.db_id).first()

    @true_ip.setter
    def true_ip(self,true_ip):
        self.ip = session.query(sa.func.INET_ATON(true_ip)).first()[0]

    def __repr__(self):
        return '<Dbinfo %r>' % self.dbname


class Dbtype(Base):
    __tablename__ = 'dbtypes'
    db_type_id = sa.Column(sa.Integer, primary_key=True)
    db_type_name = sa.Column(sa.String(20),unique=True,nullable=False)
    specify_type_dbs = relationship('Dbinfo',backref='dbtype',lazy='dynamic')


class Monitor_level(Base):
    __tablename__ = 'monitor_levels'
    level_id = sa.Column(sa.Integer, primary_key=True)
    level_name = sa.Column(sa.String(20))
    level_desc = sa.Column(sa.Text)


class Monitor_log(Base):
    __tablename__ = 'monitor_logs'
    id = sa.Column(sa.Integer, primary_key=True)
    db_id = sa.Column(sa.Integer, sa.ForeignKey('dbinfos.db_id'))
    monitor_log = sa.Column(sa.Text)
    monitor_level_name = sa.Column(sa.String(20))
    level_id = sa.Column(sa.Integer, sa.ForeignKey('monitor_levels.level_id'))
    create_time = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    status = sa.Column(sa.SmallInteger)
    finish_time = sa.Column(sa.DateTime)

dbs = session.query(Dbinfo)
#dbs = session.query(Dbinfo).filter_by(dbname='mysql2')
