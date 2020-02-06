import socket
if socket.gethostname() == 'Faramir': #for CNN_B
    data_root = '/home/tencia/Documents/data/heart/'
    data_kaggle = data_root + 'kaggle'
    data_sunnybrook = data_root + 'sunnybrook'
    local_root = '/home/tencia/Dropbox/heart/diagnose-heart/'
    data_manual = local_root + 'manual_data'
    data_intermediate = local_root + 'data_intermediate'
    output_dir = local_root + 'CNN_A/output/'
    tencia_output_dir = local_root + 'CNN_B/output/'
else: #for CNN_A
    data_root = "/media/qiliu/share/heart/";
    data_sunnybrook = data_root + '/sunnybrook';
    data_kaggle = data_root;

    local_dir = '/home/qiliu/Documents/Coding/heart/diagnose-heart/';
    manual_data_root = local_dir + 'manual_data'
    data_aug_contours = manual_data_root + '/manual_contours';

    intermediate_dir = local_dir + 'CNN_A';
    params_dir = intermediate_dir + '/params/'
    output_dir = intermediate_dir + '/output/'
    tencia_output_dir = local_dir + 'CNN_B/output'
