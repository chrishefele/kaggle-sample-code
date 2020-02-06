import os.path
import sys
import pickle

DATA_DIR     = "/home/chefele/SemiSupervised/data/data/"
DOWNLOAD_DIR = "/home/chefele/SemiSupervised/download/competition_data/"
TRAIN     = DOWNLOAD_DIR + "public_train_data.svmlight.dat"
TEST      = DOWNLOAD_DIR + "public_test_data.svmlight.dat"
UNLABELED = DOWNLOAD_DIR + "unlabeled_data.svmlight.dat"
TRAIN_TEST_UNLABELED = DATA_DIR + "train+test+unlabeled_data.svmlight.dat"

TRAIN_LINES = 50000
TEST_LINES  = 50000
UNLABELED_LINES = 1000000
TOT_LINES = TRAIN_LINES + TEST_LINES + UNLABELED_LINES 

CACHE_DIR  = "/home/chefele/SemiSupervised/data/cache/"
CACHE_DATA_FILE   = CACHE_DIR + "col_data_cache.pkl"
CACHE_ANALOG_COLS = CACHE_DIR + "analog_cols.csv"
CACHE_BINARY_COLS = CACHE_DIR + "binary_cols.csv"

DIR_OUT = "/home/chefele/SemiSupervised/data/data/"
TRAIN_OUT_ANALOG = DIR_OUT + "train_analog.csv"
TEST_OUT_ANALOG  = DIR_OUT + "test_analog.csv"
TRAIN_TEST_UNLABELED_OUT_BINARY    = DIR_OUT + "train+test+unlabeled_binary.csv"
TRAIN_TEST_UNLABELED_OUT_ANALOGPCA = DIR_OUT + "train+test+unlabeled_analogpca.csv"


def read_col_vals(): 
    line_counter = 0
    col_vals = {}
    for inFileName in [TRAIN,TEST,UNLABELED]:
        print "Reading data file:", inFileName
        print "Reading line:",
        for line in open(inFileName,"r"):
            line_counter+=1
            if line_counter % 5000 ==0:
                print line_counter,
                sys.stdout.flush()
            for field in line.split(" ")[1:]: # skips first field...
                tokens = field.split(":")
                col = int(tokens[0])
                col_val = float(tokens[1])
                col_val = max(0.0, min(1.0, col_val)) # clamp to [0,1]
                if col not in col_vals:
                    col_vals[col]=[]
                col_vals[col].append(col_val)  
        print "\nClosing:",inFileName,"at line#:", line_counter,"\n"
        sys.stdout.flush()
    return(col_vals)

def get_col_vals():
    if not os.path.exists(CACHE_DATA_FILE):
        col_vals = read_col_vals()
        print "Writing data to data cache file:", CACHE_DATA_FILE
        sys.stdout.flush()
        fout = open(CACHE_DATA_FILE,"wb")
        pickle.dump( col_vals, fout, pickle.HIGHEST_PROTOCOL )
        fout.close()
        del col_vals
    print "Reading data from data cache file:", CACHE_DATA_FILE
    sys.stdout.flush()
    col_vals = pickle.load( open(CACHE_DATA_FILE,"rb") )
    return(col_vals)
       
def calc_cols():
    cv = get_col_vals()
    print "Total number of unique columns of data read:", len(cv)
    print "Total data points read:", sum( [ len(cv[c]) for c in cv] )

    print "Writing analog and binary feature column cache files"
    fout_a = open(CACHE_ANALOG_COLS,"w")
    fout_b = open(CACHE_BINARY_COLS,"w")
    for col in sorted(cv):
        if set(cv[col]) != set([1,]): # 0's missing/implied; [0,1] means binary data
            # print "Analog col:", col
            fout_a.write(str(col)+"\n")
        else:
            fout_b.write(str(col)+"\n")
    fout_a.close()
    fout_b.close()

def get_cols(colsCacheFile):
    if not os.path.exists(colsCacheFile):
        calc_cols()
    cols = sorted( [int(line) for line in open(colsCacheFile,'r')] )
    return(cols)

def parse_line(line):
    # parses line, returns dict of column_num:value mapping
    col_vals = {}
    for field in line.split(" ")[1:]:    # skips first field...
        tokens = field.split(":")
        col, col_val = int(tokens[0]), float(tokens[1])
        col_vals[col] = max(0.0, min(1.0, col_val)) # clamp to [0,1]
    return(col_vals)
   
def analog_feature_formatter(line_col_vals, analog_cols, line_counter, analog_cols_set):
    line_out = ' , '.join([str(line_col_vals.get(ac,0)) for ac in analog_cols])
    return(line_out)

def binary_feature_formatter(line_col_vals, binary_cols, line_counter, binary_cols_set):
    # For each non-zero column on the input line, output a line 
    # with <input_line/row>,<column>  but only if it's a binary feature   
    # 
    # line_col_vals   =  a dict of col->value; only non-zero values are stored
    # binary_cols     = list of the column numbers of the binary variables 
    # binary_cols_set = set(binary_cols) for fast lookup
    # line_counter    = input line number, aka vout, aka input n-dimentional point number 
    line_out = '\n'.join([ str(line_counter)+" "+str(bc) 
                           for bc in sorted(line_col_vals) if bc in binary_cols_set ])
    return(line_out)

def write_features_file(inFileName, outFileName, formatter, cacheFile):
    cols = get_cols(cacheFile) # sorted columns of this feature type (binary/analog)
    cols_set = set(cols)  # used in formatting for fast lookup
    print "Reading:", inFileName
    print "Writing:", outFileName
    sys.stdout.flush()
    fout = open(outFileName,"w")
    line_counter = 0
    for line in open(inFileName,"r"):
        line_counter += 1 
        line_col_vals = parse_line(line)
        line_out = formatter(line_col_vals, cols, line_counter, cols_set) 
        fout.write(line_out+"\n")
    fout.close()
    print "Finished writing:", outFileName,"\n"

def write_analog_features_file(inFileName, outFileName):
    write_features_file(inFileName, outFileName, analog_feature_formatter, CACHE_ANALOG_COLS)

def write_binary_features_file(inFileName, outFileName):
    write_features_file(inFileName, outFileName, binary_feature_formatter, CACHE_BINARY_COLS)



