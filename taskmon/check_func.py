from datetime import datetime
import sys
import math
from initmon import check_func_dict, alarm_thrd_dict, alarm_level_dict,\
    check_insn_dict, db_type_dict
from alarm import decide_alarm, proc_alarm
from initmon import DbTypeError

'''
async def check_mysql_connectivity(self):
    try:
        print(self.get_url)
        # await asyncio.sleep(3)
        conn = await self.get_conn
        await conn.execute('select user()')
        print('%s connect ok.' % self.dbname)
        return {'db_id': self.db_id, 'status': 'success', 'check_time': datetime.utcnow()}
    except Exception as e:
        print(e)
        print('%s connect ok.' % self.dbname)
        return {'db_id': self.db_id, 'status': 'failure', 'check_time': datetime.utcnow()}
    finally:
        print('%s connectivity is checked \n' % self.dbname)
'''


async def check_connectivity(self):
    try:
        # await asyncio.sleep(3)
        print('beging check_connectivity')
        status = 'failure'
        #print('fun name is:{}'.format(sys._getframe().f_code.co_name))
        #print('check_func_dict is {}'.format(check_func_dict))
        check_id = check_func_dict[sys._getframe().f_code.co_name]
        #print('check_id is {}'.format(check_id))
        conn = await self.get_conn
        print(conn)
        #print('self.db_type_id is {}'.format(self.db_type_id))
        sql = check_insn_dict[(check_id, self.db_type_id)]
        #print('sql is :{}'.format(sql))
        await conn.execute(sql)
        status = 'success'
        print('%s connect ok.' % self.dbname)
        return {'db_id': self.db_id, 'status': status, 'check_time': datetime.utcnow()}

    except KeyError as e:
        print('%s: the db type %s do not support check connectivity' % (self.dbname, db_type_dict[self.db_type_id]))
        print(e)
    except DbTypeError as e:
        print(e)
    except Exception as e:
        print(e)
        if status == 'failure':
            ratio = 1
            level_id = decide_alarm(self.db_id, check_id, ratio)
            proc_alarm(self.db_id, self.dbname, check_id, level_id)
        return {'db_id': self.db_id, 'status': status, 'check_time': datetime.utcnow()}

    finally:
        print('%s connectivity is checked \n' % self.dbname)


'''
async def check_mysql_connect_num(self):
    try:
        print(self.get_url)
        # await asyncio.sleep(3)
        conn = await self.get_conn
        sql =
              select count(*) from information_schema.processlist
               union
              select @@global.max_connections

        result = await conn.execute(sql)
        nums = await result.fetchall()
        connect_num = nums[0][0]
        max_num = nums[1][0]
        percent = round(connect_num / max_num, 2)
        print(percent)
        check_id = check_func_dict[sys._getframe().f_code.co_name]
        level_id = decide_alarm(self.db_id, check_id, percent)
        print (level_id)
        if level_id:
            await proc_alarm(self.db_id, self.dbname, check_id, level_id, connect_num, max_num)
        print('%s connect num is %s, max num is %s.' % (self.dbname, connect_num, max_num))
        return {'db_id': self.db_id, 'connect_num': connect_num, 'check_time': datetime.utcnow()}
    except Exception as e:
        print(e)
    finally:
        print('%s connect_nums is checked \n' % self.dbname)
'''


async def check_connect_num(self):
    try:
        print(self.get_url)
        # await asyncio.sleep(3)
        conn = await self.get_conn
        check_id = check_func_dict[sys._getframe().f_code.co_name]
        print(check_id)
        print(self.db_type_id)
        sql = check_insn_dict[(check_id, self.db_type_id)]
        result = await conn.execute(sql)
        nums = await result.fetchall()
        connect_num = nums[0][0]
        max_num = nums[1][0]
        ratio = round(connect_num / max_num, 2)
        print(ratio)
        level_id = decide_alarm(self.db_id, check_id, ratio)
        print (level_id)
        if level_id:
            proc_alarm(self.db_id, self.dbname, check_id, level_id, connect_num, max_num)
        print('%s connect num is %s, max num is %s.' % (self.dbname, connect_num, max_num))
        return {'db_id': self.db_id, 'connect_num': connect_num, 'max_num': max_num, 'check_time': datetime.utcnow()}

    except KeyError as e:
        print('%s: the db type %s do not support check connect nums' % (self.dbname, db_type_dict[self.db_type_id]))
    except Exception as e:
        print(e)

    finally:
        print('%s connect_nums is checked \n' % self.dbname)


async def check_fra_usage(self):
    try:
        print('begin check fra usage')
        conn = await self.get_conn
        check_id = check_func_dict[sys._getframe().f_code.co_name]
        sql = check_insn_dict[(check_id, self.db_type_id)]
        print('check_fra_usage sql: %s' % sql)
        result = await conn.execute(sql)
        print('check_fra_usage result: %s' % result)
        usage_tp = await result.fetchone()
        print('check_fra_usage usage_tp: %s' % usage_tp)
        usage = usage_tp[0]
        print('check_fra_usage usage: %s' % usage)
        level_id = decide_alarm(self.db_id, check_id, usage)
        print(level_id)
        if level_id:
            proc_alarm(self.db_id, self.dbname, check_id, level_id, usage)
        print('%s fra usage is %s.' % (self.dbname, usage))

    except KeyError as e:
        print('%s: the db type %s do not support check fra usage.' % (self.dbname, db_type_dict[self.db_type_id]))
    except Exception as e:
        print(e)

    finally:
        print('%s fra usage is checked \n' % self.dbname)

