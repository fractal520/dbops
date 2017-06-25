import os
from dbmodels import Dbinfo, dbs
from types import MethodType
from check_items import *
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY
#import asyncio


os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
db_check_dict = {}


class Db_check(object):
    def __init__(self,dbname,username,password,ip,port,instance_name,schema_name,db_type):
        self.dbname = dbname
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port
        self.instance_name = instance_name
        self.schema_name=schema_name
        self.db_type = db_type

    @property
    def get_url(self):
        if self.db_type == 'mysql':
            url = 'mysql+pymysql://'+self.username+':'+self.password+'@'+str(self.ip[0])+':'+str(self.port)+'/'+self.schema_name
        elif self.db_type == 'oracle':
            url = 'oracle+cx_oracle://'+self.username+':'+self.password+'@'+str(self.ip[0])+':'+str(self.port)+'/'+self.instance_name
        else:
            url = 'mysql+pymysql://'+self.username+':'+self.password+'@'+str(self.ip[0])+':'+str(self.port)+'/'+self.schema_name
        return url

    @property
    async def get_conn(self):
        engine = create_engine(self.get_url, strategy=ASYNCIO_STRATEGY)
        return await engine.connect()


    def __repr__(self):
        return '<db_check  %r>' % self.dbname


for db_item in dbs:
    db_check = Db_check(dbname=db_item.dbname, username='dbmon', password='dbmon', ip=db_item.true_ip, port=db_item.port, instance_name=db_item.instance_name, schema_name=db_item.schema_name, db_type=db_item.db_type)

    if db_check.db_type == 'mysql':
        db_check.connectivity = MethodType(check_mysql_connectivity,db_check)
        db_check.connect_nums = MethodType(check_mysql_connect_nums,db_check)

    elif db_check.db_type == 'oracle':
        db_check.connectivity = MethodType(check_oracle_connectivity,db_check)
        db_check.connect_nums = MethodType(check_oracle_connect_nums,db_check)

    else :
        db_check.connectivity = MethodType(check_other_connectivity,db_check)
        db_check.connect_nums = MethodType(check_other_connect_nums,db_check)

    db_check_dict[db_check.dbname] = db_check

