import java.io.*;
import java.util.Random;

public class Trainer {

    public Trainer() { }

    public static void trainModels(BoardModel[] models, int nTrain) {
        System.out.println("Training for "+nTrain+" iterations");

        // NOTE Using a fixed seed with the random number generator will
        // repeat  the sequence each time trainModels is called;
        // but when training in seperate batches, we use unseeded Random() so
        // get fresh training examples. If consistency is needed,
        // make a non-static method & a Trainer object with a new Random()
        // created in the constructor.
        // Same argument applies to BoardMaker()

        // Random rands = new Random( Consts.RAND_SEED_TRAINER );  
        Random rands = new Random(); 

        BoardMaker boardMaker = new BoardMaker();
        for(int n=0; n < nTrain; n++) {
            int delta = rands.nextInt(5) + 1;
            BoardPair bp = boardMaker.nextBoardPair(delta);
            models[bp.delta].addExample(bp.startBoard, bp.stopBoard);
            if(bp.row_id % Consts.PRINT_STATUS_INTERVAL == 0) {
                System.out.print(bp.row_id + " ");
            }
        }
        System.out.println("\nPATTERN COUNT STATS\n"); 
        for(int delta=1; delta<=5; delta++) {
            models[delta].printModelStats();
        }
        // TODO save counts to files? 
    }

} //Trainer

