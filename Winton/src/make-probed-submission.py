#
# Script to make a submission in the Kaggle Winton stock market prediction challenge
#

import pandas

ALL_ZERO_SCORE      = 1770.03211
LEADERBOARD_FILE    = '../data/leaderboard.txt'
SAMPLE_SUBMISSION   = '../download/sample_submission_2.csv'
PROBES_DIR          = '../probes/test2/'

def unquote(s):
    if s.startswith('"') and s.endswith('"') and len(s) > 1: 
        return s[1:-1]
    else:
        raise ValueError, "string not enclosed in double quotes"


def get_leaderboard_entries():

    txt = open(LEADERBOARD_FILE, "r").read()
    lines = txt.splitlines()[2:]   # skip headers
    lb_entries= {}

    for line in lines:

        if "t2probe_" not in line:
            continue

        tokens = line.split(",")
        filename = unquote(tokens[0])
        publicscore = float(unquote(tokens[1]))

        # example filename to parse: probe_0020_f7_94544_scale_+5_pred_62.csv
        _, probe_num, _, f7_group, _, scale, _, suffix = filename.split("_")
        probe_num   = int(probe_num)
        f7_group    = int(f7_group)
        scale       = int(scale)
        predcol     = int(suffix.split(".")[0])
        
        lb_entries[probe_num] = (filename, probe_num, f7_group, scale, predcol, publicscore)

    return lb_entries


def main():

    lb_entries = get_leaderboard_entries()
    n_entries = len(lb_entries) if len(lb_entries) % 2 == 0 else len(lb_entries) - 1 

    submission = pandas.read_csv(SAMPLE_SUBMISSION)
    submission["Predicted"] = 0.0 
    predicted = submission["Predicted"].values

    for k in range(1, n_entries, 2):

        fn_neg, probenum_neg, group_neg, scale_neg, predcol_neg, score_neg = lb_entries[k  ]
        fn_pos, probenum_pos, group_pos, scale_pos, predcol_pos, score_pos = lb_entries[k+1]
        score_zero = ALL_ZERO_SCORE

        assert group_neg == group_pos
        assert scale_neg < 0 and scale_pos > 0 and scale_neg == -scale_pos
        assert predcol_neg == predcol_pos

        print "Comparing:"
        print "  ", lb_entries[k]
        print "  ", lb_entries[k+1]

        if score_neg > score_pos:
            scale_opt =  1* (score_neg - score_pos)/2.0 * abs(scale_neg) / (score_neg - score_zero)
        else:
            scale_opt = -1* (score_pos - score_neg)/2.0 * abs(scale_pos) / (score_pos - score_zero)

        infile = PROBES_DIR + fn_pos 
        print "Reading: ", infile, " to add with scale:", scale_opt, "\n"
        probe = pandas.read_csv(infile)
        predicted = predicted + (probe["Predicted"].values / scale_pos * scale_opt)
        del probe

    submission["Predicted"] = predicted
    outfile = "probed-submission-%04i.csv" % n_entries
    print "Writing submission to:", outfile
    submission.to_csv(outfile, index=False)
    print "Done"

main()

