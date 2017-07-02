from datetime import datetime
import sys
import math
from initmon import check_func_dict, alarm_thrd_dict, alarm_level_dict
from alarm import decide_alarm, proc_alarm


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


async def check_oracle_connectivity(self):
    try:
        print(self.get_url)
        # await asyncio.sleep(3)
        conn = await self.get_conn
        await conn.execute('select 1 from dual')
        print('%s connect ok.' % self.dbname)
        return {'db_id': self.db_id, 'status': 'success', 'check_time': datetime.utcnow()}
    except Exception as e:
        print(e)
        return {'db_id': self.db_id, 'status': 'failure', 'check_time': datetime.utcnow()}
    finally:
        print('%s connectivity is checked \n' % self.dbname)


async def check_other_connectivity(self):
    print(self.get_url)
    print('%s: the db type %s do not support check connectivity' % (self.dbname,self.db_type))


async def check_mysql_connect_num(self):
    try:
        print(self.get_url)
        # await asyncio.sleep(3)
        conn = await self.get_conn
        result = await conn.execute('select count(*) from information_schema.processlist union select @@global.max_connections')
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


async def check_oracle_connect_num(self):
    try:
        print(self.get_url)
        # await asyncio.sleep(3)
        conn = await self.get_conn
        sql = "select count(*) from v$process union select to_number(display_value) from v$parameter where name = 'processes'"
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


async def check_other_connect_num(self):
    print(self.get_url)
    print('%s: the db type %s do not support check connect nums' % (self.dbname, self.db_type))
