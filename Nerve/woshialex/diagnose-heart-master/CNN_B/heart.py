import numpy as np
import dicom
import json
import os
import random
import re
import shutil
import sys
from matplotlib import image
from scipy.ndimage import label
from scipy.ndimage.morphology import binary_erosion
from scipy.fftpack import fftn, ifftn
from scipy.signal import argrelmin, correlate
from scipy.spatial.distance import euclidean
from scipy.stats import linregress
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline
from collections import Counter;
from PIL import Image,ImageDraw;
from skimage import exposure;
import config;
import dsb_utils as du

debug=False;

from scipy.misc import imrotate;
def getAlignImg(t,label = None):#!!!notice, only take uint8 type for the imrotate function!!!
    print 'CALLING GET_ALIGN'
    f = lambda x:np.asarray([float(a) for a in x]);
    o = f(t.ImageOrientationPatient);
    o1 = o[:3];
    o2 = o[3:];
    oh = np.cross(o1,o2);
    or1 = np.asarray([0.6,0.6,-0.2]);
    o2new = np.cross(oh,or1);
    theta = np.arccos(np.dot(o2,o2new)/np.sqrt(np.sum(o2**2)*np.sum(o2new**2)))*180/3.1416;
    theta = theta * np.sign(np.dot(oh,np.cross(o2,o2new)));
    im_max = np.percentile(t.pixel_array.flatten(),99);
    res = imrotate(np.array(np.clip(np.array(t.pixel_array,dtype=np.float)/im_max*256,0,255),
        dtype=np.uint8),theta);
    if label is None:
        return res;
    else:
        lab = imrotate(label,theta);
        return res,lab

def getM(t):
    f = lambda x:np.asarray([float(a) for a in x]);
    try:
        o = f(t.ImageOrientationPatient);
        o1 = o[:3];
        o2 = o[3:];
        c = f(t.ImagePositionPatient);
        s = f(t.PixelSpacing);
    except Exception as e:
        print("!!ERROR in getM",e);
        return None;
    return (o1*s[0],o2*s[1],c);  #M[0] and M[1] is proportional to the direction
   
def getPos(M,i,j):
    return M[0]*i+M[1]*j+M[2];

def getSlocation(M_out):
    xyz = np.array([0,0,0]);
    d = np.cross(M_out[0],M_out[1]);
    MM = np.stack((M_out[0],M_out[1],d)).T;
    r = np.linalg.solve(MM,xyz-M_out[2]);
    return r[2]*np.sqrt(np.sum(d**2));

def getIdx(M_out,M_in,i,j):
    #i,j on plane M_in is index m,n on plane m_out, m_in and m_out should be parallel
    #check parallel
    d = np.cross(M_in[0],M_in[1]);
    d2 = np.cross(M_out[0],M_out[1]);
    p = np.sum(d*d2)/np.sqrt(np.sum(d**2)*np.sum(d2**2));
    if np.abs(1.0-p)>1e-3:
        print("!!!ERROR, plane is not parallel");
        return i,j;
    #find the index
    xyz = getPos(M_in,i,j);
    MM = np.stack((M_out[0],M_out[1],d2)).T;
    r = np.linalg.solve(MM,xyz-M_out[2]);
    return int(r[0]),int(r[1]);

class Dataset(object):
    dataset_count = 0

    def __init__(self, directory, subdir, aligned=False):
        self.aligned=aligned
        self.img_L = 0;
        # deal with any intervening directories
        while True:
            subdirs = next(os.walk(directory))[1]
            if len(subdirs) == 1:
                directory = os.path.join(directory, subdirs[0])
            else:
                break

        slices = []
        for s in subdirs:
            m = re.match("sax_(\d+)", s)
            if m is not None:
                slices.append(int(m.group(1)))
        
        slices_map = {}
        slices_ver = {}
        first = True
        times = []
        for s in slices:
            files = next(os.walk(os.path.join(directory, "sax_%d" % s)))[2]
            offset = None
            
            tmax = 0;
            version = [];
            for f in files:
                m = re.match("IM-(\d{4,})-(\d{4})\.dcm", f)
                if m is None:#has version number
                    m = re.match("IM-(\d{4,})-(\d{4})-(\d{4})\.dcm", f);
                    if m is not None:
                        version.append(int(m.group(3)));
                if m is not None:
                    ti = int(m.group(2));
                    if first:
                        times.append(ti)
                    if ti>tmax: #keep track max time (some has less than 30 images)
                        tmax = ti;
                    if offset is None:
                        offset = int(m.group(1))

            if first:
                times = sorted(np.unique(times))
            first = False
            version = list(np.unique(version));
            if tmax<times[-1]:
                print("WARNING, reduced time slices!");
                times = [t for t in times if t<=tmax];
            slices_map[s] = offset
            if len(version)==0:
                version = [-1];
            slices_ver[s] = version;

        self.directory = directory
        self.time = times;
        #self.slices = slices;
        self.slices_map = slices_map
        self.slices_ver = np.asarray([(s[0],x) for s in slices_ver.items() for x in s[1]]); #all the real slices
        Dataset.dataset_count += 1;
        self.name = subdir
        N = self.slices_ver.shape[0];
        self.slocation = np.zeros(N);
        self.area_multiplier = np.zeros(N);

        if len(self.slices_ver)<1 or len(self.time)<1:
            print("no data to load");
            return

        def getage(s):
            if s in [None,'']:
                return np.nan;
            if s[-1]=='Y':
                return int(s[:-1])
            elif s[-1]=='M':
                return int(s[:-1])/12.0;
            elif s[-1]=='W':
                return int(s[:-1])/52.0;
            else:
                print("what is this? ",s);
                return np.nan;

        #print(self.slices_ver)
        f1 = self._filename(self.slices_ver[0][0], self.time[0],self.slices_ver[0][1])
        d1 = dicom.read_file(f1)

        self.info = [getage(d1.PatientAge),d1.PatientSex];

    def _filename(self, s, t, v):
        aux = '';
        if v>=0:
            aux = '-%04d'%(v);
        return os.path.join(self.directory,"sax_%d" % s, "IM-%04d-%04d%s.dcm" % (self.slices_map[s], t,aux))

    def _read_dicom_image(self, sv, t):
        filename = self._filename(sv[0],t,sv[1]);
        d = dicom.read_file(filename)
        if self.aligned:
            img = getAlignImg(d)
            res = np.array(img,dtype=np.float)
            midx = tuple(sv);

            shift  = np.array([0,0]);
            #crop the center
            if res.shape[0]>res.shape[1]:
                s = (res.shape[0]-res.shape[1])//2;
                res = res[s:s+res.shape[1],:];
                shift[1] = s;
            else:
                s = (res.shape[1]-res.shape[0])//2;
                res = res[:,s:s+res.shape[0]];
                shift[0] = s;

            #crop or stretch to the same size
            if self.img_L>0 and (res.shape[0] != self.img_L):
                #print("crop or fill",filename);
                if res.shape[0]>self.img_L:#because h=w after crop
                    s = (res.shape[0]-self.img_L)//2;
                    res = res[s:s+self.img_L,s:s+self.img_L];
                    shift = shift + s;
                else:
                    s = (self.img_L-res.shape[0])//2;
                    res2 = np.zeros((self.img_L,self.img_L));
                    res2[s:s+res.shape[0],s:s+res.shape[0]] = res;
                    res = res2;
                    shift = shift - s;

                if t==self.time[0]:
                    m = self.M[midx];
                self.M[midx] = (m[0],m[1],getPos(m,shift[0],shift[1]));
            return res;
        else:
            img = du.crop_resize(d.pixel_array.astype('int'), self.img_L)
            return img


    #example code, check distance of two planes (even if one is rotated and shifted)
    #x =getPos(M1,50,50);
    #ii = getIdx(M2,M1,50,50);
    #y = getPos(M2,ii[0],ii[1]);
    #np.sqrt(np.sum((y-x)**2));
    

    def _read_all_dicom_images(self):
        N = self.slices_ver.shape[0]
        if N<3:
            print("WARN!! not enough slices to read!");
            return

        sh = np.zeros((N,2));
        i = 0;
        self.M = {};
        oldslocation = np.zeros(N);
        d = np.zeros(N);
        ref_d = np.array([-1.4,1.0,0.8]);
        for s,v in self.slices_ver:
            x = dicom.read_file(self._filename(s,self.time[0],v));
            oldslocation[i] = x.SliceLocation;
            (a, b) = x.PixelSpacing
            (a, b) = (float(a), float(b))
            self.area_multiplier[i] = a*b;
            sh[i] = x.pixel_array.shape;
            m = getM(x);
            self.M[(s,v)] = m;
            dire = np.cross(m[0],m[1]);
            d[i] = np.corrcoef(dire,ref_d)[0,1];
            self.slocation[i] = getSlocation(m);
            i += 1;

        dcommon = np.median(d);
        if dcommon<0:
            print("!!!Warn Flipped axis");
            self.slocation = - self.slocation;
        idx = (np.abs(d - dcommon)>1e-5);
        if np.sum(idx)>0:
            print("WARN, some slices are non parallel, remove it!",self.slices_ver[idx]);
            idx = np.logical_not(idx);
            self.slocation = self.slocation[idx];
            self.area_multiplier = self.area_multiplier[idx];
            self.slices_ver = self.slices_ver[idx];
            oldslocation = oldslocation[idx];

        #do some checking with the slocation
        #should be 100% correlated
        if np.abs(np.abs(np.corrcoef(self.slocation,oldslocation)[0,1])-1)>1e-3:
            print("!!!Error, check, slocation calculated is different");
            print(oldslocation)
            print(self.slocation)
        #slice distance should be the same
        if np.abs(np.max(self.slocation)-np.min(self.slocation) - \
                (np.max(oldslocation)-np.min(oldslocation)))>0.1:
            print("!!!Error, check, slice separation is different");


        c = Counter([(t[0],t[1]) for t in sh]);
        img_shape = c.most_common()[0][0];
        keep = ((sh[:,0]==img_shape[0]) & (sh[:,1]==img_shape[1]));
        #if np.sum(np.logical_not(keep))>0:
        #    print("size does not match removed:",self.slices_ver[np.logical_not(keep)]);
        #    self.slices_ver = self.slices_ver[keep];
        #    self.slocation = self.slocation[keep];
        #    self.area_multiplier = self.area_multiplier[keep];

        # will crop the center 
        self.img_L = int(np.min(img_shape));

        #sort by slice location
        idx = np.argsort(self.slocation);
        self.slocation = self.slocation[idx];
        self.area_multiplier = self.area_multiplier[idx];
        self.slices_ver = self.slices_ver[idx];

        rmlist = np.zeros(len(self.slocation),dtype=np.bool);
        #remove duplicate ones,keep the original continous ones to avoid shift of the position
        p = 0;
        for i in range(1,len(self.slocation)):
            if self.slocation[i]-self.slocation[p]<2:
                sn1 = self.slices_ver[i];
                sn2 = self.slices_ver[p];
                if np.sum(np.abs(self.slices_ver[np.logical_not(rmlist),0]-sn1[0]))>=np.sum(np.abs(self.slices_ver[np.logical_not(rmlist),0]-sn2[0])) and sn1[1]<=sn2[1]:
                    rmlist[i] = True;
                else:
                    rmlist[p] = True;
                    p = i;
            else:
                p = i;

        if np.sum(rmlist)>0 and debug:
            print("removed slices because of reduandancy: ",self.slices_ver[rmlist])

        idx = np.logical_not(rmlist);
        self.slocation = self.slocation[idx];
        self.area_multiplier = self.area_multiplier[idx];
        self.slices_ver = self.slices_ver[idx];

        self.images = np.array([[self._read_dicom_image(sv,t)
                                 for t in self.time]
                                for sv in self.slices_ver])

    def load(self):
        self._read_all_dicom_images()

    def getxydinit(self):
        Nsax = self.slices_ver.shape[0];
        Nsaxmid = Nsax//2;
        imgs = self.images[max(0,Nsaxmid-2):min(Nsax-1,Nsaxmid+2)];
        p10,p90 = np.percentile(imgs,(10,90));
        imgs = exposure.rescale_intensity(imgs, in_range=(p10, p90));
        imgs = imgs/imgs.max();
        x=np.mean(np.std(imgs,axis=1),axis=0);

        lx, ly = self.images[0][0].shape;
        xm,ym,delta = lx//2,ly//2,min(lx*2//5,ly*2//5);
        cut = np.percentile(x,95);
        img_tmp = Image.new('L', x.shape[::-1], 0)
        ImageDraw.Draw(img_tmp).ellipse((ym-delta,xm-delta,ym+delta,xm+delta), outline=1, fill=1)
        mask = np.array(img_tmp);
        y=(x>cut) & (mask>0.5);
        xm,ym = np.where(y);
        delta = (np.std(xm)+np.std(ym));
        xm = np.mean(xm);
        ym = np.mean(ym);
        delta = 1.2*max(60/np.sqrt(self.area_multiplier[Nsaxmid]),delta);
        delta = min(delta,xm,ym,lx-xm,ly-ym);

        img_tmp = Image.new('L', x.shape[::-1], 0)
        ImageDraw.Draw(img_tmp).ellipse((ym-delta,xm-delta,ym+delta,xm+delta), outline=1, fill=1)
        mask = np.array(img_tmp);
        y=(x>cut) & (mask>0.5);
        xm,ym = np.where(y);
        delta = (np.std(xm)+np.std(ym));
        xm = np.mean(xm);
        delta = max(50/np.sqrt(self.area_multiplier[Nsaxmid]),delta);
        ym = np.mean(ym)+delta/7;
        #move to right a little bit if it is dark a the point
        xm,ym,delta = int(xm),int(ym),int(delta);
        xms = [(xm,ym),(xm,ym+6),(xm+6,ym+6),(xm-6,ym+6)];
        N = len(xms);
        b = np.zeros(N);
        for i in range(N):
            b[i] = max(np.mean(self.images[Nsaxmid,0,xms[i][0]-4:xms[i][0]+4,xms[i][1]-4:xms[i][1]+4]),\
                np.mean(self.images[Nsaxmid,10,xms[i][0]-4:xms[i][0]+4,xms[i][1]-4:xms[i][1]+4]));
        i = np.argmax(b);
        xm,ym = xms[i];
        
        delta = delta*config.heart_delta_multiplier;
        xm,ym,delta = int(xm),int(ym),int(delta);
        delta = min(delta,xm,ym,lx-xm,ly-ym);
        return xm,ym,delta;
