#!/usr/bin/python2
import dicom, cv2, re, sys
import os, fnmatch, shutil, subprocess
import numpy as np
sys.path.append('..')
import SETTINGS as c
from PIL import Image
from heart import getAlignImg;
import h5py
import dsb_utils as du;

"""
This script processes (crop from center, rotate, etc..) all 
the sunny-brook dataset images and the hand-labeled images, 
and put them into a single hdf5 file for the CNNs to load and train later
"""

np.random.seed(5678);
SZ = int(sys.argv[1]);

noc = 'L'; #useless, fixed
SAX_SERIES = {
    # challenge training
    "SC-HF-I-1": "0004",
    "SC-HF-I-2": "0106",
    "SC-HF-I-4": "0116",
    "SC-HF-I-10": "0024",
    "SC-HF-I-40": "0134",
    "SC-HF-NI-3": "0379",
    "SC-HF-NI-4": "0501",
    "SC-HF-NI-34": "0446",
    "SC-HF-NI-36": "0474",
    "SC-HYP-1": "0550",
    "SC-HYP-3": "0650",
    "SC-HYP-38": "0734",
    "SC-HYP-40": "0755",
    "SC-N-2": "0898",
    "SC-N-3": "0915",
    "SC-N-40": "0944",
    "SC-HF-I-5": "0156",
    "SC-HF-I-6": "0180",
    "SC-HF-I-7": "0209",
    "SC-HF-I-8": "0226",
    "SC-HF-NI-11": "0270",
    "SC-HF-NI-31": "0401",
    "SC-HF-NI-33":"0424",
    "SC-HF-NI-7": "0523",
    "SC-HYP-37": "0702",
    "SC-HYP-6": "0767",
    "SC-HYP-7": "0007",
    "SC-HYP-8": "0796",
    "SC-N-5": "0963",
    "SC-N-6": "0981",
    "SC-N-7": "1009",
    "SC-HF-I-11": "0043",
    "SC-HF-I-12": "0062",
    "SC-HF-I-9": "0241",
    "SC-HF-NI-12": "0286",
    "SC-HF-NI-13": "0304",
    "SC-HF-NI-14": "0331",
    "SC-HF-NI-15": "0359",
    "SC-HYP-10": "0579",
    "SC-HYP-11": "0601",
    "SC-HYP-12": "0629",
    "SC-HYP-9": "0003",
    "SC-N-10": "0851",
    "SC-N-11": "0878",
    "SC-N-9": "1031"
}


TRAIN_CONTOUR_PATH = os.path.join(c.data_sunnybrook,
                            "Sunnybrook Cardiac MR Database ContoursPart3",
                            "TrainingDataContours")
ONLINE_CONTOUR_PATH = os.path.join(c.data_sunnybrook,
                            "Sunnybrook Cardiac MR Database ContoursPart1",
                            "OnlineDataContours")
VAL_CONTOUR_PATH = os.path.join(c.data_sunnybrook,
                            "Sunnybrook Cardiac MR Database ContoursPart2",
                            "ValidationDataContours")
TRAIN_IMG_PATH = os.path.join(c.data_sunnybrook,
                        "challenge_training")
VAL_IMG_PATH = os.path.join(c.data_sunnybrook,
                        "challenge_validation")
ONLINE_IMG_PATH = os.path.join(c.data_sunnybrook,
                        "challenge_online", "challenge_online")
# creates and hdf5 file from a dataset given a split in the form {'train':(0,n)}, etc
# appears to save in unpredictable order, so order must be verified after creation
def save_hd5py(dataset_dict, destfile, indices_dict_or_numfolds):
    indices_dict = indices_dict_or_numfolds
    if isinstance(indices_dict, int):
        folds = indices_dict
        n = max(len(it) for it in dataset_dict.values())
        fold_n = n // folds
        indices_dict = dict(('fold_{}'.format(i), (i*fold_n, (i+1)*fold_n)) \
                for i in range(folds))
        print indices_dict
    f = h5py.File(destfile, mode='w')
    for name, dataset in dataset_dict.iteritems():
        dat = f.create_dataset(name, dataset.shape, dtype=str(dataset.dtype))
        dat[...] = dataset
    split_dict = dict((k, dict((name, v) for name in dataset_dict.iterkeys()))
            for k,v in indices_dict.iteritems())
    from fuel.datasets.hdf5 import H5PYDataset
    f.attrs['split'] = H5PYDataset.create_split_array(split_dict)
    f.flush()
    f.close()

def shrink_case(case):
    toks = case.split("-")
    def shrink_if_number(x):
        try:
            cvt = int(x)
            return str(cvt)
        except ValueError:
            return x
    return "-".join([shrink_if_number(t) for t in toks])

class Contour(object):
    def __init__(self, ctr_path):
        self.ctr_path = ctr_path
        match = re.search(r"/([^/]*)/contours-manual/IRCCI-expert/IM-0001-(\d{4})-icontour-manual.txt", ctr_path)
        self.case = shrink_case(match.group(1))
        self.img_no = int(match.group(2))
    
    def __str__(self):
        return "<Contour for case %s, image %d>" % (self.case, self.img_no)
    
    __repr__ = __str__
    

def load_contour(contour, img_path):
    filename = "IM-%s-%04d.dcm" % (SAX_SERIES[contour.case], contour.img_no)
    full_path = os.path.join(img_path, contour.case, filename)
    f = dicom.read_file(full_path)
    ctrs = np.loadtxt(contour.ctr_path, delimiter=" ").astype(np.int)
    label = np.zeros(f.pixel_array.shape, dtype=np.uint8)
    cv2.fillPoly(label, [ctrs], 255)
    img,lab = getAlignImg(f,label);
    lx,ly = img.shape;
    assert(lx==ly);
    xm,ym = np.where(lab>127);
    if xm.size<30:
        xm,ym = lx//2,ly//2;
    xm = np.mean(xm);
    ym = np.mean(ym);
    delta = int(lx*0.62)//2;#cut middle 160x160 from 256x256 for sunny brook data
    assert(delta<xm and delta<ym);
    xm,ym,delta = int(xm),int(ym),int(delta);
    img = img[xm-delta:xm+delta,ym-delta:ym+delta];
    lab = lab[xm-delta:xm+delta,ym-delta:ym+delta];
    return cv2.resize(img, (SZ,SZ)), cv2.resize(lab, (SZ,SZ))
    
def get_all_contours(contour_path):
    contours = [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(contour_path)
        for f in fnmatch.filter(files, 'IM-0001-*-icontour-manual.txt')]
    np.random.shuffle(contours)
    print("Number of examples: {:d}".format(len(contours)))
    extracted = map(Contour, contours)
    return extracted

def process_contours(contours, img_path):
    n = len(contours)
    imgs_arr = np.empty((n, 1, SZ, SZ), dtype=np.uint8)
    labels_arr = np.empty((n, 1, SZ, SZ), dtype=np.uint8)
    for idx,ctr in enumerate(contours):
        img, label = load_contour(ctr, img_path)
        imgs_arr[idx,0]=img
        labels_arr[idx,0]=label
    return imgs_arr, labels_arr

contour_paths = [TRAIN_CONTOUR_PATH, VAL_CONTOUR_PATH, ONLINE_CONTOUR_PATH]
image_paths = [TRAIN_IMG_PATH, VAL_IMG_PATH, ONLINE_IMG_PATH]
all_data = []

##!!!!!!NOTICE: train label all has range 0-255!!!

if __name__=='__main__':
    aug_contour_path = os.path.join(c.data_aug_contours, 'contours')
    aug_image_path = os.path.join(c.data_aug_contours, 'images')
# add in manually segmented images first so they're in training set
# labels are zero or one, not 255
    for contour_img in filter(lambda x: 'jpg' in x, os.listdir(aug_contour_path)):
        if 'auto' in contour_img:
            continue
        img = cv2.imread(os.path.join(aug_image_path, contour_img), 0)
        lfile = os.path.join(aug_contour_path, contour_img);
        if 'c_' in contour_img:#labeled image by qi
            label = cv2.imread(lfile[:-3]+'png',0);
            _,label = cv2.threshold(label, 1,255,cv2.THRESH_BINARY_INV)
        else:
            label = cv2.imread(lfile, 0)
            _,label = cv2.threshold(label, 127,255,cv2.THRESH_BINARY_INV)
        #did not rotate for these cases, it might be fine since these align well with my direction
        lx,ly = img.shape;
        assert(lx==ly);
        xm,ym = np.where(label>127);
        if xm.size<30:
            xm,ym = lx//2,ly//2;
        xm = np.mean(xm);
        ym = np.mean(ym);
        delta = int(lx*0.75)//2;#cut middle ~160x160 from 246x246 for Tencia's image
        if not (delta<xm and delta<ym):
            print(xm,ym,lx,"not in the middle: ",contour_img);
            delta = min(xm,ym);
        xm,ym,delta = int(xm),int(ym),int(delta)
        img = img[xm-delta:xm+delta,ym-delta:ym+delta];
        label = label[xm-delta:xm+delta,ym-delta:ym+delta];

        img = cv2.resize(img, (SZ,SZ)).reshape(1,1,SZ,SZ)
        label = cv2.resize(label, (SZ,SZ))
        label = label.reshape(1,1,SZ,SZ);##train label all has range 0-255!!!
        all_data.append([img,label])

    ##add in no contour images!!
    if noc == 'L':
        #with open('nocontour_{}.csv'.format(noc)) as f:
        with open(c.manual_data_root + '/nocontour.csv') as f:
            label = np.zeros((1,1,SZ,SZ),dtype=np.uint8);
            for l in f:
                row = [int(x) for x in l.split(',')];
                case = row[0];
                s = row[1::2];
                t = row[2::2];
                assert(len(s)==len(t));
                dset = du.CNN_Dataset(case,img_size = SZ);
                n = len(s);
                print("add case {} no contour imgs".format(case))
                for i in range(n):
                    img = dset.images[s[i],t[i],0].reshape(1,1,SZ,SZ);
                    all_data.append([img,label]);

    #if noc == 'auto':
    #    import pickle
    #    ddir = c.data_auto_contours+'/size_{}'.format(SZ);
    #    for img_con in filter(lambda x: 'pkl' in x, os.listdir(ddir)):
    #        with open(ddir +'/'+ img_con,'rb') as f:
    #            x = pickle.load(f)
    #            img,label = x[0],x[1]
    #        img = img.reshape(1,1,SZ,SZ);
    #        label = label.reshape(1,1,SZ,SZ);
    #        all_data.append([img,label]);

    for cpath, ipath in zip(contour_paths, image_paths):
        train_ctrs = get_all_contours(cpath)
        imgs, labels = process_contours(train_ctrs, ipath)
        all_data.append([imgs,labels])

    all_imgs = np.concatenate([a[0] for a in all_data], axis=0)
    all_labels = np.concatenate([a[1] for a in all_data], axis=0)
    
#shuffle
    idx = np.arange(all_imgs.shape[0]);
    np.random.shuffle(idx)
    all_imgs = all_imgs[idx];
    all_labels = all_labels[idx];

    n = all_imgs.shape[0]
    print("total number :",n);
    fn = os.path.join(c.data_sunnybrook, 'scd_seg_noc{}_{}.hdf5'.format(noc,SZ))
    save_hd5py({'images': all_imgs, 'labels': all_labels}, fn, 5)
