from datetime import datetime
from compare import main
from tab import tab

g3_result = tab('g3', 'SUBFHD_DH')
vip_result = tab('vip', 'KM_MEMBER_CONSUME')
# scrm_result = tab('scrm', 'BH_CUSTOM_MODULE_2')
list_g3 = [t[0] for t in g3_result]
# list_scrm = [t[0] for t in scrm_result]
list_vip = [t[0] for t in vip_result]
main(list_g3, list_vip)
print('{} done !'.format(datetime.now()))
