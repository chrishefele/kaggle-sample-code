import numpy as np;
from scipy import stats;
import SETTINGS as sts;
import itertools;

from PIL import Image;
import scipy;

logpdf_dict = {}

def get_cnn_results(filename):
#silce location, t0,t1,t2,t3....
    counts_map = None
    counts_map = open(filename, 'r').readlines()
    counts_map = [l.split(',') for l in counts_map]
    counts_map = [[float(st) for st in l] for l in counts_map]
    counts_map = dict((int(r[0]), np.array(r[3:]).reshape((int(r[2])+1,int(r[1]))).T) for r in counts_map)
    return counts_map;

def volume(xy):
    xy = xy[xy[:,1]>0];
    L = xy.shape[0];
    if L<=4:
        print("length <=4");
        return np.nan;
    
    d = np.median(np.diff(xy[:,0]));
    #vol = (xy[0,1]+xy[-1,1])*d/2.0;
    vol = (xy[0,1]+xy[-1,1])*min(8,d)/2.0;
    #vol = 0.0;
    for i in range(1,L):
        #vol += (xy[i,1]+xy[i-1,1]+np.sqrt(xy[i,1]*xy[i-1,1]))/3.0 * np.abs(xy[i,0]-xy[i-1,0]);
        vol += (xy[i,1]+xy[i-1,1])/2.0 * np.abs(xy[i,0]-xy[i-1,0]);
    return vol/1000;

def getvolume(info):
    maxvol = volume(info[:,[0,1]]);
    minvol = volume(info[:,[0,2]]);
    if maxvol>580:
        print("volume {} is too big, set to 580".format(maxvol));
        maxvol = 580;
    if minvol<4:
        print("volume {} is too small, set to 4".format(minvol));
        minvol = 4;
    return maxvol,minvol;

def paratocdf(para):
    x = np.arange(600);
    d = stats.norm.pdf(x,para[0],para[1]);
    min_cut = 4;
    max_cut = 581;
    d[:(min_cut)]=0.0;
    d[(max_cut):]=0.0;
    d/=np.sum(d);
    d = np.cumsum(d);
    return d;

def make_submit(result, start, end, fn):
##generate submission file
    submit_csv = open(sts.output_dir+"/submit_%s.csv"%(fn), "w")
    submit_csv.write('Id,%s\n' % ','.join('P%d' % i for i in range(600)))

    for case in range(start,end+1):
	sede = result.get(case);
	if sede is None or np.any(np.isnan(sede)):
            print(" ERROR !! case {} is not forecasted!!!!".format(case));
            continue
	cdf = paratocdf(sede[2:4]);
        submit_csv.write("%d_Diastole"%case);
        for v in cdf:
            submit_csv.write(',');
            submit_csv.write('%f'%v);
        submit_csv.write('\n');  
	cdf = paratocdf(sede[0:2]);
        submit_csv.write("%d_Systole"%case);
        for v in cdf:
            submit_csv.write(',');
            submit_csv.write('%f'%v);
        submit_csv.write('\n');
      
    submit_csv.close();

def save_intermediate(result,start,end,fn):
    submit_csv = open(sts.output_dir+"/intermediate_%s.csv"%(fn), "w")
    submit_csv.write("Id,Systole,s_std,Diastole,d_std\n")
    for i in range(start,end+1):
        sede = result.get(i);
        hd = sede[2:4];
        hs = sede[0:2];
        submit_csv.write('%d,%f,%f,%f,%f\n'%(i,hs[0],hs[1],hd[0],hd[1]));
    submit_csv.close();

def goodness(data):
    return np.sum(data);

def ll_means_stds(counts_list):
    counts_stacked = []
    for c_ in counts_list:
        cm = np.copy(c_)
        cm = (cm*255./cm.max()).astype(np.uint8)
        cm = cm[np.where(cm.sum(axis=1))]
        im = Image.fromarray(cm).resize((30,10), Image.ANTIALIAS)
        resized_counts = np.array(im.getdata(), dtype=np.float32)/255.
        counts_stacked.append(resized_counts)
    counts_stacked = np.array(counts_stacked)
    means = counts_stacked.mean(axis=0)
    stds = counts_stacked.std(axis=0)
    return means, stds

def ll_of_count(counts, means, stds):
    if len(logpdf_dict) == 0:
        logpdf_dict.update({ int(np.round(x*1e4)): np.log(stats.norm.pdf(x))
                for x in np.arange(-6,6,1e-4) })
    cm = np.copy(counts)
    cm = (cm*255./cm.max()).astype(np.uint8)
    cm = cm[np.where(cm.sum(axis=1))]
    if cm.shape[0] == 0:
        cm = np.zeros((10, 30), dtype = np.uint8)
    im = Image.fromarray(cm).resize((30,10), Image.ANTIALIAS)
    counts_resized_arr = np.array(im.getdata(), dtype=np.float32).reshape(10,30)/255.
    max_ll = -10000000
    for roll_by in xrange(30):
        resized_counts = np.roll(counts_resized_arr, roll_by, axis=1).flatten()
        ll = 0.
        for i in xrange(resized_counts.shape[0]):
            z = (resized_counts[i] - means[i]) / stds[i]
            ll += logpdf_dict[np.clip(np.round(z*1e4), -60000,59999)]
            #ll += np.log(scipy.stats.norm.pdf(resized_counts[i], loc=means[i], scale=stds[i]))
        if ll > max_ll:
            max_ll = ll
    return max_ll

# known cases that are rejected (Tencia's code):
# 307, 212 (babies)
# 517 (blowup of one slice), 599, 634, 692
# filter_ll is min ll value thats accepted. recommend ~ -550
def take_best(cfiles,method=2, filter_ll=None):
    res = {};
    css = [list(x.keys()) for x in cfiles];
    css = set(list(itertools.chain.from_iterable(css)));
    if filter_ll is not None:
        mean, std = ll_means_stds([a_[:,1:] for sublist in [adic.values() for adic in cfiles]
            for a_ in sublist])
    for c in css:
        d = [f.get(c) for f in cfiles];
        d = [x for x in d if x is not None];
        if len(d)==0:continue;
        if method == 1: #element wise
            x = d[0];
            for i in range(1,len(d)):
                x = np.maximum(x,d[i])
            res[c] = x;
        elif method == 2: #as a whole
            d_score = [goodness(x) for x in d];
            ii = np.argmax(d_score);
            if d_score[ii]>3*30:
                res[c] = np.copy(d[ii]);   
        if filter_ll is not None:
            ll = ll_of_count(res[c][:,1:], mean, std)
            if ll < filter_ll:
                print 'rejected case {} ll = {}'.format(c, ll)
                res.pop(c,None)
    return res;

def take_best_contour(areafiles,contfiles,method=1, filter_ll=None):
    css = [list(x.keys()) for x in areafiles];
    css = set(list(itertools.chain.from_iterable(css)));
    areas = {};
    conts = {};
    if filter_ll is not None:
        mean, std = ll_means_stds([a_[:,1:] for sublist in [adic.values() for adic in areafiles]
            for a_ in sublist])
    for c in css:
        da = [f.get(c) for f in areafiles];
        dc = [f.get(c) for f in contfiles];
        dc = [x for x in dc if x is not None];
        da = [x for x in da if x is not None];
        assert(len(dc) == len(da));
        if len(dc)==0:continue;
        if method == 1:
            x = np.copy(dc[0]);
            y = np.copy(da[0]);
            for i in range(1,len(dc)):
                idx = x<dc[i];
                y[idx] = da[i][idx];
                x[idx] = dc[i][idx];
            areas[c] = y;
            conts[c] = x;
        elif method == 2:#as a whole
            score = [np.sum(x) for x in dc];
            ii = np.argmax(score);
            areas[c] = np.copy(da[ii]);
            conts[c] = np.copy(dc[ii]);
        elif method == 3:#take average
            areas[c] = np.mean(da,axis=0);
            conts[c] = np.mean(dc,axis=0);
        ##if bad:areas.pop(c,None);conts.pop(c,None)
        if filter_ll is not None:
            ll = ll_of_count(areas[c][:,1:], mean, std)
            if ll < filter_ll:
                print 'rejected case {} ll = {}'.format(c, ll)
                areas.pop(c,None)
		conts.pop(c,None)

    return areas,conts;

def clean_data(data,case,cleaner=[]):
    L = data.shape[0];
    if 0 in cleaner:#smooth single wrong reads
        for i in reversed(range(1,min(L//2,3))):
            if data[i-1,2] > (data[i,2]+10)*1.5 and data[i,2]<data[i+1,2]:
                data[:i,2] = 0.0;
                #print("case {} {} sys set to 0".format(case,i));
        #    if data[i-1,1] > (data[i,1]+10)*1.5 and data[i,1]<data[i+1,1]:
        #        data[:i,1:3] = 0.0;
        #        #print("case {} {} dias set to 0".format(case,i));
        #does not seem to work, 
        #for k in range(1,3):
        #    for i in range(2,L-2):
        #        x = (data[i,k]+100)*1.5;
        #        if (x< data[i-1,k]) and (x < data[i+1,k]):
        #            data[i,k] = 0.8*np.mean([data[i-1,k],data[i+1,k]]);
        #            #print("case {} {} {} fixed too small read".format(case,k,i));
    if 1 in cleaner:
        idx = data[:,1]<0.5*data[:,2];
        if np.sum(idx)>0:
            data[idx,1] = data[idx,2]*1.3;
            #print("case {} fixed reverse data points".format(case));
    if 2 in cleaner:
    #smooth jumpy max point
        ii = np.argmax(data[:,1]);
        v = np.percentile(data[:,1],80)
        if data[ii,1]> v * 1.4:
            #print("error max read dias for case {}".format(case))
            data[ii,1] =  v;
        ii = np.argmax(data[:,2]);
        v = np.percentile(data[:,2],80)
        if data[ii,2]> v * 1.4:
            #print("error max read sys for case {}".format(case))
            data[ii,2] =  v;
    if 3 in cleaner: #! does not seem to work, don't call it
        pass
        dsm = np.max(data[:,1:3],axis=0);
        for i in range(0,min(L//2,3)):
            if data[i,1]>0 and data[i,1] < dsm[0]*0.05:
                data[i,1] = 0.0;
                #print("case {} {} dias set to 0".format(case,i));
            if data[i,2]>0 and data[i,2] < dsm[1]*0.05:
                data[i,2] = 0.0;
                #print("case {} {} sys set to 0".format(case,i));

def get_preliminary_volume(areas_all, cleaner=[]):
    result = {};
    for case,areas in areas_all.iteritems():
        x = np.sum(areas[:,1:],axis=0);
        tsys,tdias = np.argmin(x),np.argmax(x);
        data = areas[:,[0,tdias+1,tsys+1]];
        data = np.copy(data[data[:,1]>0]);
        #add data cleanng code here
        clean_data(data,case,cleaner);
        maxv,minv = getvolume(data);
        result[case] = [minv, maxv];
    return result;

def get_preliminary_volume_cnt(areas_all, cont_all,cleaner=[]):
    result = {};
    for case,areas in areas_all.iteritems():
        x = np.sum(areas[:,1:],axis=0);
        tsys,tdias = np.argmin(x),np.argmax(x);
        data = areas[:,[0,tdias+1,tsys+1]];
        cont = cont_all.get(case);
        idx = data[:,1]>0;
        data = data[idx];
        cont = cont[idx];
        #add data cleanng code here
        conf = np.mean(cont[:,1:],axis=1);
        mc = np.max(conf);
        s_p = np.minimum(5,np.argmax(data[:,1]));
        if mc>0.95:
            for i in range(s_p):
                if (cont[i,tdias+1]<0.65 and cont[i+1,tdias+1]<0.9) or (cont[i,tdias+1]<0.55):
                    data[i,1] = 0.0;
                    data[i,2] = 0.0;
                else:break
            for i in range(s_p):
                if ((cont[i,tsys+1]<0.7 and cont[i+1,tsys+1]<0.9)) or (cont[i,tsys+1]<0.6):
                    data[i,2] = 0.0;
                    if i>=1:data[i-1,1] *= 0.8;
                    if i>=2:data[i-2,1] = 0.0;
                else:break;
        clean_data(data,case,cleaner);
        maxv,minv = getvolume(data);
        result[case] = [minv, maxv];
    return result;

def get_preliminary_volume_cnt_filter(areas_all, cont_all,cleaner=[]):
    result = {};
    for case,areas in areas_all.iteritems():
        x = np.sum(areas[:,1:],axis=0);
        tsys,tdias = np.argmin(x),np.argmax(x);
        data = areas[:,[0,tdias+1,tsys+1]];
        cont = cont_all.get(case);
        idx = data[:,1]>0;
        data = data[idx];
        cont = cont[idx];
        cd = np.sum(cont[data[:,1]>np.median(data[:,1]),tdias+1]<0.9);
        cs = np.sum(cont[data[:,2]>np.median(data[:,2]),tsys+1]<0.9);
        clean_data(data,case,cleaner);
        maxv,minv = getvolume(data);
        result[case] = [minv,cs, maxv,cd];
    return result;

def get_preliminary_volume_features(areas_all, cont_all,cleaner=[]):
    result = {};
    for case,areas in areas_all.iteritems():
        x = np.sum(areas[:,1:],axis=0);
        tsys,tdias = np.argmin(x),np.argmax(x);
        data = areas[:,[0,tdias+1,tsys+1]];
        cont = cont_all.get(case);
        idx = data[:,1]>0;
        data = data[idx];
        cont = cont[idx];
        clean_data(data,case,cleaner);
        maxv,minv = getvolume(data);
        cd = np.sum(cont[data[:,1]>np.median(data[:,1]),tdias+1]<0.9)
        cs = np.sum(cont[data[:,2]>np.median(data[:,2]),tsys+1]<0.9)
        Ls = np.sum(data[:,2]>0);
        Ld = np.sum(data[:,1]>0);
        js = np.sum(np.abs(np.diff(data[:,1])))/np.percentile(data[:,1],80)/2;
        jd = np.sum(np.abs(np.diff(data[:,2])))/np.percentile(data[:,2],80)/2;
        result[case] = [minv,cs,Ls,js,maxv,cd,Ld,jd];
    return result;

def fill_default(preds, default):
    final = {};
    for case,value in default.iteritems():
        pred = preds.get(case);
        if pred is None:
            final[case] = value;
            print("use default for {}, not predicted".format(case));
        else:
            x = np.copy(pred);
            if np.isnan(x[0]):
                x[0:2] = value[0:2];
                print("use default for {} systole, nan".format(case));
            if np.isnan(x[2]):
                x[2:4] = value[2:4];
                print("use default for {} diastole, nan".format(case));
            final[case] = x;
    return final;

def crps_score(ve,y):
    idx = np.logical_not(np.isnan(ve[:,0]));
    ve = ve[idx];
    y = y[idx];
    cdf_true = np.zeros(600);
    cidx = np.arange(600);#volume is 0 to 599ml
    score = 0.0;
    for i in range(ve.shape[0]):
        cdf_true[:] = 0.0;
        cdf_true[cidx>=y[i]] = 1.0;
        cdf = stats.norm.pdf(cidx,ve[i,0],ve[i,1]);
        cdf[:4] = 0.0;
        cdf[581:] = 0.0;
        cdf/=np.sum(cdf);
        cdf = np.cumsum(cdf);
        score += np.mean((cdf-cdf_true)**2);
    return score/ve.shape[0];

def evaluate_pred(preds, train_true):
    N = train_true.shape[0];
    X = np.zeros((N*2,2));
    y = np.zeros(N*2);
    for i,idx,row in enumerate(train_true.iterrows()):
        y[i*2] = row['Systole'];
        y[i*2+1] = row['Diastole'];
        res = preds.get(row['Id']);
        X[i*2] = res[0:2] if res else [np.nan,np.nan];
        X[i*2+1] = res[2:4] if res else [np.nan,np.nan];
    score = crps_score(X,y);
    print("score is {}".format(score));
