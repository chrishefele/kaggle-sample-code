import java.io.*;
import java.lang.*;
import java.util.*;

public class BoardModel {

    public  int[] patternCounts; 
    private int   delta;
    private double radiusStop;
    private long numExamplesTrained = 0; 
    private ZobristBoardHasher zobristStop;
    private ZobristBoardHasher zobristPosition;
    private long[][] positionHashes;

    public BoardModel() { 
        // dummy constructor for ZeroBoardModel, which inherits from this class
    }

    public BoardModel(int delta, double radiusStop) {
        System.out.print( "Initializing BoardModel: ");
        System.out.print("delta "+delta+" ");
        System.out.println("radiusStop "+radiusStop);
       
        this.delta = delta;
        this.radiusStop = radiusStop;
        clearCounts();

        zobristStop     = new ZobristBoardHasher(Consts.BOARD_SIDE, Consts.BOARD_SIDE, 
                                                 Consts.NUM_CELL_VALUES, 
                                                 Consts.ZOBRIST_SEED_STOP ); 
        zobristPosition = new ZobristBoardHasher(Consts.BOARD_SIDE, Consts.BOARD_SIDE, 
                                                 Consts.NUM_CELL_VALUES, 
                                                 Consts.ZOBRIST_SEED_POSITION); 
        initPositionHashes();
    }

    public long[][] randomBoardPositionHashes() {
        long[][] hashes = new long[Consts.BOARD_SIDE][Consts.BOARD_SIDE];
        Random rands = new Random(1234567);
        long r; 
        for(int nx=0; nx<hashes.length;    nx++) {
            for(int ny=0; ny<hashes[nx].length; ny++) {
                do {
                    r = rands.nextLong();
                } while(r <= 0L);
                hashes[nx][ny] = r;
            }
        }
        return hashes;
    }

    public long[][] zonifyHashes(long[][] hashes) {
        // overwrite existing hashes to create 'board zones' with common hashes
        for(int r=0; r<hashes.length;    r++) {
            for(int c=0; c<hashes[r].length; c++) {
                if(c < 5)                 { hashes[r][c] = hashes[0][c]; } else 
                if(c==5 || c==6)          { hashes[r][c] = hashes[0][5]; } else
                if(c==7 || c==8 || c==9 ) { hashes[r][c] = hashes[0][7]; } else
                                          { hashes[r][c] = hashes[0][c]; } 
            }
        }
        return hashes;
    }

    public void initPositionHashes() {
        // create hashes for each board position, using dihedral symetries
        int[][] dummyBoard = new int[Consts.BOARD_SIDE][Consts.BOARD_SIDE];
        positionHashes = randomBoardPositionHashes(); 
        positionHashes = zonifyHashes(positionHashes);
        for(int r=0; r<positionHashes.length; r++) {
            for(int c=0; c<positionHashes[r].length; c++) {
                int r_dih = rowColDihedral(dummyBoard, r, c)[0];
                int c_dih = rowColDihedral(dummyBoard, r, c)[1];
                positionHashes[r][c] = positionHashes[r_dih][c_dih];
                // System.out.println("positionHashes ["+r+","+c+"]->["+r_dih+","+c_dih+"]="+positionHashes[r][c]);
            }
        }
    }

    public void clearCounts() {
        patternCounts = new int[Consts.PATTERN_TABLE_SIZE];
    }

    public void saveModel(String countsFilename) {
        // serialize counts & write to file
        System.out.println("Saving model counts to: "+countsFilename);
         try {
            FileOutputStream fout = new FileOutputStream(countsFilename);
            ObjectOutputStream objout = new ObjectOutputStream(fout);
              objout.writeObject(patternCounts);
              objout.close();
              System.out.println("Saved model counts successfully." );
         } catch (IOException ex ) {
              System.out.println("ERROR writing file:"+ex);
         }
    }

    public void loadModel(String countsFilename) {
        // unserialize counts & write to file
        System.out.println("Reading model counts from: "+countsFilename);
         try {
              ObjectInputStream objin = 
                     new ObjectInputStream( new FileInputStream(countsFilename));
              patternCounts      = (int[]) objin.readObject();
              objin.close();
            System.out.println("Read model counts successfully." );
        } catch (Exception ex ) {
            System.out.println("ERROR reading file:"+ex);
        }
    } 

    // now unused - so remove? 
    public void printCounts() {
        for(int i=0; i<patternCounts.length; i++) {
            if(patternCounts[i] > 0) {
                System.out.println("delta: " + delta + " index: " + i + " count: " + patternCounts[i]);
            }
        }
    }

    public void printModelStats() {
        System.out.print("Pattern Counts:");
        printModelStatsCommon(patternCounts);
    }

    public void printModelStatsCommon(int[] patternCountTable) {
        int pos, neg, zero;
        pos = neg = zero = 0;
        for(int i=0; i<patternCountTable.length; i++) {
            if(patternCountTable[i] > 0)  { ++pos; }
            if(patternCountTable[i] < 0)  { ++neg; }
            if(patternCountTable[i] == 0) { ++zero; }
        }
        int tot = pos + neg + zero;
        int nonzero = pos + neg;
        System.out.println("delta: "+delta+" pos: "+pos+" neg: "+neg+" zero: "+zero+" tot: "+tot);
        //System.out.println("");
    }
    
    public int[][] selectCells(int[][] inboard, int ctr_row, int ctr_col, double radius) {
        // select and return a new 2d array of neighboring cells surrounding a
        // a given cell, given the center and a cell radius

        final int nrows = inboard.length;
        final int ncols = inboard[0].length; // inboard assumed to be square 
        final double radius_squared = radius * radius; 

        // radius_edge is the number of cells from center of the edge of a square
        // to to a corner, where the square encloses a circle of a given radius 
        final int radius_edge = (int) Math.round(Math.ceil(radius)); 
        final int side  = 2*radius_edge + 1; // side length of enclosing square 
        int[][]   outboard = new int[side][side];
        int       nbr_value;

        for(int dr=-radius_edge; dr<=radius_edge; dr++) {
            for(int dc=-radius_edge; dc<=radius_edge; dc++) {
                int nbr_row = ctr_row + dr;
                int nbr_col = ctr_col + dc;
                if( nbr_row<0 || nbr_row>=nrows || 
                    nbr_col<0 || nbr_col>=ncols   ) {
                    // neighboring cell is off the board 
                    nbr_value = Consts.SKIP_CELL_VALUE; 
                } else if(dr*dr + dc*dc > radius_squared) {
                    // neighboring cell is outside of a circle's radius
                    nbr_value = Consts.SKIP_CELL_VALUE; 
                } else {
                    // neighboring cell is on-board, and within circle radius
                    nbr_value = inboard[nbr_row][nbr_col]; 
                }
                outboard[dr + radius_edge][dc + radius_edge] = nbr_value;
            }
        }
        return outboard;
    }

    public int[][] boardTransforms(int[][] inboard, int transform) {
        final int nrows = inboard.length;
        final int ncols = inboard[0].length ; // inboard assumed to be rectangular
        int[][]  outboard = new int[nrows][ncols];
        for(int r=0; r<nrows; r++) {
            for(int c=0; c<ncols; c++) {
                switch (transform) {
                    case 0: outboard[r][c] = inboard[r][c];         // no change
                            break;
                    case 1: outboard[r][c] = inboard[nrows-1-r][c]; // vertical flip
                            break;
                    case 2: outboard[r][c] = inboard[r][ncols-1-c]; // horiz flip 
                            break;
                    case 3: outboard[r][c] = inboard[c][r];         // transpose
                            break; 
                }
            }
        }
        return outboard;
    }

    public int[][] vflip(    int[][] inboard) { return boardTransforms(inboard, 1); }
    public int[][] hflip(    int[][] inboard) { return boardTransforms(inboard, 2); }
    public int[][] transpose(int[][] inboard) { return boardTransforms(inboard, 3); }

    public int[][] selectCellsDihedral(int[][] inboard, int ctr_row, int ctr_col, double radius) {
        final int nrows = inboard.length;
        final int ncols = inboard[0].length ; // inboard assumed non-ragged
        int[][] cells = selectCells(inboard, ctr_row, ctr_col, radius);
        int row = ctr_row;
        int col = ctr_col;
        if(row >= nrows/2) { 
            cells = vflip(cells); 
            row = nrows-1 - row; 
        }
        if(col >= ncols/2) { 
            cells = hflip(cells); 
            col = ncols-1 - col; 
        }
        if(col > row) { 
            cells = transpose(cells); 
            int tmp = col;
            col = row;
            row = tmp;
        } 
        return cells;
    }

    public int[] rowColDihedral(int[][] inboard, int row, int col) {
        final int nrows = inboard.length;
        final int ncols = inboard[0].length ; // inboard assumed non-ragged
        if(row >= nrows/2) { row = nrows-1 - row; }
        if(col >= ncols/2) { col = ncols-1 - col; }
        if(col > row)      { int tmp = col; col = row; row = tmp; } 
        int[] rowcol = {row, col};
        return rowcol;
    }

    public int hashToIndex(long h) {
        return (int) (h % Consts.PATTERN_TABLE_MODPRIME);
    }

    public long[][] boardCellHashes(int[][] inboard, double radius, ZobristBoardHasher hasher) {
        final int nrows = inboard.length;
        final int ncols = inboard[0].length ; // inboard assumed non-ragged
        long[][] hashes = new long[nrows][ncols];
        for(int r=0; r<nrows; r++) {
            for(int c=0; c<ncols; c++) {
                int[][] boardCells = selectCellsDihedral(inboard, r, c, radius);
                hashes[r][c] = hasher.hashBoard(boardCells);
            }
        }
        return hashes;
    }

    public long[][] positionStopBoardCellHashes(int[][] stopBoard) {

        long[][] stopHashes = boardCellHashes(stopBoard, radiusStop, zobristStop);

        int nrows = stopBoard.length;
        int ncols = stopBoard[0].length ; // inboard assumed non-ragged
        long[][] outHashes = new long[nrows][ncols];

        for(int r=0; r<nrows; r++) {
            for(int c=0; c<ncols; c++) {
                // create a hash combining stop board patterns and cell position 
                outHashes[r][c] = stopHashes[r][c] ^ positionHashes[r][c];
                //outHashes[r][c] = stopHashes[r][c] ; // ^ positionHashes[r][c]; TODO for testing 
            }
        }
        return outHashes; 
    }

    public void addExample(int[][] startBoard, int[][] stopBoard) {
        final int nrows = stopBoard.length;
        final int ncols = stopBoard[0].length ; // inboard assumed non-ragged

        long[][] positionStopHashes = positionStopBoardCellHashes(stopBoard);

        for(int r=0; r<nrows; r++) {
            for(int c=0; c<ncols; c++) {
                long positionStopHash = positionStopHashes[r][c];
                if(startBoard[r][c] == 1) {
                    ++patternCounts[hashToIndex(positionStopHash)];
                } else {
                    --patternCounts[hashToIndex(positionStopHash)];
                }
            }
        }
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

        long[][] positionStopHashes = positionStopBoardCellHashes(stopBoard);
        for(int r=0; r<nrows; r++) {
            for(int c=0; c<ncols; c++) {
                long h = positionStopHashes[r][c]; 
                startBoardCounts[r][c] = patternCounts[hashToIndex(h)];
                startBoard[r][c]       = (startBoardCounts[r][c] > reg) ? 1 : 0 ; 
            }
        }
        return new Tuple2<int[][], int[][]>(startBoard, startBoardCounts);
    }


    public int[][] predictStartBoard( int[][] stopBoard, int reg) {
        return predictStartBoardAndCounts(stopBoard, reg).first ;
    }

    public void printBoardCommon(long[][] board, int option) {
        final int nrows = board.length;
        final int ncols = board[0].length ; // inboard assumed non-ragged
        for(int r=0; r<nrows; r++) {
            for(int c=0; c<ncols; c++) {
                switch (option) {
                    case 0: String cell_str = (board[r][c]==0) ? "-" : "X"; 
                            System.out.print(cell_str);
                            break;
                    case 1: System.out.print(board[r][c]);
                            break;
                    }
            }
            System.out.println("");
        }
        System.out.println("");
    }
    public void printBoardChar(long[][] board) { printBoardCommon(board, 0); }
    public void printBoardNums(long[][] board) { printBoardCommon(board, 1); }

} //BoardModel
