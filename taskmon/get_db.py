import os
from types import MethodType
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY
from check_func import *
from initmon import dbs
# import asyncio


os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'


class Db_check(object):
    def __init__(self, db_id, dbname, username, password, ip, port, instance_name, schema_name, db_type):
        self.db_id = db_id
        self.dbname = dbname
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port
        self.instance_name = instance_name
        self.schema_name = schema_name
        self.db_type = db_type

    @property
    def get_url(self):
        if self.db_type == 'mysql':
            url = 'mysql+pymysql://' + self.username + ':' + self.password + '@' + str(self.ip[0]) + ':' + str(self.port) + '/' + self.schema_name
        elif self.db_type == 'oracle':
            url = 'oracle+cx_oracle://' + self.username + ':' + self.password + '@' + str(self.ip[0]) + ':' + str(self.port) + '/' + self.instance_name
        else:
            url = 'mysql+pymysql://' + self.username + ':' + self.password + '@' + str(self.ip[0]) + ':' + str(self.port) + '/' + self.schema_name
        return url

    @property
    async def get_conn(self):
        engine = create_engine(self.get_url, strategy=ASYNCIO_STRATEGY)
        return await engine.connect()

    def __repr__(self):
        return '<db_check  %r>' % self.dbname


db_check_dict = {}
for db_item in dbs:
    db_check = Db_check(db_id=db_item.db_id, dbname=db_item.dbname, username='dbmon', password='dbmon', ip=db_item.true_ip, port=db_item.port, instance_name=db_item.instance_name, schema_name=db_item.schema_name, db_type=db_item.db_type)

    if db_check.db_type == 'mysql':
        db_check.connectivity = MethodType(check_mysql_connectivity, db_check)
        db_check.connect_num = MethodType(check_mysql_connect_num, db_check)

    elif db_check.db_type == 'oracle':
        db_check.connectivity = MethodType(check_oracle_connectivity, db_check)
        db_check.connect_num = MethodType(check_oracle_connect_num, db_check)

    else:
        db_check.connectivity = MethodType(check_other_connectivity, db_check)
        db_check.connect_num = MethodType(check_other_connect_num, db_check)

    db_check_dict[db_check.db_id] = db_check


