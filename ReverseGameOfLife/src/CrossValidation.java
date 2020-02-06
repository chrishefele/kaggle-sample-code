import java.io.*;
import java.util.*;

public class CrossValidation {

    public ArrayList<BoardPair> crossValBoards = new ArrayList<BoardPair>();

    public CrossValidation() {
        System.out.println("Reading cross-validation boards from: "+Consts.TRAIN_CSV_FILE);
        crossValBoards = BoardFileIO.readFile(Consts.TRAIN_CSV_FILE, "train");
        System.out.println("Finished reading: "+Consts.TRAIN_CSV_FILE);
    }

    public int boardErr(int[][] boardA, int[][] boardB) {
        int err = 0;
        for(int r=0; r<boardA.length; r++) {
            for(int c=0; c<boardA[r].length; c++) {
                if(boardA[r][c] != boardB[r][c]) {
                    ++err;
                }
            }
        }
        return err;
    }

    public void crossValidate(BoardModel[] boardModels) {
        int[] nboards = new int[Consts.DELTAS+1];
        BoardModelErrorCounter[] errCounters = new BoardModelErrorCounter[Consts.DELTAS+1];

        for(int delta=1; delta<=Consts.DELTAS; delta++) {
            errCounters[delta] = new BoardModelErrorCounter(boardModels[delta]);
        }
        System.out.println("Cross validating...\n");
        for(BoardPair bp : crossValBoards) {
            nboards[bp.delta]++;
            errCounters[bp.delta].updateRegErrCounts(bp.startBoard, bp.stopBoard);
            if(bp.row_id % Consts.PRINT_STATUS_INTERVAL == 0) {
                System.out.print(" "+bp.row_id);
            }
        }
        System.out.println("\nCROSS VALIDATION RESULTS\n");
        for(int delta=1; delta<=Consts.DELTAS; delta++) {
            long nExamplesTrained = boardModels[delta].getNumExamplesTrained();
            String radius         = boardModels[delta].getRadius(); 
            TreeMap<Integer,Integer> regErrCounts = errCounters[delta].getRegErrCounts();
            for(Integer reg : regErrCounts.keySet()) {
                Integer errCount = regErrCounts.get(reg);
                double errPct = 1. * errCount / 
                                (nboards[delta] * Consts.BOARD_SIDE*Consts.BOARD_SIDE); 
                System.out.format("delta %2d ", delta);
                System.out.format("errPct %8.5f ", errPct);
                System.out.format("reg %10d ", reg);
                System.out.printf("radius %12s ", radius);
                System.out.format("nTrained %12d ", nExamplesTrained);
                System.out.format("errs %9d ", errCount);
                System.out.format("nboards %8d ", nboards[delta]);
                System.out.format("%n");
            }
        }
    }

} // CrossValidation

