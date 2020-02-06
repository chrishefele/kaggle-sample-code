import os

TRAIN_DIR = '../download/train/' 
TEST_DIR  = '../download/test/' 
FEATURES_DIR = '../features/'

EXAMPLE_FILENAME = '20090329_134500_49731s182ms_1.aif'

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
    if len(fields) == 4:  # train filename
        d['whale'] = fields[3]
    else:
        d['whale'] = -1  # for test filenames
    return d


def file_features(file_dir, outfile):
    print 'Writing features to:',outfile
    fout = open(outfile,'w')

    header = sorted(parse_filename(EXAMPLE_FILENAME))
    outstring = ','.join(header)
    fout.write(outstring + '\n')

    for afile in sorted(os.listdir(file_dir)):
        features = parse_filename(afile)
        outstring = ','.join((str(features[f]) for f in sorted(features)))
        fout.write(outstring + '\n')
        # print afile, os.path.getsize(file_dir + afile)

def main():
    file_features(TRAIN_DIR, FEATURES_DIR + 'filename_features_train.csv')
    file_features(TEST_DIR,  FEATURES_DIR + 'filename_features_test.csv')

if __name__ == '__main__':
    main()



