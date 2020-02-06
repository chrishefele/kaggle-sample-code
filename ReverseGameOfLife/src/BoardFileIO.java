import java.io.*;
import java.util.*;

public class BoardFileIO {

    // note: readFile is a class method
    public static ArrayList<BoardPair> readFile(String inFileName, String format) {
        ArrayList<BoardPair> boardPairs = new ArrayList<BoardPair>();
        try { 
            File inFile  = new File(inFileName);   
            BufferedReader reader = new BufferedReader(new FileReader(inFile));
            String line = null;
            while ((line=reader.readLine()) != null) {  // loop as long as there are input lines 
                    if(line.contains("id,delta")) 
                        continue;  // skip header
                    String str = line.trim(); 
                    // line fields are: id, delta, start1..400, stop1..400
                    String[] tokens = str.split(",");   
                    int row_id = Integer.parseInt( tokens[0] );
                    int delta  = Integer.parseInt( tokens[1] );
                    int[][] startBoard = new int[Consts.BOARD_SIDE][Consts.BOARD_SIDE]; 
                    int[][] stopBoard  = new int[Consts.BOARD_SIDE][Consts.BOARD_SIDE]; 
                    for(int col=0; col<Consts.BOARD_SIDE; col++) { 
                        for(int row=0; row<Consts.BOARD_SIDE; row++) {
                            if(format=="train") { 
                                // train format: id, delta, start.1-start.400, stop.1-stop.400
                                // note column major order!
                                int startIndex = col*Consts.BOARD_SIDE + row + 2; 
                                int stopIndex  = startIndex + Consts.BOARD_SIDE*Consts.BOARD_SIDE;
                                startBoard[row][col]= Integer.parseInt( tokens[startIndex] );
                                stopBoard[ row][col]= Integer.parseInt( tokens[stopIndex ] );
                            } 
                            if(format=="test") {
                                // test format is: id, delta, stop.1-stop.400
                                // note column major order!
                                int stopIndex = col*Consts.BOARD_SIDE + row + 2;  
                                startBoard = null; 
                                stopBoard[ row][col]= Integer.parseInt( tokens[stopIndex ] );
                            }
                        }
                    }
                    boardPairs.add( new BoardPair(row_id, delta, startBoard, stopBoard) );
            } 
            reader.close();  
        } catch (IOException e) {
            System.out.println("ERROR reading: " + inFileName);
        }
        return boardPairs;
    }    

} //BoardFileIO
