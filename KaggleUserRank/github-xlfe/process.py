import datetime
import sys

#drop = ['competitions', 'status', 'prize', 'title', 'results', 'best-submission',
#        'final-rank', 'last-submission', 'final-score', 'entries', 'public-score',
#        'team', 'public-rank', 'teams']

input_header = ['competitions', 'status', 'prize', 'title', 'lbconds', 'results', 'best-submission',
                'final-rank', 'last-submission', 'final-score', 'entries', 'public-score', 'team',
                'public-rank', 'teams', 'start_dt', 'end_dt']

output_header = ['competitions','title','prize','teams','comp-days','team','entries','after-best','final-rank','rank-chg','public-score','final-score']

print ','.join(output_header)

h = sys.stdin.readline()[:-1].split(',')

h.extend(['after-best','comp-days','rank-chg'])

def str_to_dt(date):
    #     Thu 06 Sep 2012 16:54:03
    fmt = '%a %d %b %Y %H:%M:%S'
    return datetime.datetime.strptime(date,fmt)

def str_to_d(date):
    #     Friday September 07 2012
    fmt = '%A %B %d %Y'
    return datetime.datetime.strptime(date,fmt)

for line in sys.stdin.readlines():
    c = line[:-1].split(',')

    try:
	    prize = int(c[h.index('prize')][1:])
    except:
	    continue

    after_best = int((str_to_dt(c[h.index('last-submission')]) - str_to_dt(c[h.index('best-submission')])).total_seconds())

    comp_days = int((str_to_d(c[h.index('end_dt')]) - str_to_d(c[h.index('start_dt')])).days)
    pr = c[h.index('public-rank')]
    fr = c[h.index('final-rank')]

    if pr != '' and fr != '':
        rank_chg = int(c[h.index('public-rank')]) - int(c[h.index('final-rank')])
    else:
        rank_chg = ''

    t = h.index('teams')
    c[t] = c[t].split(' ')[0]

    p = h.index('prize')
    c[p] = c[p][1:]

    c.extend([after_best,comp_days,rank_chg])

    output = []
    for o in output_header:
        output.append(c[h.index(o)])

    print ','.join(str(i) for i in output)






