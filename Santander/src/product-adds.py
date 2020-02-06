
import csv
import sys
import time
import dateutil.parser
import collections
import string

CSV_TRAIN = "../data/train_ver2.csv"

def parse_csv_string(s):
    r = csv.reader([s]) # returns interator
    return list(r)[0]

def get_header(fname=CSV_TRAIN):
    with open(CSV_TRAIN) as fin:
        header = csv.reader(fin).next()
        return header

def cust_row_groups(fname=CSV_TRAIN):
    with open(fname) as fin:
        reader = csv.DictReader(fin)
        ncodpers_last = None
        cust_rows = {}
        for row_dict in reader:
            
            ncodpers = int(row_dict['ncodpers'])
            fecha_dato = row_dict['fecha_dato']
            if ncodpers_last and ncodpers != ncodpers_last:
                yield cust_rows
                cust_rows = {}
            cust_rows[fecha_dato] = row_dict
            ncodpers_last = ncodpers
        yield cust_rows

def int_default(s, default=0):
    try:
        return int(s)
    except:
        return default

def any_target_adds(cust_rows, target_cols, date0, date1):
    for col in target_cols:
        i0 = int_default(cust_rows[date0][col]) 
        i1 = int_default(cust_rows[date1][col]) 
        if i0 == 0 and i1 == 1:
            return True
    return False

def main():

    date1 = DATE1 = '2016-05-28'
    date0 = DATE0 = '2016-04-28'
    FILE_OUT = "fout.csv"

    header = get_header()
    target_cols = [col for col in header if "_ult1" in col]

    fout = open(FILE_OUT, 'w')
    fout.write(','.join(header) + '\n')

    group_n = 0
    for cust_rows in cust_row_groups():

        group_n += 1
        if group_n % 1000 == 0:
            print "group_n:", group_n

        if not date0 in cust_rows or not date1 in cust_rows:
            continue

        if not any_target_adds(cust_rows, target_cols, date0, date1):
            continue
        
        for row_date in sorted(cust_rows):
            line_out = ','.join([cust_rows[row_date][col] for col in header])
            fout.write(line_out + '\n')

    fout.close()


main()

