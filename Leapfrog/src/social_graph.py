from get_leaderboards import get_leaderboards
from get_team_users   import get_team_users
from itertools import izip
from math import isnan

GDF_OUTFILE = '../data/social_graph.gdf'

def team_name_str(tid): return 'team_'+str(tid)
def user_name_str(uid): return 'user_'+str(uid)
def to_ascii(s):        return s.decode('ascii', errors='ignore')
def enquote(s):         return '"' + s + '"' 

teams = set()
users = set()
edges = set() # (team_id, user_id)

team_users_table = get_team_users()
leaderboards     = get_leaderboards()
team_name_table = {}

for lb_name, lb_data in leaderboards:
    lb_data = lb_data.reset_index()
    for team_id, team_name in izip(lb_data['TeamId'], lb_data['TeamName']):
        team_name_table[team_id] = enquote(to_ascii(str(team_name)))
        team_users = team_users_table[team_id]
        if len(team_users) > 1: # use only 'true' teams with >1 person 
            for team_user in team_users:
                users.add(team_user)
                edge = (team_id, team_user)
                edges.add(edge) 
            teams.add(team_id)
            print lb_name, team_id, team_name, len(team_users), team_users
    print

print 'teams:', len(teams)
print 'users:', len(users)
print 'edges:', len(edges)

RECTANGLE = str(1)
ELLIPSE = str(2)
RED    = "'255,0,0'"
TOMATO = "'255,99,71'"
BLUE   = "'0,0,255'"
LIGHT_BLUE  = "'135,206,250'"

WHITE = "'255,255,255'"

node_defs = ['nodedef> name VARCHAR, label VARCHAR, color VARCHAR' ]
for user in sorted(users):
    node_defs.append(','.join([ user_name_str(user), user_name_str(user), LIGHT_BLUE]))
for team in sorted(teams):
    t_name = to_ascii(team_name_table[team])
    # t_name = team_name_str(team)
    print [team_name_str(team), t_name, RED ]
    node_defs.append(','.join([ team_name_str(team), t_name, TOMATO]))
    #node_defs.append(team_name_table(team) +','+ RED)

edge_defs = ['edgedef> node1, node2, color VARCHAR']
for edge in sorted(edges):
    team, user = edge
    edge_defs.append( ','.join([team_name_str(team), user_name_str(user), WHITE]) )

fout = open(GDF_OUTFILE,'w')
for node_def in node_defs:
    fout.write(node_def+'\n')
for edge_def in edge_defs:
    fout.write(edge_def+'\n')
fout.close()
print 'Wrote graph to:', GDF_OUTFILE



# .GDF format needs:
# nodedef> name, style 
# team_12345, 1
# team_4567,  2
# edgedef> node1,node2
# team_12345,team_4567
#
