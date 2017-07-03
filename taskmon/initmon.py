import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict
from dbmodels import Dbinfo, Dbtype, Check_item, Alarm_threshold, Alarm_level
from alarm_message import alarm_message
from check_instruction import check_instruction


conn = sa.create_engine('mysql+pymysql://opr:Opr*1234@127.0.0.1/dbops')
Session = sessionmaker(bind=conn)
session = Session()


dbs = session.query(Dbinfo)
# dbs = session.query(Dbinfo).filter_by(dbname='mysql2')
db_types = session.query(Dbtype).all()
alarm_levels = session.query(Alarm_level).order_by(Alarm_level.level_id).all()
check_items = session.query(Check_item).all()
thresholds = session.query(Alarm_threshold).all()


check_item_dict = {}
check_func_dict = {}
check_insn_dict = {}
alarm_level_dict = OrderedDict()
#alarm_thrd_dict = defaultdict(lambda: (True, 0.01))
alarm_thrd_dict = {}
alarm_msg_dict = {}
db_type_dict = {}


for check_item in check_items:

    if check_item.check_name == 'connectivity':
        alarm_msg_dict[check_item.check_id] = alarm_message['connectivity']
        check_func_dict[check_item.check_id] = 'check_connectivity'
        check_func_dict['check_connectivity'] = check_item.check_id

    elif check_item.check_name == 'connect_num':
        alarm_msg_dict[check_item.check_id] = alarm_message['connect_num']
        check_func_dict[check_item.check_id] = 'check_connect_num'
        check_func_dict['check_connect_num'] = check_item.check_id

    else:
        pass

    check_item_dict[check_item.check_id] = (check_item.check_name, check_item.active, check_item.frequency)


for db_type in db_types:
    db_type_dict[db_type.db_type_id] = db_type.db_type_name


for check_item in check_items:
    for db_type in db_types:

        if check_item.check_name == 'connectivity':
            if db_type.db_type_name == 'mysql':
                check_insn_dict[(check_item.check_id, db_type.db_type_id)] = check_instruction[('connectivity', 'mysql')]
            elif db_type.db_type_name == 'oracle':
                check_insn_dict[(check_item.check_id, db_type.db_type_id)] = check_instruction[('connectivity', 'oracle')]
            else:
                pass

        elif check_item.check_name == 'connect_num':
            if db_type.db_type_name == 'mysql':
                check_insn_dict[(check_item.check_id, db_type.db_type_id)] = check_instruction[('connect_num', 'mysql')]
            elif db_type.db_type_name == 'oracle':
                check_insn_dict[(check_item.check_id, db_type.db_type_id)] = check_instruction[('connect_num', 'oracle')]
            else:
                pass


for lev in alarm_levels:
    alarm_level_dict[lev.level_id] = lev.level_name


for thrd in thresholds:
    alarm_thrd_dict[(thrd.db_id, thrd.check_id, thrd.level_id)] = (thrd.active, thrd.threshold)


class DbTypeError(ValueError):
    pass
