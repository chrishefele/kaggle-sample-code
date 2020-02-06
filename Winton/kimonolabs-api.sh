# note on the kimono site, need to currently manually trigger recollection
# so in production, put it on a schedule (e.g. daily)

# note in the URL, csv is added to get the csv. Remove it to get json
# also note headers returned 

curl --header "authorization: Bearer BRALL8UhSiBI78UvVPEN0PC7F0fNYtBh" \
     --include \
     --request GET "https://www.kimonolabs.com/api/csv/2i3ixo7u?apikey=qtyJXfoXzVQrHxFRbRxoZ06S13CAtOjl"

