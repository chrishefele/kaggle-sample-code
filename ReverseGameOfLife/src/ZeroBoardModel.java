import java.io.*;
import java.lang.*;
import java.util.*;

public class ZeroBoardModel extends BoardModel {

    private int   delta;
    private double radiusStop = 0;
    private long numExamplesTrained = 0; 

    public ZeroBoardModel(int delta) {
        this.delta = delta;
        System.out.print( "Initializing ZeroBoardModel: ");
        System.out.print("delta "+delta+" ");
        System.out.println("radiusStop "+radiusStop);
    }

    public void saveModel(String countsFilename) {
        // serialize counts & write to file
        System.out.println("ZeroBoardModel: Mock saving model counts to: "+countsFilename);
    }

    public void loadModel(String countsFilename) {
        // unserialize counts & write to file
        System.out.println("ZeroBoardModel: Mock reading model counts from: "+countsFilename);
    } 

    public void printModelStats() {
        System.out.print("Pattern Counts:");
        printModelStatsCommon(new int[1]);
    }

    public void printModelStatsCommon(int[] patternCountTable) {
        int pos, neg, zero, tot;
        pos = neg = zero = 0;
        tot = pos + neg + zero; 
        System.out.println("delta: "+delta+" pos: "+pos+" neg: "+neg+" zero: "+zero+" tot: "+tot);
        //System.out.println("");
    }
    
    public void addExample(int[][] startBoard, int[][] stopBoard) {
       ++numExamplesTrained; 
    }

    public long getNumExamplesTrained() {
        return numExamplesTrained;
    }

    public String getRadius() {
        return ""+radiusStop ;
    }

    public Tuple2<int[][], int[][]>  predictStartBoardAndCounts(int[][] stopBoard, int reg) {
        final int nrows = stopBoard.length;
        final int ncols = stopBoard[0].length ; // inboard assumed non-ragged
        int[][]  startBoard       = new int[nrows][ncols]; 
        int[][]  startBoardCounts = new int[nrows][ncols];
        return new Tuple2<int[][], int[][]>(startBoard, startBoardCounts);
    }


    public int[][] predictStartBoard( int[][] stopBoard, int reg) {
        return predictStartBoardAndCounts(stopBoard, reg).first ;
    }

} //ZeroBoardModel
