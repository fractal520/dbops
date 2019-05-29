url_config = {
    'g3': 'oracle+cx_oracle://dbmgr:Yypp8msc@10.1.5.165:1521/KM',
    'vip': 'oracle+cx_oracle://dbmgr:Yypp8msc@10.1.5.160:1521/kmvip',
    'scrm': 'mysql+pymysql://dbmon:dbmon1234@10.1.5.143/baihui'}

sql_config = {
    'SUBFHD_LSH_OLD': '''
select distinct ticketno from (
select subbh || lsh  as ticketno from GZDBO.subfhd
 union all
select subbh || lsh  as ticketno from PNDBO.subfhd
 union all
select subbh || lsh  as ticketno from SZDBO.subfhd)
--where rownum<10
order by ticketno''',

    'SUBFHD_DH_OLD': '''
select distinct bookid from (
select subbh || dh  as bookid from GZDBO.subfhd
 union all
select subbh || dh  as bookid from PNDBO.subfhd
 union all
select subbh || dh  as bookid from SZDBO.subfhd)
--where rownum<10
order by bookid''',

    'SUBFHD_LSH': '''
select distinct ticketno from (
select subbh || lsh  as ticketno from GZDBO.subfhd
 where jzrq >= to_date('2016-01-01','yyyy-mm-dd')
   and jzrq < to_date('2017-10-12','yyyy-mm-dd')
   and sl <> 0
 union all
select subbh || lsh  as ticketno from PNDBO.subfhd
 where jzrq >= to_date('2016-01-01','yyyy-mm-dd')
   and jzrq < to_date('2017-10-12','yyyy-mm-dd')
   and sl <> 0
 union all
select subbh || lsh  as ticketno from SZDBO.subfhd
 where jzrq >= to_date('2016-01-01','yyyy-mm-dd')
   and jzrq < to_date('2017-10-12','yyyy-mm-dd')
   and sl <> 0)
--where rownum<10
order by ticketno''',

    'SUBFHD_DH': '''
select distinct bookid from (
select subbh || dh  as bookid from GZDBO.subfhd
 where jzrq >= to_date('2016-01-01','yyyy-mm-dd')
   and jzrq < to_date('2017-10-12','yyyy-mm-dd')
   and sl <> 0
 union all
select subbh || dh  as bookid from PNDBO.subfhd
 where jzrq >= to_date('2016-01-01','yyyy-mm-dd')
   and jzrq < to_date('2017-10-12','yyyy-mm-dd')
   and sl <> 0
 union all
select subbh || dh  as bookid from SZDBO.subfhd
 where jzrq >= to_date('2016-01-01','yyyy-mm-dd')
   and jzrq < to_date('2017-10-12','yyyy-mm-dd')
   and sl <> 0)
--where rownum<10
order by bookid''',

    'SUBFHD_NAME': '''
select distinct  lsh as name from (
select lsh , jzrq from GZDBO.subfhd where jzrq >= to_date('2017-03-01','yyyy-mm-dd')
 union all
select lsh , jzrq  from PNDBO.subfhd where jzrq >= to_date('2017-03-01','yyyy-mm-dd')
 union all
select lsh , jzrq from SZDBO.subfhd where jzrq >= to_date('2017-03-01','yyyy-mm-dd'))
order by lsh''',

    'SUBFHD_ARG_A2009': '''
select distinct dh as ARG_A2009 from (
select dh , jzrq from GZDBO.subfhd where jzrq >= to_date('2017-03-01','yyyy-mm-dd')
 union all
select dh , jzrq  from PNDBO.subfhd where jzrq >= to_date('2017-03-01','yyyy-mm-dd')
 union all
select dh , jzrq from SZDBO.subfhd where jzrq >= to_date('2017-03-01','yyyy-mm-dd'))
order by dh''',

    'KM_MEMBER_CONSUMEHEAD': '''
select distinct TICKETNO from kmvip.KM_MEMBER_CONSUMEHEAD
--where rownum<10
order by TICKETNO''',

    'KM_MEMBER_CONSUME': '''
select distinct BOOKID from kmvip.KM_MEMBER_CONSUME order by BOOKID''',

    'BH_CUSTOM_MODULE_1': '''
select distinct name from bh_custom_module_1
 where ARG_A2001 in (70,1562,86) and arg_a5002>= date('2017-03-01')
 order by name''',

    'BH_CUSTOM_MODULE_2': '''
select distinct ARG_A2009 from bh_custom_module_2
 where ARG_A2010 in (70,1562,86)
   and arg_a5002 > date('2017-03-01')
 order by ARG_A2009'''}
