import java.math.*;
public class Consts {
    
    static final int BOARD_SIDE = 20;  // board is 20x20 cells

    static final int INIT_DELTA = 5;   // "warm-up" time steps between random 
                                       // init board and the start board

    static final int DELTAS     = 5;   // number of different deltas (1..5) 
                                       // (time-steps between start to stop board)

    static final String TRAIN_CSV_FILE = "../download/train.csv";
    static final String TEST_FILENAME  = "../download/test.csv";
    static final String SUBMISSION_FILE  = "submission.csv";


    static final int PATTERN_TABLE_MAXBITS = 30; // 26bits for 5 simult models, 30bits for 1 model in 8GB

    static final int PATTERN_TABLE_MODPRIME = 
            BigInteger.valueOf(2).pow(PATTERN_TABLE_MAXBITS).nextProbablePrime().intValue();

    static final int PATTERN_TABLE_SIZE = PATTERN_TABLE_MODPRIME + 1; 
    
    static final int NUM_CELL_VALUES  =  3;  // must match the number of X_CELL_VALUE constants below
    static final int SKIP_CELL_VALUE  = -1; 
    static final int DEAD_CELL_VALUE  =  0; 
    static final int ALIVE_CELL_VALUE =  1; 

    static final int[] REGULARIZATIONS = 
            new int[]{-1,0,1,2,3,4,5,6,7,8,9,10,100,1000,10000,100000,1000000};

    static final int[] REGS_VS_DELTA   = new int[]{0, 0, 2, 4, 4, 6}; 

    //static final long RAND_SEED_BOARDMAKER = 12345; 
    //static final long RAND_SEED_TRAINER    = 42; 
    static final long ZOBRIST_SEED_STOP     = 711; 
    static final long ZOBRIST_SEED_POSITION = 117; 

    static final int PRINT_STATUS_INTERVAL = 10000; // print updates after processing N boards

}

