import os, sys, re, cv2, dicom, fnmatch
import numpy as np
from PIL import Image
import dsb_utils as du
import utils as u
import config as c

np.random.seed(1234)
print 'random state seeded sunnybrook'
img_size = 256

sax_series_dict = {
    'SC-HF-I-1': '0004',
    'SC-HF-I-2': '0106',
    'SC-HF-I-4': '0116',
    'SC-HF-I-5': '0156',
    'SC-HF-I-6': '0180',
    'SC-HF-I-7': '0209',
    'SC-HF-I-8': '0226',
    'SC-HF-I-9': '0241',
    'SC-HF-I-10': '0024',
    'SC-HF-I-11': '0043',
    'SC-HF-I-12': '0062',
    'SC-HF-I-40': '0134',
    'SC-HF-NI-3': '0379',
    'SC-HF-NI-4': '0501',
    'SC-HF-NI-7': '0523',
    'SC-HF-NI-12': '0286',
    'SC-HF-NI-11': '0270',
    'SC-HF-NI-13': '0304',
    'SC-HF-NI-14': '0331',
    'SC-HF-NI-15': '0359',
    'SC-HF-NI-31': '0401',
    'SC-HF-NI-33':'0424',
    'SC-HF-NI-34': '0446',
    'SC-HF-NI-36': '0474',
    'SC-HYP-1': '0550',
    'SC-HYP-3': '0650',
    'SC-HYP-6': '0767',
    'SC-HYP-7': '0007',
    'SC-HYP-8': '0796',
    'SC-HYP-9': '0003',
    'SC-HYP-10': '0579',
    'SC-HYP-11': '0601',
    'SC-HYP-12': '0629',
    'SC-HYP-37': '0702',
    'SC-HYP-38': '0734',
    'SC-HYP-40': '0755',
    'SC-N-2': '0898',
    'SC-N-3': '0915',
    'SC-N-5': '0963',
    'SC-N-6': '0981',
    'SC-N-7': '1009',
    'SC-N-9': '1031',
    'SC-N-10': '0851',
    'SC-N-11': '0878',
    'SC-N-40': '0944',
}

tr_contour_path = os.path.join(c.data_sunnybrook, 
        'Sunnybrook Cardiac MR Database ContoursPart3',
        'TrainingDataContours')
onl_contour_path = os.path.join(c.data_sunnybrook,
        'Sunnybrook Cardiac MR Database ContoursPart1',
        'OnlineDataContours')
val_contour_path = os.path.join(c.data_sunnybrook,
        'Sunnybrook Cardiac MR Database ContoursPart2',
        'ValidationDataContours')
tr_img_path = os.path.join(c.data_sunnybrook, 'challenge_training')
val_img_path = os.path.join(c.data_sunnybrook, 'challenge_validation')
onl_img_path = os.path.join(c.data_sunnybrook, 'challenge_online', 'challenge_online')

def shrink_case(case):
    toks = case.split('-')
    def shrink_if_number(x):
        try:
            cvt = int(x)
            return str(cvt)
        except ValueError:
            return x
    return '-'.join([shrink_if_number(t) for t in toks])

class Contour(object):
    def __init__(self, ctr_path):
        self.ctr_path = ctr_path
        match = re.search( \
                r'/([^/]*)/contours-manual/IRCCI-expert/IM-0001-(\d{4})-icontour-manual.txt', \
                ctr_path)
        self.case = shrink_case(match.group(1))
        self.img_no = int(match.group(2))
    
    def __str__(self):
        return '<Contour for case %s, image %d>' % (self.case, self.img_no)
    
    __repr__ = __str__

def load_contour(contour, img_path):
    filename = 'IM-%s-%04d.dcm' % (sax_series_dict[contour.case], contour.img_no)
    full_path = os.path.join(img_path, contour.case, filename)
    f = dicom.read_file(full_path)
    img = f.pixel_array.astype(np.uint8)
    ctrs = np.loadtxt(contour.ctr_path, delimiter=' ').astype(np.int)
    label = np.zeros_like(img, dtype='uint8')
    cv2.fillPoly(label, [ctrs], 1)
    return cv2.resize(img, (img_size,img_size)), cv2.resize(label, (img_size,img_size))
    
def get_all_contours(contour_path):
    contours = [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(contour_path)
        for f in fnmatch.filter(files, 'IM-0001-*-icontour-manual.txt')]
    np.random.shuffle(contours)
    print('Number of examples: {:d}'.format(len(contours)))
    extracted = map(Contour, contours)
    return extracted

def process_contours(contours, img_path):
    n = len(contours)
    imgs_arr = np.empty((n, 1, img_size, img_size), dtype=np.uint8)
    labels_arr = np.empty((n, 1, img_size, img_size), dtype=np.uint8)
    for idx,ctr in enumerate(contours):
        img, label = load_contour(ctr, img_path)
        imgs_arr[idx,0]=img
        labels_arr[idx,0]=label
    return imgs_arr, labels_arr

def process_data_hdf5():
    contour_paths = [tr_contour_path, val_contour_path, onl_contour_path]
    image_paths = [tr_img_path, val_img_path, onl_img_path]
    all_data = []

    for contour_path, img_path in zip(contour_paths, image_paths):
        train_ctrs = get_all_contours(contour_path)
        imgs,labels = process_contours(train_ctrs, img_path)
        all_data.append([imgs,labels])

    # add in manually segmented images, labels in {0,1}
    aug_contour_path = os.path.join(c.data_manual, 'manual_contours', 'contours')
    aug_image_path = os.path.join(c.data_manual, 'manual_contours', 'images')
    for cfn in [fn_ for fn_ in os.listdir(aug_contour_path) if 'jpg' in fn_]:
        if 'auto' in cfn:
            continue
        dcm_img = cv2.imread(os.path.join(aug_image_path, cfn), 0)
        dcm_img = cv2.resize(dcm_img, (img_size, img_size)).reshape(1, 1, img_size, img_size)
        contour_img = cv2.imread(os.path.join(aug_contour_path, cfn), 0)
        contour_img = cv2.resize(contour_img, (img_size, img_size))
        _,contour_img = cv2.threshold(contour_img, 127, 255,cv2.THRESH_BINARY_INV)
        contour_img = contour_img.reshape(1, 1, img_size, img_size) / 255
        all_data.append([dcm_img, contour_img])

    ##add in no contour images!!
    with open(os.path.join(c.data_manual, 'nocontour_tencia.csv')) as f:
        label = np.zeros((1,1,img_size,img_size), dtype=np.uint8);
        for l in f:
            row = [int(x) for x in l.split(',')];
            case = row[0];
            s = row[1::2];
            t = row[2::2];
            assert(len(s)==len(t));
            dset = du.CNN_Dataset(case, img_size=img_size)
            n = len(s);
            print("add case {} no contour imgs".format(case))
            for i in range(n):
                img = dset.images[s[i],t[i],0].reshape(1,1,img_size,img_size)
                all_data.append([img,label])

    np.random.shuffle(all_data)

    all_imgs = np.concatenate([a[0] for a in all_data], axis=0)
    all_labels = np.concatenate([a[1] for a in all_data], axis=0)

    n = all_imgs.shape[0]
    fn = os.path.join(c.data_intermediate, 'scd_seg_{}.hdf5'.format(img_size))
    if os.path.exists(fn):
        os.remove(fn)
    u.save_hd5py({'images': all_imgs, 'labels': all_labels}, fn, 5)
