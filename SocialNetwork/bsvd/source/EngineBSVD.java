import java.util.ArrayList;
import java.util.HashSet;
import java.lang.Math; 
import java.util.Random;
import java.io.*; 

public class EngineBSVD {

private String  DATA_DIR = "/home/chefele/SocialNetwork/data/";
private String  PROBE_FILENAME    = DATA_DIR + "social_probe.csv";
private String  TRAINING_FILENAME = DATA_DIR + "social_train_minus_probe.csv";
//private String  TRAINING_FILENAME = DATA_DIR + "social_train_plus_probe.csv"; //FOR FINAL SUB
private String  TEST_FILENAME     = "/home/chefele/SocialNetwork/download/social_test.txt"; 

public  String  PREDICTIONS_PROBE = "bsvd_predictions_probe.csv";
public  String  PREDICTIONS_TEST  = "bsvd_predictions_test.csv";
public  String  PREDICTIONS_TRAIN = "bsvd_predictions_train.csv";

private int     MAX_VERTEX_ID = 1133547;
private int     PRINT_MOD = 200000;

private double  REGULARIZATION = 0.02;  // optimal 0.02 for directed links 
private double  LRATE_INIT = 0.01; // 0.01 for 0.5328 run
private double  LRATE = LRATE_INIT; 
private double  LRATE_MIN  = 1.0e-7;
public  double  LRATE_SCALEUP = 1.1; // 2^(1/4)=1.18; 1.2 
private double  LRATE_SCALEDOWN = 0.5;  // 1.0/LRATE_SCALEUP; 
private double  ANNEALING_CONST = 10;  // anneal learning rate 

private float   INIT_FEATURE_CONST = 0.1f; // default initialization for non-bias features 
private float   INIT_FEATURE_STDEV = 0.1f; 
private long    RANDOM_SEED = 1234567; 
private Random  randNumGen = new Random(RANDOM_SEED); 
private int     UNIQUE_VOUTS = 37689;
private int     UNIQUE_VINS  = 1133505;
private double  LRATE_VIN_SCALEUP = Math.sqrt(UNIQUE_VINS/UNIQUE_VOUTS); // =5.48
private boolean BIDIRECTIONAL_EDGES = false; // directed vs undirected/bidirectional

// Edge data (global)
private ArrayList<EdgeRecord> trainEdgeRecords = new ArrayList<EdgeRecord>(); 
private ArrayList<EdgeRecord> probeEdgeRecords = new ArrayList<EdgeRecord>(); 
private ArrayList<EdgeRecord>  testEdgeRecords = new ArrayList<EdgeRecord>(); 

// Feature vectors (global) 
public  float[] fVout = new float[MAX_VERTEX_ID+1];  // Working feature vectors
public  float[] fVin  = new float[MAX_VERTEX_ID+1]; 
private ArrayList<float[]> fVouts = new ArrayList<float[]>(); // Finalized feature vectors
private ArrayList<float[]> fVins  = new ArrayList<float[]>();

private int[] degreeVout = new int[MAX_VERTEX_ID+1]; // outbound edges for each Vertex 
private HashSet<Integer> VinIDs   = new HashSet<Integer>();
private HashSet<Integer> VoutIDs  = new HashSet<Integer>();


// Start code

public EngineBSVD() { //constructor

    if (BIDIRECTIONAL_EDGES) {   // directed links, unidirectional 
        LRATE_VIN_SCALEUP = 1.0; 
    } else {                // undirected, bidirectional links, since con.matrix is square
        LRATE_VIN_SCALEUP = Math.sqrt(UNIQUE_VINS/UNIQUE_VOUTS); // con.matrix rectangular
    } 

} 

public void randomFeatures() {
    for(int i=0; i<fVout.length;i++) {
        fVout[i] = (float) (randNumGen.nextGaussian() * INIT_FEATURE_STDEV);
    }
    for(int i=0; i<fVin.length; i++) {
        fVin[ i] = (float) (randNumGen.nextGaussian() * INIT_FEATURE_STDEV);
    }
}

public void fillFeatures(float fVoutConst, float fVinConst) {
    for(int i=0; i<fVout.length;i++) fVout[i]=fVoutConst;
    for(int i=0; i<fVin.length; i++) fVin[ i]=fVinConst;
}

public void startNewFeature(float fVoutConst, float fVinConst) {
    fVout = new float[MAX_VERTEX_ID+1];  // current feature vectors
    fVin  = new float[MAX_VERTEX_ID+1]; 
    fillFeatures(fVoutConst, fVinConst);
}

public void addEdge(int Vout, int Vin, float EdgeProb, ArrayList<EdgeRecord> edgeRecords) {
    edgeRecords.add( new EdgeRecord(Vout, Vin, EdgeProb) );
}

public void calcDegreeVout(ArrayList<EdgeRecord> edgeRecords) {
    System.out.print("Calculating outbound vertex degrees..."); 
    for(int i=0; i<degreeVout.length; i++) {
        degreeVout[i] = 0;
    }
    for(EdgeRecord edge : edgeRecords)  {
        degreeVout[edge.Vout]++;  
    } 
    System.out.println("Done.");
}

public void calcVoutVinIDs(ArrayList<EdgeRecord> edgeRecords) {
    System.out.print("Calculating vertex ID sets..."); 
    for(EdgeRecord edge : edgeRecords)  {
        VoutIDs.add(edge.Vout); 
        VinIDs.add(edge.Vin); 
    } 
    System.out.println("Done.");
}

public double calcVoutFeatureMeanSquare() {
    double sumSq = 0.0; 
    for(int VoutID : VoutIDs) {
        sumSq += fVout[VoutID]*fVout[VoutID];
    }
    return sumSq/VoutIDs.size();
}

public double calcVinFeatureMeanSquare() {
    double sumSq = 0.0; 
    for(int VinID : VinIDs) {
        sumSq += fVin[VinID]*fVin[VinID];
    }
    return sumSq/VinIDs.size();
}

private void printStatus(int n) {
    if (n % PRINT_MOD == 0) {
        System.out.print(".");
        System.out.flush(); 
    }
}

public void readEdgeFile(String edgeFileName, ArrayList<EdgeRecord> edgeRecords,
                         boolean bidirectionalEdges ) {
    System.out.println("Reading: "+edgeFileName); 
    try { 
        BufferedReader in = new BufferedReader(new FileReader(edgeFileName)); 
        int linesRead = 0; 
        String line; 
        while ((line = in.readLine()) != null) { 
            String[] tokens = line.split(","); 
            int Vout = Integer.parseInt( tokens[0] );
            int Vin  = Integer.parseInt( tokens[1] );
            float EdgeProb;
            if (tokens.length >= 3) {   // for train & probe files
                EdgeProb = (float) Integer.parseInt( tokens[2] ); // 1=true edge, 0=false edge
            } else {
                EdgeProb = Float.NaN; // in test file, edge probability unknown 
            }
            if (bidirectionalEdges) {
                addEdge(Vout, Vin, EdgeProb, edgeRecords);
                addEdge(Vin, Vout, EdgeProb, edgeRecords);
            } else {
                addEdge(Vout, Vin, EdgeProb, edgeRecords);
            }
            printStatus(linesRead);
            linesRead++;
        }
        in.close(); 
        System.out.println("");
        System.out.println("Read "+linesRead+" lines\n"); 
    } catch (IOException e) { } 
}


public double logistic(double x) {
    return 1.0 / (1.0 + Math.exp(-x)) ; 
}

private double calcDeltaTotLogLikelihood(double probActual, double sumFeatureProducts) {
        // Calculate LogLikelihood in a numerically stable way.
        // The following 2 lines sometimes rounds 1-probPredicted to 0, yielding log(0)->NaN:
        //    double deltaLogLikelihood  = (    probActual)*Math.log(    probPredicted) + 
        //                                 (1.0-probActual)*Math.log(1.0-probPredicted);
        // So instead, do some algebra to simplify log(logistic(sumFeatureProducts)). 
        // The resulting equations are more numerically stable. 
        double logProbPredicted, logOneMinusProbPredicted;
        if (sumFeatureProducts>=0.0) {
               logProbPredicted         = -Math.log(1.0+Math.exp(-sumFeatureProducts));
               logOneMinusProbPredicted = -sumFeatureProducts + logProbPredicted;
        } else {  
               logOneMinusProbPredicted = -Math.log(1.0+Math.exp( sumFeatureProducts));
               logProbPredicted         =  sumFeatureProducts + logOneMinusProbPredicted;
        }
        double deltaTotLogLikelihood  = (    probActual)*(logProbPredicted) + 
                                        (1.0-probActual)*(logOneMinusProbPredicted);
        return deltaTotLogLikelihood; 
} 

public double calcFeatureIteration(boolean updateVoutFeatures, 
                                   boolean updateVinFeatures,
                                   ArrayList<EdgeRecord> edgeRecords)   { 
    double totLogLikelihood = 0.0;
    //double fVoutNorm = calcVoutFeatureMeanSquare(); 
    //double fVinNorm  = calcVinFeatureMeanSquare(); 
    for(EdgeRecord edge : edgeRecords) {

        double probActual    = edge.Prob; 
        double sumFeatureProducts = fVout[edge.Vout]*fVin[edge.Vin] + edge.Cache;
        double probPredicted = logistic( sumFeatureProducts );
        double err = probActual - probPredicted;

        double deltaTotLogLikelihood = calcDeltaTotLogLikelihood(probActual,sumFeatureProducts);
        if (Double.isNaN(deltaTotLogLikelihood)) {
            System.out.print("NaN_ERR@ Vout "+edge.Vout+" Vin "+edge.Vin);
            System.out.print(" Pred "+probPredicted);
            System.out.print(" Actual "+probActual+" Err "+err);
            System.out.print(" fVout "+fVout[edge.Vout]+" fVin "+fVin[edge.Vin]);
            System.out.println(" Cache "+edge.Cache); 
            return(Double.NaN); 
        } 
        totLogLikelihood += deltaTotLogLikelihood; 

        // calc weight to train equally on each Vout's data, instead of equally on each data pt
        double LRateVoutScaleDown = 10.0 / Math.sqrt(degreeVout[edge.Vout]); 
        if (updateVoutFeatures) {
            double dFVout = err*fVin[ edge.Vin ] - fVout[edge.Vout]*REGULARIZATION; 
            //double dFVout = err*fVin[ edge.Vin ] - fVout[edge.Vout]*(1.0/1.0); 
            fVout[edge.Vout] += dFVout * LRATE ; // * LRateVoutScaleDown; 
        }
        if (updateVinFeatures) {
            double dFVin =  err*fVout[edge.Vout] - fVin[ edge.Vin ]*REGULARIZATION;
            //double dFVin =  err*fVout[edge.Vout] - fVin[ edge.Vin ]*(1.0/fVinNorm);
            fVin[edge.Vin]   += dFVin  * LRATE * LRATE_VIN_SCALEUP ; // *LRateVoutScaleDown; 
        }  
    }
    double avgLogLikelihood = totLogLikelihood / edgeRecords.size(); 
    return(avgLogLikelihood); 
}

public double annealing(int passNum) {
    return ((double) ANNEALING_CONST)/(ANNEALING_CONST + passNum) ; 
}

public double calcFeature(double minDeltaLL, int minIterations, int maxIterations,
                          boolean updateVoutFeatures, boolean updateVinFeatures,
                          float fVoutInitConst, float fVinInitConst) {
    LRATE = LRATE_INIT; 
    // System.out.println("Starting a new feature");  
    startNewFeature(fVoutInitConst, fVinInitConst); 
    double lastLL = calcFeatureIteration(updateVoutFeatures, updateVinFeatures,
                                            trainEdgeRecords);
    double deltaLL, currentLL, probeLL; // "LL" = log-likelihood
    double lastDeltaLL = 0.0; 
    int iterations = 1;
    boolean excessiveIterations, slowedImprovement;  
    do {
        currentLL = calcFeatureIteration(updateVoutFeatures, updateVinFeatures,
                                            trainEdgeRecords); 
        if (Double.isNaN(currentLL)) return(Double.NaN); // aborts feature; doesn't finalize
        deltaLL = currentLL - lastLL; 
        double deltaDeltaLL = deltaLL - lastDeltaLL; 
        probeLL = calcProbeLogLikelihood();
        System.out.printf("Pass %3d TrainLL %12.8f  ", iterations, currentLL);
        System.out.printf("dTrainLL %11.8f ddTrainLL %11.8f ", deltaLL, deltaDeltaLL);
        System.out.printf("ProbeLL %11.8f  ",  probeLL);
        System.out.printf("LRate %11.8f %n",LRATE); 
        lastLL = currentLL;
        lastDeltaLL = deltaLL;   
        if (deltaLL>=0.0)  {  //changed from deltaLL only
            LRATE = LRATE*LRATE_SCALEUP ; // *annealing(iterations); 
        } else {
            LRATE = Math.max(LRATE*LRATE_SCALEDOWN, LRATE_MIN); 
        } 
        iterations++;
        excessiveIterations = (iterations>maxIterations);
        slowedImprovement = (iterations>minIterations) && (deltaLL<minDeltaLL); 
    } while (! (excessiveIterations || slowedImprovement)); 
    finalizeFeature(); 
    System.out.printf("\nFEATURE_RESULTS: Passes %3d  TrainLL %11.8f  ProbeLL %11.8f\n",
                     iterations, currentLL, probeLL);
    return (currentLL);
}

public void calcFeatures(int numFeatures, double regularization,
                         double minDeltaLL, int minIterations, int maxIterations,
                         float fVoutInitConst, float fVinInitConst)   {

    REGULARIZATION = regularization;
    System.out.println("Regularization: "+REGULARIZATION); 

    System.out.println("\nCalculating biases\n"); 
    // first calculate biases for each Vout by only updating Vouts
    // (that is, Vin stays =1.0, so Vin*Vout = Vout)
    calcFeature(minDeltaLL, minIterations, maxIterations, true, false, 1.0f, 1.0f); 

    // calculate features
    double lastProbeLL = calcProbeLogLikelihoodFinalizedFeatures();
    for(int numFeature=0; numFeature<numFeatures; numFeature++) {
        System.out.println("\nCalculating feature "+numFeature+"\n"); 
        double trainLL = calcFeature(minDeltaLL, minIterations, maxIterations, 
                                true, true, INIT_FEATURE_CONST, INIT_FEATURE_CONST);
        // catch if the features diverged, etc. and stop training early
        if (Double.isNaN(trainLL)) {
            System.out.println("NaN Error; aborting feature & finishing");
            break; 
        }

        // if cross-validation LL of holdout/probe set decreases, stop training early
        double currentProbeLL = calcProbeLogLikelihoodFinalizedFeatures();
        System.out.print( "PROBE_LL of completed features: ");
        System.out.println( "Current = "+currentProbeLL+" Previous = "+lastProbeLL);
        if (currentProbeLL-lastProbeLL < 0.0) { 
            System.out.println("\nTraining STOPPED. Feaure finished, but probe LL decreased\n");
            break;
        }
        lastProbeLL = currentProbeLL; 
    }
}


public void finalizeFeature() {
    commitFeatureToCache( trainEdgeRecords );
    commitFeatureToCache( probeEdgeRecords );
    fVouts.add(fVout); 
    fVins.add(fVin); 
}

public void commitFeatureToCache( ArrayList<EdgeRecord> edgeRecords ) {
    //System.out.println("Committing current feature to cache");
    for(EdgeRecord edge : edgeRecords) {
        edge.Cache += fVout[edge.Vout]*fVin[edge.Vin];
    }
} 

public void commitFeatureToCache() {            // no argument default version
    commitFeatureToCache( trainEdgeRecords );
} 

public double calcProbeLogLikelihood() {
    // turn feature updates to false to just get log-likelihood without updating features
    return( calcFeatureIteration(false,false,probeEdgeRecords) );
}

public double calcProbeLogLikelihoodFinalizedFeatures() {
    // only use finalized features (does not use interim features in cache)
    double totLogLikelihood = 0.0; 
    double EPS = 0.00001; 
    for(EdgeRecord edge : probeEdgeRecords ) {
        double probActual    = edge.Prob;
        double probPredicted = predictEdgeProb(edge.Vout, edge.Vin);
        probPredicted = Math.max(Math.min(probPredicted,1.0-EPS),EPS); //clamp [EPS,1-EPS]
        totLogLikelihood    += ((    probActual)*Math.log(    probPredicted) + 
                                (1.0-probActual)*Math.log(1.0-probPredicted));
    }
    double avgLogLikelihood = totLogLikelihood / probeEdgeRecords.size(); 
    return(avgLogLikelihood);
}


public double predictEdgeProb(int Vout, int Vin) {
    assert fVouts.size() == fVins.size(); // check 
    int numFeatures = fVouts.size();
    double sumProds = 0.0; 
    for(int numFeature=0; numFeature < numFeatures; numFeature++) {
        float[] fVoutArray = fVouts.get(numFeature);
        float[] fVinArray  = fVins.get(numFeature);
        sumProds += fVoutArray[Vout]*fVinArray[Vin]; 
    }
    double probPredicted = logistic(sumProds);
    return probPredicted;
} 

public void writeEdgeFile(String edgeFileName, ArrayList<EdgeRecord> edgeRecords) {
    try { 
        BufferedWriter out = new BufferedWriter(new FileWriter(edgeFileName)); 
        for(EdgeRecord edge : edgeRecords) {
            String lineOut; 
            double edgeProbPrediction = predictEdgeProb(edge.Vout, edge.Vin); 
            if ( Float.isNaN(edge.Prob) ) {   // test records 
                lineOut = edge.Vout+","+edge.Vin+","+edgeProbPrediction+"\n";  
            } else {                          // probe records
                lineOut = edge.Vout+","+edge.Vin+","+edge.Prob+","+edgeProbPrediction+"\n";
            } 
            out.write(lineOut);
        }
        out.close(); 
        int numPredictions = edgeRecords.size();
        System.out.println("Wrote "+numPredictions+" predictions to: "+edgeFileName);
    } catch (IOException e) { 
        System.out.println("ERROR writing to:"+edgeFileName); 
    } 
}

public void go( int     numFeatures,    // excludes bias
                double  regularization, // tune via Xvalidation with probe; 0.02 typical 
                double  minDeltaLL,     // min improvement in trainLL to keep training
                int     minIterations,  // min/max iterations allowed per feature
                int     maxIterations,  
                float   fVoutInitConst, // initialization constants for features
                float   fVinInitConst)    { 

    System.out.println("\n*** BSVD Calculation ***\n"); 

    readEdgeFile(TRAINING_FILENAME, trainEdgeRecords, BIDIRECTIONAL_EDGES); 
    readEdgeFile(PROBE_FILENAME,    probeEdgeRecords, false); 
    readEdgeFile(TEST_FILENAME,     testEdgeRecords,  false); 

    calcDegreeVout(trainEdgeRecords); 
    calcVoutVinIDs(trainEdgeRecords);

    calcFeatures(numFeatures, regularization,
                 minDeltaLL, minIterations, maxIterations,
                 fVoutInitConst, fVinInitConst);  

    System.out.println("\nWriting prediction files");
    writeEdgeFile(PREDICTIONS_PROBE, probeEdgeRecords);
    writeEdgeFile(PREDICTIONS_TEST, testEdgeRecords);
    writeEdgeFile(PREDICTIONS_TRAIN, trainEdgeRecords); 
    System.out.println("\nBSVD Calculation finished.\n");
}


} // class EngineSVD
 
