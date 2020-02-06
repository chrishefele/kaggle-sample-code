import pandas
from itertools import izip
from collections import defaultdict

USER_NAMES_FILE = '../download/user_location_and_software.csv'

"""
Id,DisplayName,Country,City,Software
"62","Administrator","Australia","",""
"368","Anthony Goldbloom (Kaggle)","Australia","Melbourne",""
"387","Nicholas Gruen","Australia","Sydney",""
"""

def get_user_names():
    df = pandas.read_csv(USER_NAMES_FILE)
    uids   = df['Id']
    unames = df['DisplayName']
    user_names = {}
    for uid, uname in izip(uids, unames):
        user_names[int(uid)] = uname.decode('ascii', errors='ignore')
    return user_names

if __name__=='__main__':
    
    unames = get_user_names()
    for uid in unames:
        print uid, unames[uid]
