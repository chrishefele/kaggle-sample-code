import pandas
from filename_features import parse_filename

SUBMISSION_TEMPLATE = '../download/sampleSubmission.csv'

def last_msec_digit_nonzero(fname):
    digit = parse_filename(fname)['daymsec_pos0'] 
    if digit == '0':
        return 0
    else:
        return 1

df = pandas.read_csv(SUBMISSION_TEMPLATE)
df['probability'] = df['clip'].apply(last_msec_digit_nonzero)
df.to_csv('submission.csv', index=False)

