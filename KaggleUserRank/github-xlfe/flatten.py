import json
import sys
import csv

fn_name = sys.argv[1]
inp_file = open(fn_name)

inp_list = json.load(inp_file)

def get_columns(obj):

    columns = []
    cols = []

    if type(obj) == list:
        for l in obj:
            cols.extend(get_columns(l))

    elif type(obj) == dict:

        for k,v in obj.iteritems():

            cols.append(k)
            cols.extend(get_columns(v))

    for c in cols:
        if c in columns:
            continue
        columns.append(c)

    return columns

column_names = ['competitions'] + get_columns(inp_list)

def flatten(obj,column_names,columns):

    dyield = False

    if type(obj) == list:

        #The index is written to the first empty (None) row
        for idx in range(0,len(columns)):
            if columns[idx] == None:
                break

        for i in range(0,len(obj)):

            columns[idx] = i + 1

            for r in flatten(obj[i],column_names,columns):
                yield r

            columns[idx] = None

    elif type(obj) == dict:

        for k,v in obj.iteritems():

            if type(v) == list:
                continue

            columns[column_names.index(k)] = v

        for k,v in obj.iteritems():

            if type(v) == list:

                #make sure we don't yield a result for the dict by itself as it is being expanded
                dyield = True

                for r in flatten(v,column_names,columns):
                    yield r

        if not dyield:
            #only yield a result for this dict if it is an end leaf (ie no children)
            yield ','.join(str(c).replace(',','') if c is not None else '' for c in columns)

print ','.join(column_names)
columns = [None for i in range(0,len(column_names))]
for r in flatten(inp_list,column_names,columns):
    print r

