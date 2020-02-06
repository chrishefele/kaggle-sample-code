

import urllib2

request = urllib2.Request("https://www.kimonolabs.com/api/csv/2i3ixo7u?apikey=qtyJXfoXzVQrHxFRbRxoZ06S13CAtOjl", 
                            headers={"authorization" : "Bearer BRALL8UhSiBI78UvVPEN0PC7F0fNYtBh"})

contents = urllib2.urlopen(request).read()

print(contents)
print

for line in contents.splitlines():
    print line

