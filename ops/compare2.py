# -*- coding: utf-8 -*-
#弹出列表左边的n个元素
def mulitpop(list, n):
    while n:
        list.pop(0)
        n = n-1
    return list

#对有序列表进行去重
def dedup(order_list):
    #n为添加到目标列表中元素的个数减1
    n = 0
    rlist=[]
    #将源列表最左边元素弹出，添加到目标列表中
    rlist.append(order_list.pop(0))
    while order_list:
        l = order_list.pop(0)
        #如果源列表最左边的元素等于目标列表最后一个元素，则跳过
        if l == rlist[n]:
            continue
        rlist.append(l)
        n = n+1
    return rlist

#对比有序（递增）且元素唯一的两个列表,返回在source中却不在target中的元素
def tabcompare(source, target):
    n = 0
    with open('result.txt', 'w') as f:
        for s in source:
            for t in target:
                print('compare {} and {}'.format(s, t))
                '''当target中还有元素时，记录下对应source中的元素，这样当target中的元素
                   遍历完后，可以知道source遍历到了哪一个元素'''
                s_last_deal = s
                #因为两个列表都是递增的，所以如果s小于t,表示s不在target中，并跳出内层循环
                if s < t:
                    f.write(str(s))
                    f.write('\n')
                    break
                #s等于t，元素在两个列表中都存在
                if s == t:
                    #在单次外层循环中，内层循环循环的次数
                    n = n + 1
                    print('target pop {} numbers'.format(n))
                    #弹出target中的前n个元素
                    target = mulitpop(target, n)
                    #弹出后重置n的记数，并跳出内层循环
                    n = 0
                    break
                #s大于t，比较s和内层循环中的下一个元素
                else:
                    #在单次外层循环中，内层循环循环的次数
                    n = n + 1
                    continue
        print('s_last_deal is {}'.format(s_last_deal))
        #source中剩余的没有比较的元素，它们都比target中的元素要大
        source = source[source.index(s_last_deal)+1:]
        for s in source:
            f.write(str(s))
            f.write('\n')


def main(source, target):
    print(source)
    print(target)
    source = dedup(source)
    target = dedup(target)
    print(source)
    print(target)
    tabcompare(source, target)


if __name__ == '__main__':
    source = [1, 2, 2,      5,    7, 8, 8, 9, 10, 12, 14]
    target = [   2,   3, 4, 5, 5, 7, 8, 8,        12]
    main(source, target)
