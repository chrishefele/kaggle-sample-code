import pandas
from itertools import izip
from collections import defaultdict

TEAM_FILE = '../download/teams.csv'

def get_team_users():
    team_users = defaultdict(list)
    df = pandas.read_csv(TEAM_FILE)
    tids = df['TeamId']
    uids = df['UserId']
    for tid, uid in izip(tids, uids):
        team_users[tid].append(uid)
    return team_users

