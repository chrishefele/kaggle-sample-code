import java.lang.*;
import java.util.*;

public class BoardModelErrorCounter {
    
    private TreeMap<Integer, Integer> regErrCounts = new TreeMap<Integer, Integer>(); 
    private BoardModel model;

    public BoardModelErrorCounter(BoardModel model) {
        this.model = model;
        initRegErrCounts(Consts.REGULARIZATIONS);
    }

    public void initRegErrCounts(int[] regs) { 
        regErrCounts = new TreeMap<Integer, Integer>(); 
        for(int i=0; i<regs.length; i++) {
            regErrCounts.put(regs[i], 0);
        }
    }

    public void updateRegErrCounts(int[][] startBoard, int[][] stopBoard) { 
        // for each regularization, and for each cell in the board,count the
        // errors between the predicted startBoard and the actual startBoard
        final int dummy_reg = 0;
        int[][] counts = model.predictStartBoardAndCounts(stopBoard, dummy_reg).second;
        for(Integer reg : regErrCounts.keySet() ) {
            for(int r=0; r<counts.length; r++) {
                for(int c=0; c<counts[r].length; c++) {
                    int cellPrediction = (counts[r][c] > reg) ? 1 : 0 ;
                    if(cellPrediction != startBoard[r][c]) {
                        regErrCounts.put(reg, regErrCounts.get(reg) + 1);
                    }
                }
           }
        }
    }

    public TreeMap<Integer, Integer> getRegErrCounts() {
        return regErrCounts;
    }

} // BoardModelErrorCounter
