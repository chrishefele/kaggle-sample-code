import lxml.html as LH
import json
import sys

def get_text(doc,xpth):
    s = ''.join( doc.xpath(xpth + '//text()') ).strip()
    return s

def get_competitions(print_comps=False):

    sys.stderr.write('Downloading and parsing competition list\n')
    comp_idx = LH.parse('http://www.kaggle.com/competitions')
    comp_links = set( 'http://www.kaggle.com' + s if s[0] == '/' else s for s in comp_idx.xpath("//div[@class='competition-details']//a/@href"))
    leaderboard_links = [l + '/leaderboard' for l in comp_links]

    sys.stderr.write('{0} competitions identified\n'.format(len(leaderboard_links)))

    if print_comps:
        i=0
        for l in leaderboard_links:
            print 'wget -O comp_{0} {1}'.format(i,l)
            print 'wget -O comp_{0}_public {1}/public'.format(i,l)
            i +=1

    return leaderboard_links

def parse_comp(doc):

    try:
        prize,teams = get_text(doc,"//div[@id='comp-header-stats-prize']").split(u'\u2022')
    except:
        sys.stderr.write('Unable to parse competition\n')
        return None

    comp = {
            'title':    get_text(doc,"//div[@id='comp-header-details']/h1")
        ,   'status':   get_text(doc,"//div[@id='comp-header-stats-teams']")
        ,   'start_dt': get_text(doc,"//div[@id='comp-header-stats-start']")
        ,   'end_dt':   get_text(doc,"//div[@id='comp-header-stats-end']")
        ,   'prize':    prize.strip()
        ,   'teams':    teams.strip()
        ,   'lbconds':  get_text(doc,"//div[@id='leadeboard-conditions']")
    }

    #only look at Finished comps
    if comp['status'].lower() != "finished":
        sys.stderr.write('Skipping {0}, not finished\n'.format(comp['title']))
        return None

    return comp

def parse_results(doc):
    rows = doc.xpath("//table[@id='leaderboard-table']//tr")

    results = []

    header = rows.pop(0).getchildren()
    try:
        if header[3].text_content().strip() != 'Score':
            sys.stderr.write('Score not found in header...\n')
            return None
    except:
        return None

    for row in rows:

        r = row.getchildren()

        try:
            e = r[5].find('abbr').get('title')
            ls, bs = e.split('\r\n')
            ls = ls.strip()[17:42]
            bs = bs.strip()[17:42]
        except:
            ls = r[5].text_content().strip()
            bs = ''

        if 'class' not in row.attrib:
            row_items = {
                    'final-rank'            : r[0].text_content()
                ,   'team'                  : r[2].text_content().strip().split('\r\n')[0].encode('ascii','ignore')
                ,   'final-score'           : r[3].text_content().strip().replace(',','')
                ,   'entries'               : r[4].text_content().strip()
                ,   'last-submission'       : ls
                ,   'best-submission'       : bs
            }
        else:
            bm = r[3].text_content().strip()
            row_items = {
                    'final-score'             :float(bm.replace(',',''))
                ,   'team'                    :r[2].text_content().strip().split('\r\n')[0]
                ,   'final-rank'              :None
            }

        results.append(row_items)
    return results

def append_results(private_file,results):

    public_results = parse_results(LH.parse(private_file + '/public'))

    if public_results is None:
        sys.stderr.write('No public results found for {0}\n'.format(private_file))
        return

    team_details = {}

    for r in public_results:
        team_details[r['team']] = {
                'public-score'      :r['final-score']
            ,   'public-rank'       :r['final-rank']
            }

    for r in results:
        if r['team'] in team_details:
            for k,v in team_details[r['team']].iteritems():
                r[k] = v

comps = []
leaderboard_links =get_competitions()

for l in leaderboard_links:
#for l in ['./_data/comp_'+ str(i) for i in range(0,76)]:

    try:
        doc = LH.parse(l)
    except:
        sys.stderr.write('Unable to open {0}\n'.format(l))
        continue

    comp = parse_comp(doc)

    if comp:
        results = parse_results(doc)
        if not results:
            sys.stderr.write('No results found in {0}\n'.format(l))
            continue
        append_results(l,results)
        comp['results'] = results
        comps.append(comp)
        sys.stderr.write('Comp details scraped {0}\n'.format(comp['title']))
    else:
        sys.stderr.write('Skipping {0}\n'.format(l))
        #to see which competitions are skipped, uncomment below line and run
        #$ python scrape.py | grep _data/dl_list | bash
        #print 'grep -m1 ' + l.split('/')[2] + ' _data/dl_list'
        pass

print json.dumps(comps,indent=1)
