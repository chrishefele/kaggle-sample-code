import java.math.BigInteger;

public class PrimeEngine {

    public static long previousProbablePrime(long n) {
        BigInteger val = BigInteger.valueOf(n);
        // To achieve the same degree of certainty as the nextProbablePrime 
        // method, use x = 100 --> 2^(-100) == (0.5)^100.
        int certainty = 100;
        do {
            val = val.subtract(BigInteger.ONE);
        } while (!val.isProbablePrime(certainty));
        return val.longValue();
    }

}

