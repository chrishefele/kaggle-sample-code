public class BoardPair{

    public int row_id;
    public int delta;
    public int[][] startBoard, stopBoard;

    public BoardPair(int row_id, int delta, int[][] startBoard, int[][] stopBoard) {
        this.row_id     = row_id;
        this.delta      = delta;
        this.startBoard = startBoard;
        this.stopBoard  = stopBoard;
    }
}

