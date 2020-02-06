import pandas
import sys
import numpy as np
from itertools import izip

DOWNLOAD_DIR= '/home/chefele/kaggle/HHP/download/HHP_release3/'
FEATURES_DIR= '/home/chefele/kaggle/HHP/features/'

FILE_DIH_Y2 = DOWNLOAD_DIR + 'DaysInHospital_Y2.csv'       
FILE_DIH_Y3 = DOWNLOAD_DIR + 'DaysInHospital_Y3.csv'   
FILE_TARGET = DOWNLOAD_DIR + 'Target.csv'

FILE_MEMBERS= DOWNLOAD_DIR + 'Members.csv'
FILE_CLAIMS = DOWNLOAD_DIR + 'Claims.csv'     
FILE_LABS   = DOWNLOAD_DIR + 'LabCount.csv'
FILE_DRUGS  = DOWNLOAD_DIR + 'DrugCount.csv'

HASH_BINS           = 47
HASH_BINS_PCP       = HASH_BINS
HASH_BINS_VENDOR    = HASH_BINS
HASH_BINS_PROVIDERID= HASH_BINS

RANDOM_FEATURES     = 20 
RANDOM_SEED         = 42
np.random.seed(RANDOM_SEED)

# ========================================================================
# File/dataframe I/O routines
# ========================================================================

def read_csv_files(fnames):
    dfs = []
    for fname in fnames:
        print "Reading:",fname,'...',
        sys.stdout.flush()
        df = pandas.read_csv(fname)
        dfs.append(df)
        print 'Read', len(df),"rows"
        for col in df.columns:
            print '    %22s %7i unique_values' % (col, nuniq(df[col]))
        sys.stdout.flush()
        print
    return dfs

def alphanum_name(nm): return ''.join((c if c.isalnum() else '_' for c in nm))

def alphanum_cols(df): 
    df.columns = [alphanum_name(col_name) for col_name in df.columns]
    return df

def write_features(df, outfile):
    nrows, ncols = df.shape
    print 
    print "Preparing to write #rows:", nrows, "#cols:", ncols
    print "Writing features to:", outfile,"..."
    sys.stdout.flush()
    df = alphanum_cols(df)
    df.to_csv(outfile, na_rep = '0')  # TODO: change na_rep for better merge?
    print "Wrote features to:", outfile
    sys.stdout.flush()
    print "\nFeatures written (sorted):" 
    for n, col_name in enumerate(sorted(df.columns)):
        print "   ",n, col_name 
    print

# ========================================================================
# Functions to pre-process raw source data read from files
# ========================================================================

# use the 'hashing trick' for high-dimentional categorical variables
def hash_pcp(x):        return hash(x) % HASH_BINS_PCP
def hash_vendor(x):     return hash(x) % HASH_BINS_VENDOR
def hash_pid(x):        return hash(x) % HASH_BINS_PROVIDERID

class LookupTable:
    def __init__(self):

        self.age = {'0-9':5,   '10-19':15, '20-29':25, '30-39':35, '40-49':45,
                    '50-59':55,'60-69':65, '70-79':75, '80+':85,
                    'DEFAULT':45 
                   }

        self.dsfs= {'0- 1 month':1,  '1- 2 months':2,  '2- 3 months':3,    
                    '3- 4 months':4, '4- 5 months':5,  '5- 6 months':6,    
                    '6- 7 months':7, '7- 8 months':8,  '8- 9 months':9,   
                    '9-10 months':10,'10-11 months':11,'11-12 months':12,
                    'DEFAULT':6
                   }

        self.count={'1':1, '2':2,  '3':3, '4':4, '5':5,   '6':6, 
                    '7':7, '7+':7, '8':8, '9':9, '10+':10,
                    'DEFAULT':2
                   }

        self.los = {'1 day' :1,        '2 days':2,     '3 days':3,     
                    '4 days':4,        '5 days':5,     '6 days':6, 
                    '1- 2 weeks':11,   '2- 4 weeks':21,'4- 8 weeks':42, 
                    '26+ weeks':180,
                    'DEFAULT':0
                   }

        self.charlson = { '0':0, '1-2':2, '3-4':4, '5+':6, 'DEFAULT':0  }

    def _nan_filter(self, x, table): 
        return table[x] if not pandas.isnull(x) else table['DEFAULT']

    def int_age(self, x):      return self._nan_filter(x, self.age  )
    def int_dsfs(self, x):     return self._nan_filter(x, self.dsfs )
    def int_count(self, x):    return self._nan_filter(x, self.count)
    def int_los(self, x):      return self._nan_filter(x, self.los  )
    def int_charlson(self, x): return self._nan_filter(x, self.charlson)


# ========================================================================
# Pre-processing of raw source data & augment with additional variables
# ========================================================================

def maxDSFSxDSFS(mbrIDs_, DSFSs_):
    mbrIDs = mbrIDs_.tolist()
    DSFSs  = DSFSs_.fillna(value=0).tolist()
    assert len(mbrIDs) == len(DSFSs)
    mbr_maxDSFS = {}
    for mbrID, DSFS in izip(mbrIDs, DSFSs):
        if mbrID not in mbr_maxDSFS:
            mbr_maxDSFS[mbrID] = 0
        mbr_maxDSFS[mbrID] = max(mbr_maxDSFS[mbrID], DSFS)
    maxDSFSs = (mbr_maxDSFS[mbrID] for mbrID in mbrIDs)
    return [ '%02i-%02i' % (maxDSFS, DSFS) for maxDSFS, DSFS in izip(maxDSFSs, DSFSs)] 


def augment(members, claims, drugs, labs):

    print "Augmenting source data features"
    sys.stdout.flush()

    lut = LookupTable()

    members['int_AgeAtFirstClaim'] = members['AgeAtFirstClaim'].map(lut.int_age)

    claims['int_LengthOfStay' ] = claims[ 'LengthOfStay' ].map(lut.int_los)
    claims['int_CharlsonIndex'] = claims[ 'CharlsonIndex'].map(lut.int_charlson) 
    claims['int_DSFS'         ] = claims[ 'DSFS'         ].map(lut.dsfs)
    claims['int_ClaimDSFS'    ] = claims[ 'DSFS'         ].map(lut.dsfs)
    claims['ClaimDSFS'        ] = claims[ 'DSFS'         ]
    claims['ClaimYear'        ] = claims[ 'Year'         ]

    claims['hash_ProviderID'  ] = claims[ 'ProviderID'   ].map(hash_pid)
    claims['hash_Vendor'      ] = claims[ 'Vendor'       ].map(hash_vendor)
    claims['hash_PCP'         ] = claims[ 'PCP'          ].map(hash_pcp)

    claims['ClaimMaxDSFSxDSFS'] = maxDSFSxDSFS(claims['MemberID'], claims['int_ClaimDSFS'])

    drugs[ 'int_DrugCount'    ] = drugs[  'DrugCount'    ].map(lut.int_count) 
    drugs[ 'int_DSFS'         ] = drugs[  'DSFS'         ].map(lut.dsfs)
    drugs[ 'int_DrugDSFS'     ] = drugs[  'DSFS'         ].map(lut.dsfs)
    drugs[ 'DrugDSFS'         ] = drugs[  'DSFS'         ]
    drugs[ 'DrugYear'         ] = drugs[  'Year'         ]
    drugs[ 'usedDrugFlag'     ] = 1

    labs[  'int_LabCount'     ] = labs[   'LabCount'     ].map(lut.int_count) 
    labs[  'int_DSFS'         ] = labs[   'DSFS'         ].map(lut.dsfs)
    labs[  'int_LabDSFS'      ] = labs[   'DSFS'         ].map(lut.dsfs)
    labs[  'LabDSFS'          ] = labs[   'DSFS'         ]
    labs[  'LabYear'          ] = labs[   'Year'         ]
    labs[  'usedLabFlag'      ] = 1

    print "Done augmenting source data features\n"
    sys.stdout.flush()
    return members, claims, drugs, labs


# ========================================================================
# Functions to transform pre-processed source data into features 
# ========================================================================

def feature_func(df, col_name, func, prefix):
    # feature_func: applies function to col values on per-member id basis
    df1                    = df[['MemberID']]
    df1[prefix + col_name] = df[  col_name  ]
    grouped = df1.groupby('MemberID')
    return grouped.aggregate(func)

f_func = feature_func

def velocity(x):      return x[len(x)-1] - x[0]   # TODO: fix - key error
def f_velocity(df,c): return f_func(df, c, velocity, 'velocity_')

def nuniq(x):         return len(x.unique())
def f_nuniq(df, col): return f_func(df, col, nuniq,   'nuniq_')

def num(x):           return x.size 
def f_num(df, col):   return f_func(df, col, num,     'num_')

def f_sum(  df, col): return f_func(df, col, np.sum,  'sum_'  )
def f_mean( df, col): return f_func(df, col, np.mean, 'mean_' )
def f_max(  df, col): return f_func(df, col, np.amax, 'max_'  )
def f_max_notag(  df, col): 
                      return f_func(df, col, np.amax, ''      )
def f_min(  df, col): return f_func(df, col, np.amin, 'min_'  )
def f_std(  df, col): return f_func(df, col, np.std,  'std_'  ).fillna(0) 
#   fillna above used to fix std=NaN if just 1 value in array
def span(x):          return np.amax(x)-np.amin(x)
def f_span( df, col): return f_func(df, col, span,    'span_' )
def f_stats(df, col):
    df1 = f_mean(df, col)
    for fn in [f_max, f_min, f_span, f_std, f_nuniq, f_sum]:
        df1 = df1.merge( fn(df, col), \
                         how='outer', left_index=True, right_index=True )
    return df1

def f_rands(df, col):                   # random features; ignores input data
    g = f_min(df, col)                  # just to get g's shape 
    for col in g.columns:
        del g[col]
    for i in xrange(RANDOM_FEATURES):   # replace with random cols
        g['random_%02i' % i] = np.random.random(len(g)) 
    return g

def feature_counts(df, col_name):
    # count_feature: creates per-member counts of categorical variable
    d = pandas.crosstab(df['MemberID'], df[col_name]) 
    d.columns = ['count_'+col_name+'_'+str(val_name) for val_name in d.columns]
    return d

f_counts = feature_counts # alias...

"""
def expand_var(df, col_name):
    # expand_var: creates binary variables from a categorical one (per claim)
    df_out = pandas.DataFrame( {'MemberId':df['MemberID']} )
    for elem in df[col_name].unique():
        df_out[col_name+'__'+str(elem)] = (df[col_name]==elem)*1
    return df_out
"""

"""
def hash_bin(df, col_name, nbins):
    # Uses the hashing trick for dimentionality reduction. 
    # This uses two functions:
    # 1. hash function to map a large space of IDs to a small # of hash bins 
    # 2. A sign function used to reduce the impact of hash collisions
    # See http://en.wikipedia.org/wiki/Feature_hashing
    #
    # NOTE: This performed *worse* than the hash_pid, hash_pcp 
    # and hash_vendor functions, so it's no longer used. 

    def x_id_hash(x_id): return  hash(x_id) % nbins
    def x_id_sign(x_id): return (hash(x_id) % 2)*2-1 # returns 1 or -1
    df_out      = df[['MemberID']]
    x_id_hashes = df[col_name].map( x_id_hash ) 
    x_id_signs  = df[col_name].map( x_id_sign ) 
    for x_id_hash in sorted(set(x_id_hashes)):
        out_col_name = 'hashbin_'+col_name+'__'+str(x_id_hash)
        df_out[out_col_name] = (x_id_hashes == x_id_hash) * x_id_signs
    result = df_out.groupby('MemberID').sum()
    return result

def hash_bin_pcp(   df, col_name): return hash_bin(df, col_name, HASH_BINS_PCP)
def hash_bin_vendor(df, col_name): return hash_bin(df, col_name, HASH_BINS_VENDOR)
def hash_bin_pid(   df, col_name): return hash_bin(df, col_name, HASH_BINS_PROVIDERID)
"""

# ========================================================================
# Functions to create all features for a specific year 
# ========================================================================

def time_sort(dfs_list):
    dfs_sorted = []
    for n, df in enumerate(dfs_list):
        print "Time-sorting dataframe:",n+1,"of",len(dfs_list) 
        sys.stdout.flush()
        df_sorted = df.sort(['MemberID','Year','int_DSFS'])
        dfs_sorted.append(df_sorted)
    print 
    return dfs_sorted

def df_years_select(years, df):
    mask = False
    for yr in years:
        mask = np.array(df['Year']==yr) | mask
    return df[mask]

def year_select(yrs, dfs_list):
    dfs_yr = []
    for n, df in enumerate(dfs_list):
        print "Selecting year:", yrs, "  (",n+1,"of",len(dfs_list),")"
        sys.stdout.flush()
        # df_yr = df[ df['Year']==yr ]
        df_yr = df_years_select(yrs, df)
        dfs_yr.append(df_yr)
    print
    return dfs_yr


def make_features(members_df, claims_df, drugs_df, labs_df):

    members_features_plan = (

        ('int_AgeAtFirstClaim', (f_rands,)),  # NOTE: random features

        ('AgeAtFirstClaim',     (f_counts,)),
        ('int_AgeAtFirstClaim', (f_min,)),
        ('Sex',                 (f_counts,))
    )

    claims_features_plan = (
       #('MemberID'      ,(f_counts,)),
        ('ProviderID'    ,(f_nuniq,  )),
        ('hash_ProviderID',(f_counts,)),
        ('Vendor'        ,(f_nuniq,  )),
        ('hash_Vendor'   ,(f_counts, )),
        ('PCP'           ,(f_nuniq,  )),
        ('hash_PCP'      ,(f_counts, )),
        ('ClaimYear'     ,(f_counts, f_nuniq, f_num)),
        ('Specialty'     ,(f_counts, f_nuniq)),
        ('PlaceSvc'      ,(f_counts, f_nuniq)),
       #('PayDelay'      ,(f_counts,)),\
        ('LengthOfStay'  ,(f_counts, )),
        ('int_LengthOfStay', (f_stats,)),
        ('ClaimDSFS'     ,(f_counts, )),
        ('ClaimMaxDSFSxDSFS',(f_counts, )),
        ('int_ClaimDSFS' ,(f_stats,  )),
        ('PrimaryConditionGroup' ,(f_counts, f_nuniq)),
        ('CharlsonIndex' ,(f_counts, )),
        ('int_CharlsonIndex' ,(f_stats,)),
        ('ProcedureGroup',(f_counts, f_nuniq)),
        ('SupLOS'        ,(f_counts, ))
    )

    drugs_features_plan = (
        ('DrugYear',        (f_counts, f_nuniq, f_num)),
        ('DrugDSFS',        (f_counts,)),
        ('int_DrugDSFS',    (f_stats, )),
        ('DrugCount',       (f_counts,)),
        ('int_DrugCount',   (f_stats, )),
        ('usedDrugFlag',    (f_max_notag,)) 
    )

    labs_features_plan = (
        ('LabYear',         (f_counts, f_nuniq, f_num)),
        ('LabDSFS',         (f_counts,)),
        ('int_LabDSFS',     (f_stats, )),
        ('LabCount',        (f_counts,)),
        ('int_LabCount',    (f_stats, )),
        ('usedLabFlag',     (f_max_notag,))
    )

    features_plans = [ 
        ("Members", members_df, members_features_plan), 
        ("Claims",  claims_df,  claims_features_plan), 
        ("Labs",    labs_df,    labs_features_plan),    
        ("Drugs",   drugs_df,   drugs_features_plan)     
    ]

    
    print "Generating features"
    all_feats = pandas.DataFrame()
    for file_name, file_data, features_plan in features_plans:
        for col, funcs in features_plan:
            for func in funcs:
                print "%10s --> %23s --> %10s" % (file_name, col, func.__name__)
                sys.stdout.flush()
                feats = func(file_data, col) 
                all_feats = all_feats.merge(feats, \
                                how='outer', left_index=True, right_index=True)
                # print feats[:10].to_string()   
    print 
    sys.stdout.flush()
    return all_feats

# ========================================================================
# main
# ========================================================================

def main():

    print "\n*** HHP: xfeatures generation ***\n"

    dih_y2, dih_y3, target = read_csv_files( [FILE_DIH_Y2, \
                                              FILE_DIH_Y3, FILE_TARGET])
    dih_y2 = dih_y2.set_index('MemberID')
    dih_y3 = dih_y3.set_index('MemberID')
    target = target.set_index('MemberID')

    members, claims, drugs, labs = read_csv_files([FILE_MEMBERS, FILE_CLAIMS, \
                                                   FILE_DRUGS,   FILE_LABS])
    members, claims, drugs, labs = augment(members, claims, drugs, labs)
    claims, drugs, labs = time_sort([claims, drugs, labs])

    for yr, dih in ( (('Y1',    ),dih_y2),   
                     (('Y2',    ),dih_y3),   
                     (('Y3',    ),target), 
                     (('Y1','Y2'),dih_y3),   
                     (('Y2','Y3'),target)\
                   ):
        yr_claims, yr_drugs, yr_labs = year_select(yr, [claims, drugs, labs])
        yr_features = make_features(members, yr_claims, yr_drugs, yr_labs)
        dih_features = dih.merge(yr_features, \
                                 how='left', left_index=True, right_index=True)
        del dih_features['DaysInHospital']
        dih_answers = dih[['DaysInHospital']]
        prefix = ''.join(yr)
        write_features(dih_features, FEATURES_DIR+prefix +'_xfeatures.csv')
        write_features(dih_answers,  FEATURES_DIR+prefix +'_xanswers.csv')

    print "\nDone.\n"

main()


