
import csv
import sys
import time
import dateutil.parser
import collections
import string

CSV_TRAIN = "../data/train_ver2.csv"
DATE_DEFAULT = "2015-01-28"
NAN = float("NaN")

def dateparse(d, date_default=DATE_DEFAULT):
    d = d if d else DATE_DEFAULT
    return dateutil.parser.parse(d) 

# print dateparse("2012-01-27")

def get_header(fname=CSV_TRAIN):
    with open(CSV_TRAIN) as fin:
        header = csv.reader(fin).next()
        return header

def cust_row_groups(fname=CSV_TRAIN):
    with open(fname) as fin:
        reader = csv.DictReader(fin)
        ncodpers_last = None
        cust_rows = []
        for row_num, row_dict in enumerate(reader):
            ncodpers = int(row_dict['ncodpers'])
            if ncodpers_last and ncodpers != ncodpers_last:
                yield cust_rows
                cust_rows = []
            cust_rows.append(row_dict)
            ncodpers_last = ncodpers
        yield cust_rows

for cust_rows in cust_rows_groups():
    print len(cust_rows)
    for cust_row in cust_rows:
        print cust_row
        print
    print "---------------------"
    
raise ValueError, "value error"

def type_default(converter, default_value, func_name):
    def func(x):
        try:
            return converter(x)
        except:
            return default
    func.__name__ = func_name
    return func


float_default = type_default(float, NAN, 'float_default')
int_default   = type_default(int,     0, 'int_default')
date_default  = type_default(dateutil.parser.parse,     
                             dateutil.parser.parse(DATE_DEFAULT),'date_default')

converters = {
	"fecha_dato" 		: date_default,
	"ncodpers" 			: int, 
	"ind_empleado" 		: str, 
	"pais_residencia" 	: str,  # ES or non-ES? country 118 unique values, mostly ES
	"sexo" 				: str, 
	"age" 				: int_default,  # TODO check, use float default instead? 
	"fecha_alta" 		: date_default, 
	"ind_nuevo" 		: int_default, 
	"antiguedad" 		: int_default, # NOTE -999999 sentinal , 200+ unique values
	"indrel" 			: int_default,  # note 99 sentinel ; 1 or 99; any NULLS????
	"ult_fec_cli_1t" 	: date_default,   # last date as primary customer
	"indrel_1mes" 		: string.strip,
	"tiprel_1mes" 		: str, 
	"indresi" 			: str, 
	"indext" 			: str, 
	"conyuemp" 			: str,  # TODO check????
	"canal_entrada" 	: str,  # 152 KCODES...what is this? 
	"indfall" 			: str, 
	"tipodom" 			: int_default, 
	"cod_prov" 			: int_default, 
	"nomprov" 			: str,  # name of province...many different classes 
	"ind_actividad_cliente" : int_default, 
	"renta" 			: float_default, 
	"segmento" 			: str,
    # 
    "ind_ahor_fin_ult1" : int_default, 
    "ind_aval_fin_ult1" : int_default, 
    "ind_cco_fin_ult1" 	: int_default, 
	"ind_cder_fin_ult1" : int_default, 
	"ind_cno_fin_ult1"  : int_default, 
	"ind_ctju_fin_ult1" : int_default, 
	"ind_ctma_fin_ult1" : int_default, 
	"ind_ctop_fin_ult1" : int_default, 
	"ind_ctpp_fin_ult1" : int_default, 
	"ind_deco_fin_ult1" : int_default, 
	"ind_deme_fin_ult1" : int_default, 
	"ind_dela_fin_ult1" : int_default, 
	"ind_ecue_fin_ult1" : int_default, 
	"ind_fond_fin_ult1" : int_default, 
	"ind_hip_fin_ult1"  : int_default, 
	"ind_plan_fin_ult1" : int_default, 
	"ind_pres_fin_ult1" : int_default, 
	"ind_reca_fin_ult1" : int_default, 
	"ind_tjcr_fin_ult1" : int_default, 
	"ind_valo_fin_ult1" : int_default, 
	"ind_viv_fin_ult1"  : int_default, 
	"ind_nomina_ult1"   : int_default, 
	"ind_nom_pens_ult1" : int_default, 
	"ind_recibo_ult1"   : int_default 
}

cust_info = [k for k in field_perser if "_ult1" not in k]
fin_prods = [k for k in field_perser if "_ult1"     in k]

