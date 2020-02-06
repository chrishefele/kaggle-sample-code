public class EdgeRecord {

public final int   Vout;  // vertex of outbound side of edge
public final int   Vin;   // vertex of inbound side of edge 
public final float Prob;  // edge probability; 1 if exists, or 0 if doesn't exist 
public float Cache; // sum of previous features

public EdgeRecord(int VertexOut, int VertexIn, float EdgeProb ) {
    Vout  = VertexOut;
    Vin   = VertexIn;
    Prob  = EdgeProb; 
    Cache = 0.0f;
}

public float getCache() {
    return Cache;
}

public void setCache(float newCacheValue) {
    Cache = newCacheValue;
}

} // class EdgeRecord
 
