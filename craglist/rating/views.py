# Create your views here.
from googlemaps import GoogleMaps, GoogleMapsError
import urllib
import urllib2
import re
import os,sys
from urlparse import *
from math import *

from rating.models import AD


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
            if loc.has_key(xstreet1) and loc.has_key(city) and loc.has_key(region):
                locstr = '%(xstreet0)s %(xstreet1)s %(city)s %(region)s CA' % loc
            else:
                locstr = '%(xstreet0)s Vancouver BC CA' % loc
        except:
            #print loc
            if loc.has_key('GeographicArea'):
                locstr = loc['GeographicArea']
            else:
                if not rec['title'].find('UBC') == -1 and not rec['title'].find('ubc') == -1:
                    rec['dist'] = 5000
                    return evalfunc(5000, price)
                else:
                    locstr = 'Unknown'
    else:
        p = re.compile(""".*href=\"(?P<googleurl>.*)\".*""")
        m = p.search(loc)
        googleurl = m.group('googleurl').split('%3A')[-1]
        address = googleurl.replace('%3','')
        locstr = address.replace('+',' ')

    #print locstr

    UBC = '6224 Agricultural Road Vancouver, B.C. CA V6T 1Z1'
    def evalfunc(dist, price):
        res = 0.1*log(1000./price)+log(10000./dist)
        if res == None:
            print res
            raise Error
        else:
            return res

    distance = dist_from(UBC, locstr)
    rec.update({'dist':distance/1000.})
    return evalfunc(distance, price) 


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



def listing(reqest):

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
        linerec = line
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
        record = {'date':date, 'title':title, 'loc':loc, 'url':url, 'price':price, 'line':linerec}

        exist = AD.objects.filter(url__icontains=record['url'])
        if len(exist) == 0:
            exist = AD.objects.filter(title__icontains=record['title']) 
        if len(exist) == 0:
            record.update({'rating':evaluate_loc(record)})
            rec = AD(**record)
            rec.save()


    ads = AD.objects.all()
        #ads.append(record)


    


    sorted_list = sorted(ads, key=lambda x:x.rating, reverse=True)
    #print ads

    from django.http import HttpResponse, HttpResponseRedirect
    from django.template import loader, Context
    from django.contrib.flatpages.models import FlatPage
    from django.shortcuts import render_to_response

    return render_to_response('home.html', {'results': sorted_list})


