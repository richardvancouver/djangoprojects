from googlemaps import GoogleMaps, GoogleMapsError
import urllib
import urllib2
from html2plaintext import *
import re
import os,sys
from urlparse import *
from math import *


def evaluate_loc(rec):
    url = rec['url']
    price = rec['price']
    urlContent = urllib2.urlopen(url).read()
    loc = None
    tags = []
    urlContent=urlContent.replace('<li>','')
    for lines in urlContent.split('\n'):
        if not lines.find('<!-- CLTAG') == -1:
            tag = lines.replace(' <!--','%%%<!--').split('%%%')[-1]
            tag = tag.split('-->')[0]
            tags.append(tag)
        if not lines.find('http://maps.google.com') == -1:
            loc = lines
            break
    if loc == None:
        loc = {}
        for line in tags:
            line = line.strip('<!-->')
            line = line.replace('CLTAG','')
            line = line.strip(' ')
            tag, value = line.split('=')
            loc.update({tag:value})
        try:
            locstr = '%(xstreet0)s %(xstreet1)s %(city)s %(region)s CA' % (loc)
        except:
            #print loc
            locstr = loc['GeographicArea']
    else:
        p = re.compile(""".*href=\"(?P<googleurl>.*)\".*""")
        m = p.search(loc)
        googleurl = m.group('googleurl').split('%3A')[-1]
        address = googleurl.replace('%3','')
        locstr = address.replace('+',' ')

    #print locstr

    UBC = '6224 Agricultural Road Vancouver, B.C. CA V6T 1Z1'
    def evalfunc(dist, price):
        return log(1000./price)+log(dist/10000.)

    return evalfunc(dist_from(UBC, locstr), price) 


def dist_from(destination, location):
    gmaps = GoogleMaps('ABQIAAAAAPMmDP4HCUrLtqjxnhTeXRQV_yMSNSvbo2tmQzi3qOzMvFrzcRTFTor1bOkU8NE2pW1HDlgjEDlcIQ')
    try:
        origin = location
        destination = '6224 Agricultural Road Vancouver, B.C. CA V6T 1Z1'
        dirs = gmaps.directions(origin, destination, mode='walking')
        time = dirs['Directions']['Duration']['html']
        dist = dirs['Directions']['Distance']['meters']
        route = dirs['Directions']['Routes'][0]
        return dist
    except GoogleMapsError:
        return 10000



MinPrice = 700
MaxPrice = 1300
url = 'http://vancouver.en.craigslist.ca/search/apa/van?query=UBC&srchType=A&minAsk=%d&maxAsk=%d&bedrooms=1&hasPic=1' % (MinPrice, MaxPrice)
#URL:http://vancouver.en.craigslist.ca/search/apa/van?query=UBC&srchType=A&minAsk=700&maxAsk=1300&bedrooms=1&hasPic=1
urlContent = urllib2.urlopen(url).read()

head, body = urlContent.split('sphinx')
listing = body.split('</div>')[0]

#from BeautifulSoup import BeautifulSoup as Soup
#soup = Soup(''.join(urlContent))
#body_text = soup.body(text=True)
#text = ''.join(body_text)

#print listing 

#text = html2plaintext(listing, encoding='utf-8')
#print text.encode('utf-8')

p = re.compile("""\<a href="(?P<url>.*)"\>(?P<title>.+)\</a\>""")


text = listing.replace('</p>','\n').replace('<p>','')

ads = []

for line in text.split('\n')[2:]:
    line=line.replace('- <','%<')
    items = line.split('%')
    record = {}
    try: 
        date = items[0].strip(' ')
        title = items[1].strip(' ')
        loc = items[2]
        loc = loc.split('<span')[0]
        loc = loc.replace('<font size="-1">','').replace('</font>','').strip(' ')
        m = p.match(title)
        url = m.group('url')
        title = m.group('title')
        p2 = re.compile('.*\$(?P<price>\d+).*')
        m = p2.search(title)
        price = int(m.group('price'))
    except:
        pass

    #print date, title, loc, price
    record = {'date':date, 'title':title, 'loc':loc, 'url':url, 'price':price}
    #if record == {}:
        #print date, title, loc, price
    record.update({'rate':evaluate_loc(record)})
    ads.append(record)


#print ads
print sorted(ads, key=lambda x:x['rate'], reverse=True)
    


#p = re.compile("""\<p\>\s?P<date>\s-\s\<a\shref=\"(?P<url>.*\")\>(?P<title>.*)\</a\>\s-\s\<font size="-1"\>\s\((?P<loc>.*)\)\</font\>.*\</p\>""")


sys.exit(0)

