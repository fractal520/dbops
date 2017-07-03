from string import Template
from alarm_message import alarm_message
from initmon import check_item_dict, alarm_thrd_dict, alarm_level_dict, alarm_msg_dict
from dbmodels import Alarm_log

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from datetime import datetime


conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()


def decide_alarm(db_id, check_id, ratio):
    alarm_level = 0
    print(alarm_thrd_dict)
    for lev in alarm_level_dict.keys():
        if (db_id, check_id, lev) in alarm_thrd_dict:
            print(''.join((str(db_id), str(check_id), str(lev))) +
                  'in alarm_thrd_dict')
            alarm_thrd = alarm_thrd_dict[(db_id, check_id, lev)]
        else:
            print(''.join((str(db_id), str(check_id), str(lev))) +
                  'not in alarm_thrd_dict')
            if lev < len(alarm_level_dict):
                continue
            elif lev == len(alarm_level_dict):
                alarm_thrd = (True, 0.01)
        print ('aaa:' + str(alarm_thrd))
        if (alarm_thrd[0] and (ratio >= alarm_thrd[1])):
            alarm_level = lev
            break
    return alarm_level


def proc_alarm(db_id, dbname, check_id, level_id, alarm_value=1, max_value=1):
    print('#######livel_id#######' + str(level_id))
    level_name = alarm_level_dict[level_id]
    msg = Template(alarm_msg_dict[check_id])
    ratio = round(alarm_value / max_value, 2)
    message = msg.safe_substitute(dbname=dbname, connect_num=alarm_value, max_num=max_value, percent=ratio)
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

