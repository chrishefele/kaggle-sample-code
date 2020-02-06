import os, os.path, sys
import pandas
import numpy

TRAIN_DIR           = '../download/train2/' 
TEST_DIR            = '../download/test2/' 

TRAIN_FEATURES_FILE = '../features/diff_daysec_features_train.csv'
TEST_FEATURES_FILE  = '../features/diff_daysec_features_test.csv'

TRAIN_TEMPLATE_FILE = '../data/train2_template.csv'
TEST_TEMPLATE_FILE  = '../download/sampleSubmission2.csv'

EXAMPLE_FILENAME    = '20090328_000000_002s3ms_TRAIN0_0.aif'
CATEGORICAL_FILESIZES = True

def make_train_file_template(filename):
    # make a template file for training data in the 
    # same format as the submission template file
    print "Writing template for training data to:", filename
    fout = open(filename,'w')
    fout.write('clip,probability\n')
    for afile in sorted(os.listdir(TRAIN_DIR)):
        whale_flag = parse_filename(afile)['whale']
        outline = afile + ',' + str(whale_flag)
        fout.write(outline + '\n')
    fout.close()

def parse_filename(filename):
    d = {}
    fname, ext = filename.split('.')
    fields = fname.split('_')
    d['file']   = filename
    d['year']   = fields[0][0:4]
    d['month']  = fields[0][4:6]
    d['day']    = fields[0][6:8]
    d['hour']   = fields[1][0:2]
    d['minute'] = fields[1][2:4]
    d['sec']    = fields[1][4:6]
    d['daysec'] = fields[2].split('s')[0]
    d['daymsec']= fields[2].split('s')[1][:-1]
    d['daymsec_pos0'] = d['daymsec'][-1]
    if len(fields) == 5:  # for training set 
        d['whale'] = fields[4]
    else:
        d['whale'] = -1  # for test set
    return d

def parse_daysec(fname):       
    return int(parse_filename(fname)['daysec'])

def file_size(filename): 
    return int(os.path.getsize(filename))

def expand_var(df, col_name):
    # creates binary variables from a categorical one 
    for elem in df[col_name].unique():
        df[col_name+'_'+str(elem)] = 1*(df[col_name]==elem)
    return df
    # initialize?: df_out = pandas.DataFrame( {'clip':df['clip']} )  

def make_features(template_file, clip_dir): # returns dataframe
    print "Making features using:", template_file
    clip_names = pandas.read_csv(template_file)['clip']
    df = pandas.DataFrame( {'clip':clip_names} )

    # add "diffDaysec" features, which are seconds since last clip 
    # add them as both an integer and categorical feature
    daysec = df['clip'].apply(parse_daysec)
    df['diffDaysec'] = numpy.ediff1d( numpy.array(daysec), to_begin=0)
    for i in range(10):
        df['diffDaysec%02i'%i] = 1*(df['diffDaysec']==i)

    """
    dir_file_size = lambda f: file_size(clip_dir + f)
    df['fsize'] = df['clip'].apply(dir_file_size)
    if CATEGORICAL_FILESIZES:
        df = expand_var(df, 'fsize')
    """

    del df['clip']
    return df

def write_features(df, filename):
    print "Writing features with shape", df.shape,"to file:", filename
    sys.stdout.flush()
    df.to_csv(filename, index=False)

def main():
    print "\n*** Diff Daysec Features for Whale Redux ***\n"

    print "Train template file:", TRAIN_TEMPLATE_FILE, 
    if os.path.exists(TRAIN_TEMPLATE_FILE):
        print "found. Using it."
    else:
        "not found. Creating it."
        make_train_file_template(TRAIN_TEMPLATE_FILE)

    train_features = make_features(TRAIN_TEMPLATE_FILE, TRAIN_DIR)
    test_features  = make_features(TEST_TEMPLATE_FILE,  TEST_DIR)

    write_features(train_features, TRAIN_FEATURES_FILE)
    write_features(test_features,  TEST_FEATURES_FILE)

    print "Done."

if __name__ == '__main__':
    main()

