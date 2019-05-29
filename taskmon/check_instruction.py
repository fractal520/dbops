check_instruction = {
    ('connect_num', 'mysql'): '''
        select count(*) from information_schema.processlist
         union
        select @@global.max_connections
        ''',
    ('connect_num', 'oracle'): '''
        select count(*) from v$process
         union
        select to_number(display_value) from v$parameter
         where name = 'processes'
    ''',
    ('connectivity', 'mysql'): 'select user()',
    ('connectivity', 'oracle'): 'select 1 from dual',
    ('fra usage', 'oracle'): '''
        select sum(PERCENT_SPACE_USED)/100 from v$flash_recovery_area_usage
        '''
}
