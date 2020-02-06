from get_leaderboards import get_leaderboards
from get_team_users   import get_team_users
from get_user_names   import get_user_names
import itertools

GDF_OUTFILE = '../data/user_user_graph.gdf'

RED         = "'255,0,0'"
TOMATO      = "'255,99,71'"
BLUE        = "'0,0,255'"
LIGHT_BLUE  = "'135,206,250'"
KAGGLE_BLUE = "'32,190,255'"
WHITE       = "'255,255,255'"

def user_name_str(uid): 
    return 'user_'+str(uid)

def enquote(s):
    return '"' + s + '"'

users = set() # user_id
edges = set() # (user_id_min, user_id_max)
team_users_table = get_team_users()
user_name_table  = get_user_names()
leaderboards     = get_leaderboards()

for lb_name, lb_data in leaderboards:
    lb_data = lb_data.reset_index()
    for team_id in lb_data['TeamId']:
        team_users = team_users_table[team_id]
        if len(team_users) > 1: # use only 'true' teams with >1 person 
            print 'contest:', lb_name, 'team:', team_id, '#users:', 
            print len(team_users), 'user_ids:', team_users
            for team_user in team_users:
                users.add(team_user)
            for user_pair in itertools.combinations(team_users,2):
                user_pair = tuple(sorted(user_pair))
                edges.add(user_pair) 
    print

print '#users:', len(users)
print '#edges:', len(edges)

node_defs = ['nodedef> name VARCHAR, label VARCHAR, color VARCHAR' ]
for user in sorted(users):
    u_id_str = user_name_str(user)
    u_name   = user_name_str(user) + ' ' + user_name_table.get(user, '')
    print "node_def:", u_id_str, u_name
    node_defs.append(','.join([ u_id_str, enquote(u_name), KAGGLE_BLUE]))

edge_defs = ['edgedef> node1, node2, color VARCHAR']
for edge in sorted(edges):
    user1, user2 = edge
    edge_defs.append( ','.join([user_name_str(user1), user_name_str(user2), WHITE]) )

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
