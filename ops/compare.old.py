def tabcompare(source, target):
    s_last_deal = 0
    n = 0
    with open('result.txt', 'w') as f:
        for s in source:
            for t in target:
                print('compare {} and {}'.format(s, t))
                s_last_deal = s
                if s < t:
                    f.write(str(s))
                    f.write('\n')
                    break
                if s == t:
                    n = n + 1
                    target = target[n:]
                    n = 0
                    break
                else:
                    n = n + 1
                    continue
        print(s_last_deal)
        source = source[source.index(s_last_deal)+1:]
        for s in source:
            f.write(str(s))
            f.write('\n')


if __name__ == '__main__':
    source = [1, 2,       5, 7, 8, 10, 12, 14]
    target = [   2, 3, 4, 5, 7, 8,     12]
    tabcompare(source, target)
