#!/usr/bin/python2
import pandas as pd;
import SETTINGS as sts;
from fitting_models import *
import analysis

def train_sex_age_model(info, train_true):
    ##train sex_age model
    print(" ------ train sex age model :");
    sa_model = SexAgeModel();
    sa_model.fit(info,train_true);
    sa_predict = sa_model.predict(info);
    analysis.evaluate_pred(sa_predict, train_true);
    return sa_predict;

def train_ch4_model(ch4_data, train_true):
    #tencia's 4-ch model, implemented 02/27
    print(" ---- train ch4 model :");
    ch4_model = Ch4Model();
    ch4_model.fit(ch4_data, train_true);
    ch4_pred = ch4_model.predict(ch4_data);
    analysis.evaluate_pred(ch4_pred, train_true);
    return ch4_pred;

def train_sax_model(areas_all,train_true, version,cleaner=[]):
    print(" ---- train sax model :");
    sax_model = SaxModel(version=version);
    result = analysis.get_preliminary_volume(areas_all,cleaner=cleaner);
    sax_model.fit(result,train_true);
    sax_predict = sax_model.predict(result);
    analysis.evaluate_pred(sax_predict, train_true);
    return sax_predict;

def train_sax_cnt_model(areas_all, cont_all, train_true,version=2,cleaner=[]):
    #sax model method2, use contour compeleteness to filter result
    print(" ---- train sax countour model :");
    cnt_sax_model = SaxModel(version=version);
    cnt_result = analysis.get_preliminary_volume_cnt(areas_all, cont_all,cleaner=cleaner);
    cnt_sax_model.fit(cnt_result,train_true);
    cnt_sax_predict = cnt_sax_model.predict(cnt_result);
    analysis.evaluate_pred(cnt_sax_predict, train_true);
    return cnt_sax_predict;

def train_sax_cnt_filter_model(areas_all, cont_all, train_true,cleaner=[]):
    print(" ---- train sax countour filter model :");
    cnt_result = analysis.get_preliminary_volume_cnt_filter(areas_all,cont_all,cleaner=cleaner);
    cnt_sax_model = SaxFilterModel();
    cnt_sax_model.fit(cnt_result,train_true);
    cnt_sax_predict = cnt_sax_model.predict(cnt_result);
    analysis.evaluate_pred(cnt_sax_predict, train_true);
    return cnt_sax_predict;

def train_oneslice_model(areas_all,train_true):
    #train OneSliceModel using CNN_B result
    print(" --- train oneslice model :");
    oneslice_model = OneSliceModel();
    oneslice_model.fit(areas_all,train_true);
    oneslice_predict = oneslice_model.predict(areas_all);
    analysis.evaluate_pred(oneslice_predict, train_true);
    return oneslice_predict;

def build_default_model(oneslice_pred, ch4_pred, sa_predict,p_1 = 0.6):
    #p_1 one slice model percentage
    print(" --- building default model :");
    default_pred = {};
    def _bdm_ave(x1,x2,x0):
        if np.isnan(x1[0]):
            return x0 if np.isnan(x2[0]) else x2;
        elif np.isnan(x2[0]):
            return x1;
        return np.asarray([x1[0]*p_1 + x2[0]*(1-p_1),min(x1[1],x2[1])]);

    for case,value in sa_predict.iteritems():
        pred1 = oneslice_pred.get(case);
	pred2 = ch4_pred.get(case);
        if pred1 is None:
            pred1 = np.zeros(4);
            pred1[:] = np.nan;
        if pred2 is None:
            pred2 = np.zeros(4);
            pred2[:] = np.nan;
        x = np.zeros(4);
        x[0:2] = _bdm_ave(pred1[0:2],pred2[0:2],value[0:2]);
        x[2:4] = _bdm_ave(pred1[2:4],pred2[2:4],value[2:4]);
        default_pred[case] = x;
    return default_pred;

if __name__ == '__main__':
    cleaner = [0,1,2]; #set to [] to turn it off
    #####Load all data, same in the test code, but we can filter out train in train and test for test
    info = pd.read_csv(sts.output_dir + '/info.csv')
    ch4_data = { int(r[0]):(r[1], r[2]) for _,r in 
          pd.read_csv(sts.tencia_output_dir+'/ch4_volumes_map.csv', header=False).iterrows()};
    #CNN_B results
    tencia_files = ['pMS','p1090'];
    tencia_areas = [analysis.get_cnn_results(sts.tencia_output_dir+'/areas_map_{}.csv'.format(x)) for x in tencia_files];
    #CNN_A results
    qifiles = [ 'v1_p2090_size256_ss100_nocL_tag3_2norm',
            'v2_p2090_size196_ss100_nocL_tag6_2norm',
            'v1_p2090_size256_ss150_nocL_tag10_2norm',
            'v2_p2090_size196_ss150_nocL_tag11_2norm',
            'v1_p2090_size256_ss200_nocL_tag5_2norm',
            'v2_p2090_size196_ss200_nocL_tag7_2norm',
            'v1_p2090_size256_ss75_nocL_tag12_2norm',
            'v2_p2090_size196_ss75_nocL_tag13_2norm',
            ];
    qi_areas = [analysis.get_cnn_results(sts.output_dir +"/areas_map_{}.csv".format(v)) for v in qifiles];
    qi_cnts = [analysis.get_cnn_results(sts.output_dir +"/contour_portion_{}.csv".format(v)) for v in qifiles];

    train_true = pd.read_csv(sts.data_kaggle + '/train_valid.csv');#append validate result to here once released
    Ntrain = train_true.shape[0];#500, becomes 700 when validate data released
    print("number of train cases is {}".format(Ntrain));
    
    filter_ll = -2000;
    #### train models,
    ########### default models
    sa_predict = train_sex_age_model(info, train_true);
    ch4_predict = train_ch4_model(ch4_data, train_true);
    pick = [0,1];
    qi_best,qi_best_cont = analysis.take_best_contour([qi_areas[i] for i in pick],[qi_cnts[i] for i in pick],method=1, filter_ll = filter_ll);
    oneslice_pred = train_oneslice_model(qi_best,train_true);
    # fit the fall back model, a combination of oneslice_model and 4-ch model, 
    # if it still fails use the sex-age model
    # 0.6 * oneslice_predict + 0.4 * ch4_predict; (use fixed 0.6, 0.4)
    default_pred = build_default_model(oneslice_pred, ch4_predict, sa_predict);
    analysis.evaluate_pred(default_pred, train_true);

    ########## sax based CNN models

    tencia_best = analysis.take_best(tencia_areas, method=2,filter_ll=-1100);
    tencia_predict = train_sax_model(tencia_best, train_true, version = 2);

    pick = [0,1];
    qi_best,qi_best_cont = analysis.take_best_contour([qi_areas[i] for i in pick],[qi_cnts[i] for i in pick],method=1, filter_ll=filter_ll);
    qi_sax_pred = train_sax_model(qi_best,train_true, version = 2, cleaner = cleaner);
    qi_sax_cnt_pred = train_sax_cnt_model(qi_best, qi_best_cont, train_true,version=2, cleaner = cleaner);
    qi_sax_filter_pred = train_sax_cnt_filter_model(qi_best,qi_best_cont,train_true, cleaner = cleaner);

    pick = [2,3];
    qi_best,qi_best_cont = analysis.take_best_contour([qi_areas[i] for i in pick],[qi_cnts[i] for i in pick],method=3,filter_ll=filter_ll);
    qi_sax_pred2 = train_sax_model(qi_best,train_true, version = 2, cleaner = cleaner);
    qi_sax_cnt_pred2 = train_sax_cnt_model(qi_best, qi_best_cont, train_true,version=2, cleaner = cleaner);
    qi_sax_filter_pred2 = train_sax_cnt_filter_model(qi_best,qi_best_cont,train_true, cleaner = cleaner);

    pick = [4,5];
    qi_best,qi_best_cont = analysis.take_best_contour([qi_areas[i] for i in pick],[qi_cnts[i] for i in pick],method=1,filter_ll = filter_ll);
    qi_sax_pred3 = train_sax_model(qi_best,train_true, version = 2, cleaner = cleaner);
    qi_sax_cnt_pred3 = train_sax_cnt_model(qi_best, qi_best_cont, train_true,version=2, cleaner = cleaner);
    qi_sax_filter_pred3 = train_sax_cnt_filter_model(qi_best,qi_best_cont,train_true, cleaner = cleaner);

    pick = [6,7];
    qi_best,qi_best_cont = analysis.take_best_contour([qi_areas[i] for i in pick],[qi_cnts[i] for i in pick],method=3,filter_ll = filter_ll);
    qi_sax_pred4 = train_sax_model(qi_best,train_true, version = 2, cleaner = cleaner);
    qi_sax_cnt_pred4 = train_sax_cnt_model(qi_best, qi_best_cont, train_true,version=2, cleaner = cleaner);
    qi_sax_filter_pred4 = train_sax_cnt_filter_model(qi_best,qi_best_cont,train_true, cleaner = cleaner);
    
    # fit the combined model based on the cnn-sax models.
    # when it fails, fall to the previously fitted fall back model
    print(" --------- average models --");
    #Submit V9
    all_models = [qi_sax_pred,qi_sax_pred2,qi_sax_pred3,\
            qi_sax_cnt_pred, qi_sax_cnt_pred2,qi_sax_cnt_pred3,\
            qi_sax_filter_pred, qi_sax_filter_pred2,qi_sax_filter_pred3,\
            qi_sax_pred4,qi_sax_cnt_pred4,qi_sax_filter_pred4,\
            tencia_predict,default_pred];
    ave_model = AverageModel(ll = 1.0e-4);
    ave_model.fit(all_models,train_true);
    ave_model.set(ave_model.p*1.1);#inflate 10%
    ave_pred = ave_model.predict(all_models);
    
    #apply default model when it fails
    final_pred = analysis.fill_default(ave_pred, default_pred);
    analysis.evaluate_pred(final_pred, train_true);

    #this is for the test part, the test cases are also calculated in the above trainning process
    #we might want to save the parameters of the models, and code another script to calculate the test cases. These fittings are very quick anyway.
    analysis.make_submit(final_pred, 701, 1140, "test"); #inclusive
    analysis.save_intermediate(final_pred, 1, 1140, "test"); #raw 
