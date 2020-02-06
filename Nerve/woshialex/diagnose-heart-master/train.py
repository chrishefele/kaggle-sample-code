def train_tencia_model():
    from .CNN_B import sunnybrook, segfcn, ch4
    sunnybrook.process_data_hdf5()
    segfcn.train_model()
    segfcn.evaluate()
    ch4.process_data()
    ch4.train_model()
    ch4.evaluate()

def main():
    train_tencia_model()

if __name__ == '__main__':
    main()
