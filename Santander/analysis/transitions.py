
import csv

CSV_TRAIN = "../data/train_ver2.csv"

def is_fin_prod(s):
    return "_ult1" in s


def prod_status(s): 
    try:
        return(str(int(float(s))))
    except:
        return("?")

def row_statuses(d):
    return [prod_status(d[k]) for k in sorted(d) if is_fin_prod(k)]

def status_str(statuses):
    return ''.join(statuses)

def status_diff(statuses0, statuses1):
    return ['1' if s0=='0' and s1=='1' else '0' for s0,s1 in zip(statuses0, statuses1)]

def status_diff_str(sds):
    return ''.join('X' if int(sd) else '-' for sd in sds)


with open(CSV_TRAIN) as fin:

    cust_t0 = None
    reader = csv.DictReader(fin)
    for n, row in enumerate(reader):

        cust_t1   = row['ncodpers']
        date_t1   = row['fecha_dato']
        status_t1 = row_statuses(row)
        
        if cust_t0 == cust_t1:
            n_changes = sum(int(i_str) for i_str in status_diff(status_t0, status_t1))
            if n_changes > 0:
                #print n, date_t0, cust_t0, status_str(status_t0)
                #print n, date_t1, cust_t1, status_str(status_t1)
                #print n_changes, n, date_t0, date_t1, cust_t1, status_diff_str(status_diff(status_t0, status_t1))
                print n_changes, status_str(status_t0), "->", status_str(status_t1),
                print status_diff_str(status_diff(status_t0, status_t1))

        date_t0     = date_t1
        cust_t0     = cust_t1
        status_t0   = status_t1


