#import asyncio


async def check_mysql_connectivity(self):
    try:
        print(self.get_url)
        #await asyncio.sleep(3)
        conn = await self.get_conn
        await conn.execute('select user()')
        print('%s connect ok.' % self.dbname)
    except Exception as e :
        print(e)
        print('%s connect fault.' % self.dbname)
    finally:
        print('%s is checked \n' % self.dbname)


async def check_oracle_connectivity(self):
    try:
        print(self.get_url)
        #await asyncio.sleep(3)
        conn = await self.get_conn
        await conn.execute('select 1 from dual')
        print('%s connect ok.' % self.dbname)
    except Exception as e :
        print(e)
        print('%s connect fault.' % self.dbname)
    finally:
        print('%s is checked \n' % self.dbname)


async def check_other_connectivity(self):
    print(self.get_url)
    print('%s by passed ' % self.dbname)


async def check_mysql_connect_nums(self):
    try:
        print(self.get_url)
        #await asyncio.sleep(3)
        conn = await self.get_conn
        result = await conn.execute('select count(*) from information_schema.processlist')
        connect_nums = await result.fetchone()
        connect_nums = connect_nums[0]
        print('%s connect num is %s.' % (self.dbname, connect_nums))
    except Exception as e :
        print(e)
        print('%s connect fault.' % self.dbname)
    finally:
        print('%s is checked \n' % self.dbname)


async def check_oracle_connect_nums(self):
    try:
        print(self.get_url)
        #await asyncio.sleep(3)
        conn = await self.get_conn
        result = await conn.execute('select count(*) from v$process')
        connect_nums = await result.fetchone()
        connect_nums = connect_nums[0]
        print('%s connect num is %s.' % (self.dbname, connect_nums))
    except Exception as e :
        print(e)
        print('%s connect fault.' % self.dbname)
    finally:
        print('%s is checked \n' % self.dbname)


async def check_other_connect_nums(self):
    print(self.get_url)
    print('%s by passed ' % self.dbname)
