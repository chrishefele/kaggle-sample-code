import unzip2opt as u2
import sys

def main():
    tour_infile = sys.argv[1]
    tour1_init, tour2_init = u2.read_tours(tour_infile) 
    tour1 = u2.TourEngine(tour1_init, load_neighbors=False)
    tour2 = u2.TourEngine(tour2_init, load_neighbors=False)
    tour1_len = tour1.get_tour_length()
    tour2_len = tour1.get_tour_length()
    print 'RESULT ',
    print 'tour_length_1:', int(tour1_len),
    print 'tour_length_2:', int(tour2_len),
    print 'file:', tour_infile

main()

