import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from collections import defaultdict, OrderedDict
from dbmodels import Dbinfo, Check_item, Alarm_threshold, Alarm_level


conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()


# dbs = session.query(Dbinfo)
dbs = session.query(Dbinfo).filter_by(dbname='mysql2')
alarm_levels = session.query(Alarm_level).order_by(Alarm_level.level_id.desc()).all()
check_items = session.query(Check_item).all()
thresholds = session.query(Alarm_threshold).all()


check_item_dict = {}
check_func_dict = {}
alarm_level_dict = OrderedDict()
alarm_thrd_dict = defaultdict(lambda: (True, 0.01))


for check_item in check_items:

    if check_item.check_name == 'connectivity':
        check_func_dict[check_item.check_id] = 'connectivity'
        check_func_dict['check_oracle_connectivity'] = check_item.check_id
        check_func_dict['check_mysql_connectivity'] = check_item.check_id
        check_func_dict['check_other_connectivity'] = check_item.check_id

    elif check_item.check_name == 'connect_num':
        check_func_dict[check_item.check_id] = 'connect_num'
        check_func_dict['check_oracle_connect_num'] = check_item.check_id
        check_func_dict['check_mysql_connect_num'] = check_item.check_id
        check_func_dict['check_other_connect_num'] = check_item.check_id

    else:
        pass

    check_item_dict[check_item.check_id] = (check_item.check_name, check_item.active, check_item.frequency)


for lev in alarm_levels:
    alarm_level_dict[lev.level_id] = lev.level_name


for thrd in thresholds:
    alarm_thrd_dict[(thrd.db_id, thrd.check_id, thrd.alarm_level)] = (thrd.active, thrd.threshold)
