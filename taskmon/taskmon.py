import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio
from pprint import pprint
from get_db import db_check_dict
from dbmodels import Check_connectivity_log, Check_connect_num_log
from operator import is_not
from functools import partial
from datetime import datetime
import pdb

Base = declarative_base()
conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()

'''
class Foo:
    def bar1(self):
        print 1
    def bar2(self):
        print 2

def callMethod(o, name):
    getattr(o, name)()


f = Foo()
callMethod(f, "bar1")
'''

def check_task():
    check_connectivity = asyncio.gather(*[asyncio.ensure_future(db_check.check_connectivity()) for db_check in db_check_dict.values()])

    check_connect_num = asyncio.gather(*[asyncio.ensure_future(db_check.check_connect_num()) for db_check in db_check_dict.values()])

    check_task = asyncio.gather(check_connectivity, check_connect_num)
    return check_task


def task_result(results):
    print('The results of the inspection task:\n')
    pprint(results)

    check_connectivity_list = results[0]
    check_connectivity_list = filter(partial(is_not, None), check_connectivity_list)

    check_connect_num_list = results[1]
    check_connect_num_list = filter(partial(is_not, None), check_connect_num_list)

    print('check:')
    print(list(check_connectivity_list))
    print(list(check_connect_num_list))
    pdb.set_trace()
    session.bulk_insert_mappings(Check_connectivity_log, list(check_connectivity_list))
    pdb.set_trace()
    session.bulk_insert_mappings(Check_connect_num_log, list(check_connect_num_list))

    '''
    session.bulk_save_objects([Check_connectivity_log(**kw) for kw in check_connectivity_list if kw is not None])

    session.bulk_save_objects([Check_connect_num_log(**kw) for kw in check_connect_num_list if kw is not None])
    '''
    aa=session.execute('select * from Check_connect_num_logs where to_days(check_time) = to_days(now())')
    for a in aa:
        print(a)
    session.commit()
    print('session inserted')


def run_task():
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(check_task())
        task_result(results)
        print('task complete')
        loop.close


if __name__ == '__main__':
    # while True:
        run_task()
