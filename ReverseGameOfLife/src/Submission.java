import java.io.*;
import java.util.*;

public class Submission {

    public static void writeSubmissionFile( String outFileName, 
                                            BoardModel[] models, 
                                            int[] regsVsDelta   ) {

        ArrayList<BoardPair> testFileBoardPairs = BoardFileIO.readFile(Consts.TEST_FILENAME, "test");
        System.out.println("Writing submission to: "+outFileName);
        try {
            File outFile = new File(outFileName);  
            BufferedWriter writer = new BufferedWriter(new FileWriter(outFile));
            writer.write("id");
            for(int i=1;i<=Consts.BOARD_SIDE*Consts.BOARD_SIDE; i++) {
                writer.write(",start."+i);
            }
            writer.newLine(); 

            for(BoardPair bp : testFileBoardPairs ) {
                int reg = regsVsDelta[bp.delta];
                int[][] predStartBoard = models[bp.delta].predictStartBoard(bp.stopBoard, reg); 
                StringBuilder predLine = new StringBuilder();
                predLine.append(""+bp.row_id);
                for(int col=0; col < Consts.BOARD_SIDE; col++) { // NOTE column major order 
                    for(int row=0; row < Consts.BOARD_SIDE; row++) {
                        predLine.append("," + predStartBoard[row][col]);
                    }
                }
                writer.write(predLine.toString());
                writer.newLine(); 
                if(bp.row_id % Consts.PRINT_STATUS_INTERVAL == 0) {
                    System.out.print(" "+bp.row_id);
                }
            }    
            writer.close(); 
        } catch (IOException e) {
            System.out.println("ERROR: problems writing submission");
        }
    }
} //Submission

