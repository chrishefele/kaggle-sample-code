import pandas
import StringIO
import os
import dateutil
import numpy as np

PUBLIC_LEADERBOARD_DIR  = '../download/ALL_LEADERBOARDS/' 

def get_leaderboards():
    leaderboards = []
    for fname in sorted(os.listdir(PUBLIC_LEADERBOARD_DIR)):

        fname_root = os.path.splitext(fname)[0]
        path_fname = os.path.join(PUBLIC_LEADERBOARD_DIR, fname)
        print 'Reading:', path_fname

        # Example file lines below (and note leading spaces in col names): 
        # TeamId, TeamName, SubmissionDate, Score
        # 5085,"All 1's Benchmark",6/28/2011 2:41:39 PM,1.513011
        to_ascii = lambda s: s.decode('ascii', errors='ignore')
        converters = {' SubmissionDate':dateutil.parser.parse, ' TeamName': to_ascii} 
        lb = pandas.read_csv(path_fname, converters=converters)

        # Remove leading spaces on col names, remove null submissions & null leaderboards
        lb.columns = [col_name.strip() for col_name in lb.columns] 
        lb = lb[lb['Score']!=0] 
        if len(lb)==0:          
            continue

        # Determine how to rank leaderboard scores (bigger score = good or bad?)
        lb1 = lb.groupby('TeamId').agg(lambda lb: lb.sort('SubmissionDate')[-1:].values[0])
        lb0 = lb.groupby('TeamId').agg(lambda lb: lb.sort('SubmissionDate')[0:1].values[0])
        lb1['FirstScore'] = lb0['Score']
        user_scores_ascending = np.all(np.logical_not(lb1['Score'] < lb1['FirstScore']))
        leaderboard_ascending = not user_scores_ascending
        lb1 = lb1.sort('Score', ascending=leaderboard_ascending)
        lb1['Rank'] = range(1, len(lb1)+1)

        leaderboards.append((fname_root, lb1))
    return leaderboards
