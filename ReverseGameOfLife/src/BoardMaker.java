import java.util.Random;

public class BoardMaker {

    // NOTE since we're training in batches, and BoardMaker is created 
    // per batch, use an UNseeded random number generator so we get
    // unique boards in every batch, instead of repeating  boards each batch
    //private Random rands = new Random( Consts.RAND_SEED_BOARDMAKER );
    private   Random rands = new Random();

    private int row_id = 0; 

    public BoardMaker() { }

    public BoardPair nextBoardPair(int delta) { 
        int[][] startBoard, stopBoard;
        do {
            startBoard = randomBoard(); 
            for(int d=1; d<=Consts.INIT_DELTA; d++) { 
                startBoard = evolveBoard(startBoard); 
            }
            stopBoard = startBoard;  
            for(int d=1; d<=delta;      d++) { 
                stopBoard = evolveBoard(stopBoard); 
            }
            //System.out.println("Initial board"); printBoard(startBoard);
            //System.out.println("Start board");   printBoard(startBoard);
            //System.out.println("Stop board");    printBoard(stopBoard);

        } while(isEmptyBoard(stopBoard));   
        return new BoardPair(++row_id, delta, startBoard, stopBoard);
    }

    public int[][] randomBoard() {
        int[][]  board = new int[Consts.BOARD_SIDE][Consts.BOARD_SIDE];
        float density = 0.01f + 0.98f * rands.nextFloat(); // rand interval [0.01, 0.99]
        // System.out.println("density:" + density);
        for(int r=0; r<Consts.BOARD_SIDE; r++) {
            for(int c=0; c<Consts.BOARD_SIDE; c++) {
                board[r][c] = (density > rands.nextFloat()) ? 1 : 0; 
            }
        }
        return board;
    }

    public boolean isEmptyBoard(int[][] board) {
        boolean emptyBoard = true; 
        for(int r=0; r<Consts.BOARD_SIDE; r++) {
            for(int c=0; c<Consts.BOARD_SIDE; c++) {
                emptyBoard = emptyBoard && (board[r][c]==0);
            }
        }
        return emptyBoard;
    }

    public int[][] evolveBoard(int[][] board) {
        int[][]  nbrsBoard  = new int[Consts.BOARD_SIDE][Consts.BOARD_SIDE];
        int[][]  evolBoard  = new int[Consts.BOARD_SIDE][Consts.BOARD_SIDE];

        for(int r=0; r<Consts.BOARD_SIDE; r++) {
            for(int c=0; c<Consts.BOARD_SIDE; c++) {
                for(int dr=-1; dr<=1; dr++) {
                    for(int dc=-1; dc<=1; dc++) {
                        int nbr_row = r + dr;
                        int nbr_col = c + dc;
                        if( nbr_row<0 || nbr_row>=Consts.BOARD_SIDE || 
                            nbr_col<0 || nbr_col>=Consts.BOARD_SIDE) 
                            continue;
                        nbrsBoard[r][c] += board[nbr_row][nbr_col];
                    }
                }
                nbrsBoard[r][c] -= board[r][c];
            }
        }
        //System.out.println("Board Neighbor Counts");
        //printBoardInts(nbrsBoard);
        for(int r=0; r<Consts.BOARD_SIDE; r++) {
            for(int c=0; c<Consts.BOARD_SIDE; c++) {
                int cell_nbrs = nbrsBoard[r][c];
                int cell      = board[r][c]; 
                evolBoard[r][c] = (cell_nbrs==3 || (cell_nbrs==2 && cell!=0)) ? 1 : 0;
            }
        }
        return evolBoard;
    }

    public void printBoard(int[][] board) {
        for(int r=0; r<Consts.BOARD_SIDE; r++) {
            for(int c=0; c<Consts.BOARD_SIDE; c++) {
                // System.out.print(board[r][c]);
                String cell_str = (board[r][c]==0) ? "-" : "X"; 
                System.out.print(cell_str);
            }
            System.out.println("");
        }
        System.out.println("");
    }

    public void printBoardInts(int[][] board) {
        for(int r=0; r<Consts.BOARD_SIDE; r++) {
            for(int c=0; c<Consts.BOARD_SIDE; c++) {
                System.out.print(board[r][c]);
            }
            System.out.println("");
        }
        System.out.println("");
    }

} // BoardMaker
