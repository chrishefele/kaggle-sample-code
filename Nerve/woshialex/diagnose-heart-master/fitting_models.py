from scipy.optimize import minimize;
import numpy as np;
from scipy import stats
import itertools;
import analysis;

class BaseModel:
    def __init__(self):
        self.p = None;

    def set(self,p):
        self.p = p;

class SexAgeModel(BaseModel):
    def __init__(self):
        self.p = np.array([[4.0,3,10.6,12,75,181],\
                [3.0,8,7.0,30,53,144]]);
        #fitted: 0.03737 in train

    def fit(self, info, train_true):
        print("use fitted values, no fitting")

    def predict(self,info):
        res = {};
        for idx,row in info.iterrows():
            case,age,sex = row['Id'],row['age'],row['sex'];
            p = self.p;
            if sex=='M':
                if age<15:
                    hS = [p[0][0]*age+p[0][1],15];
                    hD = [p[0][2]*age+p[0][3], 35];
                else:
                    hS = [p[0][4],35];
                    hD = [p[0][5],45];
            elif sex=='F':
                if age<15:
                    hS = [p[1][0]*age+p[1][1],15];
                    hD = [p[1][2]*age+p[1][3],35];
                else:
                    hS = [p[1][4],35];
                    hD = [p[1][5],40];
            else:
                print("!!!no such sex type!");
                hS = [p[1][4],35];
                hD = [p[1][5],45];
            res[case] = np.asarray(hS + hD);
        return res;

class OneSliceModel(BaseModel):
    def __init__(self):
        self.p = np.array([5,0.00115,10,0.00124,0.080,6,0.075,7]);
        #fitted on train, score = 0.01519

    def fit(self, areas_all, train_true):
        print("not implemented yet, use default to fit")

    def predict(self, areas_all): 
        #take the area_data as input
        #return sys_vol, sys_err, dias_vol, dias_error
        res = {};
        p = self.p;
        for case,areas in areas_all.iteritems():
            x = np.sum(areas[:,1:],axis=0);
            tsys,tdias = np.argmin(x),np.argmax(x);
            a = areas[:,tdias+1];
            if np.sum(a>100) <= 2:
                dias_v = np.nan;
                sys_v = np.nan;
            else:
                da = np.percentile(a,80);
                dias_v = np.clip(p[2] + p[3]*da**1.5,5,580);
                a = areas[:,tsys+1];
                if np.sum(a>100) <= 2:
                    sys_v = np.nan;
                else:
                    sa = np.percentile(a,80);
                    sys_v = np.clip(p[0] + p[1]*(10+sa)*(da**0.5+sa**0.5)/2,5,580);    
            sys_err = np.clip(sys_v * p[4] + p[5],0,30);
            dias_err = np.clip(dias_v * p[6] + p[7],0,30);
            res[case] = np.asarray([sys_v, sys_err, dias_v, dias_err]);
        return res;

class SaxModel(BaseModel):
    def __init__(self,version=1):
        self.version = version;
        if version == 1:
            self.p0 = [1.05,1.05,0.05,4];
            self.bounds = [(0.8,1.5),(0.8,1.3),(0.03,0.07),(0,10)];
        elif version == 2:
            self.p0 = [1.0,1.0,0.05,4,0.05,4];
            self.bounds = [(-0.5,1.8),(-0.5,1.5),(0.03,0.10),(0,10),(0.03,0.10),(0,10)];
        elif version == 3:
            self.p0 = [1.05,0, 1.05, 0, 0.05,4, 0.05, 4];
            self.bounds = [(0.8,1.5),(0,30), (0.8,1.3),(0,50),(0.03,0.10),(0,10), (0.03,0.10),(0,10)];

        self.p = None;

    def _get_result(self,X,p):#X a single column vector of sys and dias volume
        CLIP = 25;
        Y = np.zeros((X.shape[0],2));
        if self.version == 1:
            Y[::2,0] = X[::2]*p[0];
            Y[1::2,0] = X[1::2]*p[1];
            Y[:,1] = np.clip(Y[:,0]*p[2]+p[3], 0, CLIP);
        elif self.version == 2:
            Y[::2,0] = X[::2] - np.sqrt(X[::2])*p[0];
            Y[1::2,0] = X[1::2] - np.sqrt(X[1::2])*p[1];
            Y[::2,1] = np.clip(Y[::2,0]*p[2]+p[3], 0, CLIP);
            Y[1::2,1] = np.clip(Y[1::2,0]*p[4]+p[5], 0, CLIP);
        elif self.version == 3:
            Y[::2,0] = X[::2]*p[0] + p[1];
            Y[1::2,0] = X[1::2]*p[2] + p[3];
            Y[::2,1] = np.clip(Y[::2,0]*p[4]+p[5], 0, CILP);
            Y[1::2,1] = np.clip(Y[1::2,0]*p[6]+p[7], 0, CLIP);
        return Y;

    def fit(self, results, train_true):
        x = [];
        y = [];
        count = 0;
        missing = [];
        for idx,row in train_true.iterrows():
            res = results.get(row['Id']);
            if res is None:
                missing.append(row['Id']);
                continue
            count+=1;
            x.extend(res);
            y.extend([row['Systole'],row['Diastole']]);
        print("{} cases are used to fit the model".format(count));
        if len(missing)>0:
            print("cases are missing: " + ','.join([str(m_) for m_ in missing]));
        x = np.asarray(x);
        y = np.asarray(y);
        ff = minimize(lambda p:analysis.crps_score(self._get_result(x,p),y), self.p0, bounds=self.bounds, options={'gtol':1e-5,'maxiter':500,'eps':1e-5});
        self.p = ff.x;
        print("fitting parameters " + str(self.p));
        print("fitting score " + str(ff.fun));
    
    def predict(self,results):
        res = {};
        if self.p is None:
            print("need to fit the model first");
        for case,sd in results.iteritems():
            res[case] = self._get_result(np.asarray(sd),self.p).flatten();
        return res;

class Ch4Model(BaseModel):
    def __init__(self):
        self.p0 = [.8,10,.3,.9,.09,4];
        self.bounds = [(.6,.98),(0,20),(.2,0.7),(0.6,0.98),(.03,.2),(0,10)];
        self.p = None;

    def _get_result(self,X,p):#X a single column vector of sys and dias volume
        Y = np.zeros((X.shape[0],2));
        Y[1::2,0] = np.clip(X[1::2]*p[0]+p[1],4,580);
        Y[::2,0] = np.clip(np.maximum(Y[1::2,0]*p[2], X[::2]*p[3]),4,580);
        Y[:,1] = np.clip(Y[:,0]*p[4]+p[5], 0, 35);
        dele = np.array([[i*2,i*2+1] for i in range(X.shape[0]/2) if X[i*2+1]<40]).reshape((-1))
        if len(dele) > 0:
            Y[dele]=np.nan
        return Y;

    def fit(self, results, train_true):
        x = [];
        y = [];
        count = 0;
        missing = [];
        for idx,row in train_true.iterrows():
            res = results.get(row['Id']);
            if res is None or res[1] < 40:
                missing.append(row['Id']);
                continue
            count+=1;
            x.extend(res);
            y.extend([row['Systole'],row['Diastole']]);
        print("{} cases are used to fit the model".format(count));
        if len(missing)>0:
            print("cases are missing in train: " + ','.join([str(int(m)) for m in missing]));
        x = np.asarray(x);
        y = np.asarray(y);
        ff = minimize(lambda p:analysis.crps_score(self._get_result(x,p),y), self.p0, bounds=self.bounds, options={'gtol':1e-5,'maxiter':500,'eps':1e-3});
        self.p = ff.x;
        print("fitting parameters " + str(self.p));
        print("fitting score " + str(ff.fun));
    
    def predict(self,results):
        res = {};
        if self.p is None:
            print("need to fit the model first");
        for case,sd in results.iteritems():
            res[case] = self._get_result(np.asarray(sd),self.p).flatten();
        return res;


class AverageModel(BaseModel):
    def __init__(self,ll=9.5e-5):
        self.p = None;
        self.ll = ll;

    def _get_result(self,X,p):
        """
        how to deal with nans???
        this code treat them as missing use the same coefficients
        ideally, it should fit another model use only the rest of models
        """
        NR = X.shape[0];
        y = np.zeros((NR,2));
        p = np.asarray(p);
        for i in range(NR):
            preds = np.copy(X[i]).reshape((-1,2));
            err0 = np.copy(preds[:,1]);
            preds[:,1] = err0*p;
            preds = preds[~np.isnan(preds[:,0])];
            if preds.shape[0]==0:
                y[i] = [np.nan,np.nan];
                continue;
            me = np.sum(preds[:,0]/preds[:,1]**2);
            err = np.sum(1.0/preds[:,1]**2);
            me /= err;
            err = 1.0/np.sqrt(err);
            err = np.minimum(np.nanmin(err0),err);
            err *=(1.0 + np.std(preds[:,0])/np.max(preds[:,1])/3)**0.5;
            y[i] = [me,err];
        return y;
            
    def fit(self,preds,train_true):
        N = len(preds);
        print("combine # predictions:" + ','.join([str(len(x)) for x in preds]));
        self.p0 = np.ones(N)*np.sqrt(N);
        X = np.zeros((train_true.shape[0]*2,N*2));
        X[:] = np.nan;
        y = [];
        i = 0;
        for idx,row in train_true.iterrows():
            case = row['Id'];
            y.extend([row['Systole'],row['Diastole']]);
            for j in range(N):
                sede = preds[j].get(case);
                if sede is not None:
                    X[i*2,2*j:2*j+2] = sede[0:2];
                    X[i*2+1,2*j:2*j+2] = sede[2:4];
            i += 1;
        y = np.asarray(y);
        print("init score :{}".format(analysis.crps_score(self._get_result(X,self.p0),y)));
        ff = minimize(lambda p:analysis.crps_score(self._get_result(X,p),y) + self.ll*np.var(p), self.p0, options={'gtol':1e-5,'eps':1e-4,'maxiter':500});
        self.p = ff.x;
        print("fitting parameters " + str(self.p));
        print("fitting score " + str(ff.fun));

    def predict(self,preds):
        print("combine # predictions:" + ','.join([str(len(x)) for x in preds]));
        res = {};
        css = [list(x.keys()) for x in preds];
        css = set(list(itertools.chain.from_iterable(css)));
        N = len(preds);
        assert(N == self.p.size);
        for case in css:
            X = np.zeros((2,2*N));
            X[:] = np.nan;
            for j in range(N):
                sede = preds[j].get(case);
                if sede is not None:
                    X[0,2*j:2*j+2] = sede[0:2];
                    X[1,2*j:2*j+2] = sede[2:4];
            res[case] = self._get_result(X,self.p).flatten();
        return res;

class SaxFilterModel(BaseModel):
    def __init__(self):
        self.p0 = [1.0,1.0,0.05,4,0.05,4];
        self.bounds = [(-0.5,1.8),(-0.5,1.5),(0.03,0.10),(0,10),(0.03,0.10),(0,10)];

        self.p = None;

    def _get_result(self,X,p):#X a single column vector of sys and dias volume
        Y = np.zeros((X.shape[0],2));
        idx = X[:,1]>1;
        ridx = np.logical_not(idx);
        Y[idx,0] = X[idx,0] - np.sqrt(X[idx,0])*p[0];
        Y[ridx,0] = X[ridx,0] - np.sqrt(X[ridx,0])*p[1];
        Y[idx,1] = np.clip(Y[idx,0]*p[2]+p[3],0,25);
        Y[ridx,1] = np.clip(Y[ridx,0]*p[4]+p[5],0,25);
        return Y;

    def fit(self, results,train_true):
        x = [];
        y = [];
        count = 0;
        missing = [];
        for idx,row in train_true.iterrows():
            res = results.get(row['Id']);
            if res is None:
                missing.append(row['Id']);
                continue
            count+=1;
            x.extend(res);
            y.extend([row['Systole'],row['Diastole']]);
        print("{} cases are used to fit the model".format(count));
        if len(missing)>0:
            print("cases are missing: " + ','.join([str(_x) for _x in missing]));
        x = np.asarray(x).reshape((-1,2));
        y = np.asarray(y);
        ff = minimize(lambda p:analysis.crps_score(self._get_result(x,p),y), self.p0, bounds=self.bounds, options={'gtol':1e-5,'maxiter':500,'eps':1e-5});
        self.p = ff.x;
        print("fitting parameters " + str(self.p));
        print("fitting score " + str(ff.fun));
    
    def predict(self,results):
        res = {};
        if self.p is None:
            print("need to fit the model first");
        for case,sd in results.iteritems():
            res[case] = self._get_result(np.asarray(sd).reshape(-1,2),self.p).flatten();
        return res;

class SaxFeatureModel(BaseModel):
    def __init__(self):
        self.p0 = [0.2,-0.2,0.9, 0.5,-0.5,0.5,4];
        self.bounds = [(-0.5,0.5),(-0.5,0.5),(0.0,2.0),\
                (-3.0,3.0),(-3.0,3.0),(-3.0,3.0),(2,10)];

        self.p = None;

    def _get_result(self,X,p):#X a single column vector of sys and dias volume
        Y = np.zeros((X.shape[0],2));
        e1 = (X[:,1]>1)*1.0;
        e2 = (X[:,2]<=7)*1.0;
        e3 = (X[:,3]>1.3)*1.0;
        Y[:,0] = X[:,0] - np.sqrt(X[:,0])*(p[0]*e1+p[1]*e2+p[2])
        Y[:,1] = np.clip(X[:,0]*(p[3]*e1+p[4]*e2+p[5]*e3+p[6])/100+4,4,30);
        return Y;

    def fit(self, results,train_true):
        x = [];
        y = [];
        count = 0;
        missing = [];
        for idx,row in train_true.iterrows():
            res = results.get(row['Id']);
            if res is None:
                missing.append(row['Id']);
                continue
            count+=1;
            x.extend(res);
            y.extend([row['Systole'],row['Diastole']]);
        print("{} cases are used to fit the model".format(count));
        if len(missing)>0:
            print("cases are missing: " + ','.join([str(_x) for _x in missing]));
        x = np.asarray(x).reshape((-1,4));
        y = np.asarray(y);
        ff = minimize(lambda p:analysis.crps_score(self._get_result(x,p),y), self.p0, bounds=self.bounds, options={'gtol':1e-6,'maxiter':500,'eps':1e-5});
        self.p = ff.x;
        print("fitting parameters " + str(self.p));
        print("fitting score " + str(ff.fun));
    
    def predict(self,results):
        res = {};
        if self.p is None:
            print("need to fit the model first");
        for case,sd in results.iteritems():
            res[case] = self._get_result(np.asarray(sd).reshape(-1,4),self.p).flatten();
        return res;
