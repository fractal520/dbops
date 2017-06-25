from get_db import db_check_dict
import asyncio


db_list = []
task_list = []


async def check_task(check_db):
    try:
        await check_db.connectivity()
        await check_db.connect_nums()
    except Exception as e:
        print(e)
        print('%s connect fault.' % check_db.dbname)
    finally:
        print('%s is checked \n' % check_db.dbname)

if __name__ == '__main__':
    for check_db in db_check_dict.values():
        db_list.append(check_db)
        task_list.append(check_task(check_db))

    print(db_list,task_list)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(task_list))
    loop.close()

