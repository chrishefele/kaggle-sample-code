  
public class Life {

    public static void main (String[] args) {

        // e.g. java -Xmx7000M Life <batches_int> <modelDeltas_String> 
        int    batches     = Integer.parseInt(args[0]);
        String modelDeltas = args[1];
        //double radii     = Double.parseDouble(args[1]);

        System.out.println("\n***** Reverse Game of Life Predictions *****\n");
        System.out.println("batches (millions)    : " + batches);
        System.out.println("model deltas          : " + modelDeltas);
        //System.out.println("start board radii     : " + radii  );
        System.out.println("PATTERN_TABLE_MAXBITS : " + Consts.PATTERN_TABLE_MAXBITS);
        System.out.println("PATTERN_TABLE_MODPRIME: " + Consts.PATTERN_TABLE_MODPRIME);
        System.out.println("PATTERN_TABLE_SIZE    : " + Consts.PATTERN_TABLE_SIZE);
        System.out.println("");

        BoardModel[] models = new BoardModel[] { 
            null, 
            modelDeltas.contains("1") ? new BoardModel(1, 2.9) : new ZeroBoardModel(1),
            modelDeltas.contains("2") ? new BoardModel(2, 2.9) : new ZeroBoardModel(2),
            modelDeltas.contains("3") ? new BoardModel(3, 3.1) : new ZeroBoardModel(3),
            modelDeltas.contains("4") ? new BoardModel(4, 3.1) : new ZeroBoardModel(4),
            modelDeltas.contains("5") ? new BoardModel(5, 3.7) : new ZeroBoardModel(5)
        }; 

        // optimum model (delta,radius) for 32M training iterations: 
        // (1,2.9),(2,2.9),(3,3.1), (4,3.1), (5,3.7)
        // double radii = 0;   // 1 cell, no border
        // double radii = 0.9; // 1 cell, with -1 border
        // double radii = 1.1; // 5 cells
        // double radii = 1.5; // 9 cells

        CrossValidation cv = new CrossValidation();

        for(int batch=0; batch<batches; batch++) {       
            final int nTrain = 1000*1000;
            //final int nTrain = 20*1000; // TODO for testing 
            Trainer.trainModels(models, nTrain);
            cv.crossValidate(models);
            String subFile = "sub-deltas-"+modelDeltas+".csv";
            Submission.writeSubmissionFile(subFile, models, Consts.REGS_VS_DELTA);
        }

        for(int delta=1; delta<Consts.DELTAS+1; delta++) {
            String fname = "model-delta-"+delta+".ser";
            models[delta].saveModel(fname); // TODO reenable
            // models[delta].loadModel(fname);
        }

    }
}

