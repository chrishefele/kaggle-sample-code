// Zobrist hashing engine 
// (see: http://en.wikipedia.org/wiki/Zobrist_hashing)
//

import java.io.*;
import java.util.Random;

public class ZobristBoardHasher {

    private long[][][] table;
    private long rng_seed;

    public ZobristBoardHasher(int nBoardX, int nBoardY, int nValues, long rng_seed) { 
        initRandomsTable(nBoardX, nBoardY, nValues, rng_seed);
    }

    public void initRandomsTable(int nBoardX, int nBoardY, int nValues, long rng_seed) { 
        // Initialize the random values table with positive random numbers,
        // one per combination of cell value and (x,y) board position.
        table = new long[nBoardX][nBoardY][nValues];
        Random rands = new Random(rng_seed); 
        long r; 
        for(int nx=0; nx < nBoardX; nx++) {
            for(int ny=0; ny < nBoardY; ny++) {
                for(int nv=0; nv < nValues; nv++) {
                    do {
                        r = rands.nextLong(); 
                    } while(r <= 0L);
                    table[nx][ny][nv] = r;
                }
            }
        }
    }

    public long hashBoard(int[][] board) {
        // Xor together the random table values that correspond to 
        // the values in each board position.
        long h = 0; 
        for(int x=0; x < board.length; x++) {
            for(int y=0; y < board[x].length; y++) {
                int v = board[x][y] + 1; // board(-1,0,1) +1 -> table(0,1,2) 
                h = h ^ table[x][y][v]; 
            }
        }
        return h; // guaranteed positive hash 
    }

    public long test() {
        // to test, use: test_hash = new ZobristBoardHasher(4,4,3).test()
        int[][] b = new int[][]{ { 0, 1, 0, 1},
                                 {-1, 1, 0, 1},
                                 { 1, 0,-1, 1},
                                 { 0, 0, 1, 0} };
        // System.out.println("test hash = " + hashBoard(b));
        return hashBoard(b);
    }

} //ZobristBoardHasher

