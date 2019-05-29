import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime
from config import url_config, sql_config


def tab(dbname, tabname):
    url = url_config[dbname]
    sql = sql_config[tabname]

    conn = sa.create_engine(url, poolclass=NullPool)
    Session = sessionmaker(bind=conn)
    session = Session()

    print('{} begin execute sql in {}'.format(datetime.now(), dbname))
    sql_execute = session.execute(sql)
    print('{} begin fectch {}\'s results'.format(datetime.now(), tabname))
    result = sql_execute.fetchall()
    print('{} the {}.{} nums is {}, the min is {}, the max is {}'.format(
        datetime.now(), dbname, tabname, len(result), result[0], result[-1]))

    return result
