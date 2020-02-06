from collections import defaultdict

donor_project_count = defaultdict(int)
project_donor_count = defaultdict(int)

def print_counts(counts):
    counts_iter = sorted(((v,k) for k,v in counts.iteritems()), reverse=True)
    for v, k in counts_iter:
        print k, ",", v

fin = open('../download/donations.csv')
fin.readline() # bypass header

for line in fin:
    tokens = line.split(',')
    projectid    = tokens[1]
    donor_acctid = tokens[2]

    donor_project_count[donor_acctid] += 1
    project_donor_count[projectid   ] += 1

print_counts(donor_project_count)


#donationid,projectid,donor_acctid,donor_city,donor_state,donor_zip,is_teacher_acct,donation_timestamp,donation_to_project,donation_optional_support,donation_total,dollar_amount,donation_included_optional_support,payment_method,payment_included_acct_credit,payment_included_campaign_gift_card,payment_included_web_purchased_gift_card,payment_was_promo_matched,via_giving_page,for_honoree,donation_message

