// Generic class for bundling pairs of objects of different types into one object

public class Tuple2<FirstT, SecondT> {
    public final FirstT  first;
    public final SecondT second; 

    public Tuple2(FirstT first, SecondT second) {
        this.first  = first;
        this.second = second;
    }
}
