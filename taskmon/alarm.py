from string import Template
from alarm_message import alarm_message
from initmon import check_item_dict, alarm_thrd_dict, alarm_level_dict
from dbmodels import Alarm_log

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from datetime import datetime


conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()


def decide_alarm(db_id, check_id, percent):
    alarm_level = 0
    for lev in alarm_level_dict.keys():
        print(db_id,check_id,lev)
        alarm_thrd = alarm_thrd_dict[(db_id, check_id, lev)]
        print ('aaa:'+str(alarm_thrd))
        if (alarm_thrd[0] and (percent >= alarm_thrd[1])):
            alarm_level = lev
            break
    return alarm_level


async def proc_alarm(db_id, dbname, check_id, level_id, alarm_value, max_value):
    item_name = check_item_dict[check_id][0]
    level_name = alarm_level_dict[level_id]
    msg = Template(alarm_message.get(item_name))
    percent = round(alarm_value / max_value, 2)
    message = msg.safe_substitute(level_name=level_name, dbname=dbname, connect_num=alarm_value, max_num=max_value, percent=percent)
    print(message)
    alarm_log = Alarm_log(db_id=db_id,
                          check_id=check_id,
                          level_id=level_id,
                          level_name=level_name,
                          alarm_message=message
                          )
    session.add(alarm_log)
    print(alarm_log)
    session.commit()

