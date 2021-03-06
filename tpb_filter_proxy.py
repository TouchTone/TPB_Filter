#!/usr/bin/python

# Simple filter app to remove dead torrents frm TBP results

import cherrypy, requests, re, os, time, json, base64, traceback
from bs4 import BeautifulSoup
from functools import partial

baseurl="http://thepiratebay.se/"
basetorperpage = 30
refreshtime = 600

# Image getters
imgstyle = 'max-width:100%; display: block; margin-left: auto; margin-right: auto;'


def makeImage(bs, url, img, referer=False, headers=None):
    if referer:
        img = "http://localhost:8080/addReferer?url=" + img
        if headers:
            img += "&headers=" + base64.b64encode(json.dumps(headers))
    s = bs.new_tag("span")
    if url:
        a = bs.new_tag("a")
        a['href'] = url
        a.append(url)
        s.append(a)
    i = bs.new_tag("img")
    i['style'] = imgstyle
    i['src'] = img
    s.append(i)
    return s


def IG_id(bs, session, url, idval):
    return IG_tags(bs, session, url, {"id" : idval})


def IG_tags(bs, session, url, tagvals, method="get", referer=False, headers=None, postdata=None):
    try:
        if not url.startswith("http"):
            url = "http://" + url
            
        site = url.split('/')[2]
        
        if method == "get":
            r = session.get(url, headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "User-Agent": "Mozilla",
                "Referer": url
            })
        else:
            r = session.post(url, headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "User-Agent": "Mozilla",
                "Referer": url
            }, data=postdata)

        bs = BeautifulSoup(r.content)
        
        img = bs.find("img", **tagvals)
        if img:
            return makeImage(bs, url, img["src"], referer, headers)

    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)
	print traceback.format_exc()
    return None


def IG_multitags(bs, session, url, tagsets, method="get", referer=False, headers=None, postdata=None):
    for t in tagsets:
        ret = IG_tags(bs, session, url, t, method, referer, headers, postdata)
        if ret:
            return ret
    return None


def IG_regex(bs, session, url, regex):
    try:
        nurl = re.sub(regex[0], regex[1], url)
        return makeImage(bs, url, nurl)
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None
    


def IG_blobopicsbiz(bs, session, url):
    try:
        pid = url[url.find("share-")+6:url.find(".html")]
        return makeImage(bs, url, "http://blobopics.biz/image-" + pid + ".jpg")
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None
    


def IG_fileeq(bs, session, url):
    try:
        ii = url.find("file=")

        if ii >= 0:
            src = url[ii+5:]
            if url.startswith("http://"):
                url = url[7:]
            f = url.split('/',1)
            return makeImage(bs, url, "/addReferer?url=http://" + f[0] + "/images/" + src)
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)
        
    return None


def IG_torrentpreviewscom(bs, session, url):
    try:
        r = session.get(url)
        bs = BeautifulSoup(r.content)
        
        out = bs.new_tag("span")
        a = bs.new_tag("a")
        a["href"] = url
        a.append(url)
        out.append(a)
        
        for img in bs.findAll("img", class_ = "img-responsive"):
            out.append(makeImage(bs, None, img["src"]))
            
        return out
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None


def IG_xbustyorg(bs, session, url):
    try:
        r = session.get(url)
        bs = BeautifulSoup(r.content)
        
        out = bs.new_tag("span")
        a = bs.new_tag("a")
        a["href"] = url
        a.append(url)
        out.append(a)
        
        for img in bs.findAll("img", title = True):
            if img["src"].startswith("/uploads"):
                out.append(makeImage(bs, None, "http://x-busty.org" + img["src"]))
            
        return out
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None


def IG_amateurhubcom(bs, session, url):
    try:         
        r = session.get("http://" + url)
        bs = BeautifulSoup(r.content)
        
        out = bs.new_tag("span")
        a = bs.new_tag("a")
        a["href"] = url
        a.append(url)
        out.append(a)
        
        for img in bs.findAll("img", alt = "image"):
            if img.parent["href"]:
                temp = bs.new_tag("span")
                temp.append("http:" + img.parent["href"])
                out.append(the.imageReplace(bs, temp))
            
        return out
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None


def IG_sampleviewscom(bs, session, url):
    try:         
        if not url.startswith("http://"):
            url = "http://" + url
        r = session.get(url)
        bs = BeautifulSoup(r.content)
        
        out = bs.new_tag("span")
        a = bs.new_tag("a")
        a["href"] = url
        a.append(url)
        a.append(bs.new_tag("br"))
        out.append(a)
        
        for img in bs.findAll("img", class_ = "img-responsive"):
            print "SV: %s" % img
            temp = bs.new_tag("span")
            out.append(temp)
            temp.append(img["src"])
            i = bs.new_tag("img")
            i["src"] = img["src"]
            i['style'] = imgstyle
            temp.append(i)
            
        return out
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None

    
def IG_hideimgcom_gallery(bs, session, url):
    try:         
        if not url.startswith("http:"):
            url = "http://" + url
        r = session.get(url)
        bs = BeautifulSoup(r.content)
        
        out = bs.new_tag("span")
        a = bs.new_tag("a")
        a["href"] = url
        a.append(url)
        out.append(a)
        
        for img in bs.findAll("div", class_ = "gallery-thumb"):
            iurl = img.div["onclick"]
            iiurl = iurl[iurl.find("?v="):-1]
            iiurl = "http://hideimg.com/images/" + iiurl

            out.append(the.makeImage(bs, iurl, iiurl))
        
        return out
        
    except Exception, e:
        print "***Caught %s trying to get image from %s!" % (e, url)        
        
    return None

    
    
the = None
    
class TBPFilter(object):

    def __init__(self):
        global the        
        the = self
        
        self.session = requests.Session()
        self.session.get(baseurl, headers={'referer': baseurl + '/browse/603'}, verify=False)

        self.lastpage = baseurl
        self.lastget = 0
        self.cache = {}
        
        # Config options
        self.torperpage = 40
        
        # Filter options
        self.invertFilter = False
        
        # Number of seeds
        self.filterSeeds = True
        self.filterSeedsMin = 3
        self.filterSeedsMax = 1000
        
        # Number of leechers
        self.filterLeechs = False
        self.filterLeechsMin = 1
        self.filterLeechsMax = 1000
        
        # File size (in MiB)
        self.filterSize = False
        self.filterSizeMin = 0
        self.filterSizeMax = 10

        
    def imageReplace(self, bs, tag):
        igs = [("3xplanet.com", partial(IG_tags, tagvals={"alt": "picContent"})),
               ("image.bayimg.com", partial(IG_regex, regex=("(.*)", "\\1"))),
               ("bayimg.com", partial(IG_id, idval="mainImage")),
               ("interimagez.com", partial(IG_id, idval="full_image")),
               ("244pix.com", IG_fileeq),
               ("imagecurl.org", IG_fileeq),
               ("pixxx.me", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}])),
               ("imgbabes.net", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}])),
               ("imagesnt.com", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}], referer=True)),
               ("celebrityclips.org", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}])),
               ("unloadhost.com", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}])),
               ("imgdetop.com", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}], method="post")),
               ("pixxxsex.com", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}])),
               ("imgmen.com", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}])),
               ("imgcorn.net", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}],
                                       headers={
                                           "Cookie": "PHPSESSID=03289ce037afb1ad88574fcfd8c532d9; HstCfa2849557=1416604688169; HstCmu2849557=1416604688169; c_ref_2849557=http%3A%2F%2Flocalhost%3A8080%2Ftorrent%2F11573849%2FWowGirls_-_Vanessa_-_The_One_For_Me_(19_Nov_2014); HstCla2849557=1417089446978; HstPn2849557=7; HstPt2849557=55; HstCnv2849557=7; HstCns2849557=9"})),
               ("imgza.biz", partial(IG_multitags, tagsets=[{"class_": "centred"}, {"class_": "centred_resized"}], method="post", postdata={"imgContinue":"Click"})),
               ("imgbays.com", partial(IG_regex, regex=("(.*)", "/getImagebays?url=\\1"))),
               ("imgreserve.com", partial(IG_regex, regex=(".*\\?v=([0-9]*)", "http://imgreserve.com/images/\\1.jpg"))),
               ("blobopics.biz", IG_blobopicsbiz),
               ("torrentpreviews.com", IG_torrentpreviewscom),
               ("postimg.org", partial(IG_multitags, tagsets=[{"width": "1280px"}, {"width": "1024px"}, {"width": "1000px"}])),
               ("imghorny.biz", partial(IG_regex, regex=(".*share-([^.]*)\.html", "http://imghorny.biz/image.php?id=\\1"))),
               ("imgswift.com", partial(IG_tags, tagvals={"class_": "pic"})),
               ("torrentimagehost.com", partial(IG_tags, tagvals={"data-load": "full"})),
               ("x-busty.org", IG_xbustyorg),
               ("hideimg.com/?g=", IG_hideimgcom_gallery),
               ("hideimg.com", partial(IG_regex, regex=(".*v=([0-9]*)", "http://hideimg.com/images/\\1.jpg"))),
               ("amateur-hub.com", IG_amateurhubcom),
               ("sampleviews.com", IG_sampleviewscom),
               ("imgcoffee.biz", partial(IG_regex, regex=(".*share-([^.]*)\.html", "http://imgcoffee.biz/image.php?id=\\1"))),
               ("imgtwist.org", partial(IG_regex, regex=(".*v=([0-9]*)", "http://imgtwist.org/images/\\1.jpg"))),
               ("hideimg.org", partial(IG_regex, regex=(".*v=([0-9]*)", "http://hideimg.org/images/\\1.jpg"))),
               ("stooorage.com", partial(IG_tags, tagvals={"onload": True})),
               ("imgrest.com", partial(IG_tags, tagvals={"alt": re.compile("[0-9a-z]*.(?:jpg|jpeg|png|gif)")}))
        ]

        if False:
            text = " ".join(tag.stripped_strings)
            for prov,func in igs:
                for l in re.finditer(prov + "/[^ ]*", text):
                    n = func(bs, self.session, l.group())
                    if n:
                        i.replaceWith(n)
                        break
                    
        else:
            for i in tag.find_all("a"):
                url = i["href"]                   
                for prov,func in igs:
                    if prov in url:
                        n = func(bs, self.session, url.strip())
                        if n:
                            i.replaceWith(n)
                            break
         
        return tag 
      
        
    def getPage(self, url):
    
        try:
            r = self.session.get(url, verify=False, headers={'referer': self.lastpage})
            r.raise_for_status()
        except Exception, e:
            print "Caught %s trying to get %s!" % (e, url)
            return "Caught %s trying to get %s!" % (e, url)
            
        cont = r.content
        
        if url.endswith('.css'):
            cherrypy.response.headers['Content-Type']= 'text/css'
        elif url.endswith('.png') or url.endswith('.jpg') or url.endswith('.gif'):
            cherrypy.response.headers['Content-Type']= 'image/' + url.rsplit('.',1)[1]
        
        if cont.startswith('<!DOCTYPE'):
            self.lastpage = url
            self.lastget = time.time()
            
            bs = BeautifulSoup(r.content)
            
            # Take out ads
            for rem in ['sky-right', 'sky-banner']:
                d = bs.find(id=rem)
                if d:
                    d.extract()
                
            for i in bs.find_all("iframe"):
                i.extract()
                
            for i in bs.find_all("script"):
                i.extract()
             
            # Replace image links with actual images
            nfo = bs.find(class_="nfo")
            
            if nfo:      
                self.imageReplace(bs, nfo)

            cont = str(bs)
            
            # Fix messes. Not sure what's happening, the /browse URLs are just messed up.
            cont = re.sub(r'href="//browse/([0-9]*)/([0-9]*)/([0-9]*)', r'href="/browse/\1/\2/\3', cont)
            
            return cont
        else:
            return r.content


    @cherrypy.expose
    def default(self, *args, **kwargs):  
        url = baseurl + '/'.join(args)
        if kwargs:
            url += "?"
            for k,v in kwargs.iteritems():
                url += k + "=" + v + "&"
            url = url[:-1]
        
        print "DEFAULT:", args, kwargs, url
          
        return self.getPage(url)
 
 
    @cherrypy.expose
    def filters(self, *args, **kwargs):   
        print "FILTERS:",args, kwargs        
        
        for p in "Seeds", "Leechs", "Size":
            self.__dict__["filter"+p] = p+"_enable" in kwargs.keys()
            self.__dict__["filter"+p+"Min"] = float(kwargs[p+"_min"])
            self.__dict__["filter"+p+"Max"] = float(kwargs[p+"_max"])
        
        self.cache = {}
        
        raise cherrypy.HTTPRedirect(cherrypy.request.headers['Referer'])
        
 
    @cherrypy.expose
    def s(self, *args, **kwargs):   
        return self.filteredPage("search/%s" % kwargs["q"], ["0","99","0"])
    
 
    @cherrypy.expose
    def browse(self, *args):  
        if len(args) > 0:
            return self.filteredPage("browse/" + args[0], args[1:])
        else:
            return self.getPage(baseurl + "/browse")

  
    @cherrypy.expose
    def search(self, *args):   
        return self.filteredPage("search/" + args[0], args[1:])
  
  
    @cherrypy.expose
    def addReferer(self, url):
        if url.startswith("http"):
            site = url.split('/')[2]
        else:
            site = url.split('/')[0]
        headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                   "User-Agent": "Mozilla/5.0",
                   "Referer": site}
        if "headers" in kwargs:
            h = json.loads(base64.b64decode(kwargs["headers"]))
            headers.update(h)
        r = self.session.get(url, headers=headers, verify=False)
        return r.content

    @cherrypy.expose
    def getImagebays(self, url):
        try:
            r = self.session.get(url)
            bs = BeautifulSoup(r.content)

            for c in ["centred", "centred_resized"]:
                img = bs.find("img", class_=c)

                if img:
                    r2 = self.session.get(img["src"])
                    cherrypy.response.headers['Content-Type']= 'image/jpeg'
                    return r2.content

        except Exception, e:
            print "***Caught %s trying to load image from %s!" % (e, url)

        return None


    def filteredPage(self, base, args):
    
        print "FILTER:", base, len(args), args
        
        sortid = 3
        page = 0
        
        if len(args) == 1:
            sortid = int(args[0])
        elif len(args) == 2:
            page = int(args[0])
            sortid = int(args[1])
        
        key = "%s+%s" % (base, sortid)
        
        print "FILTER: base=%s sort=%s page=%s" % (base, sortid, page)
        
        try:
            lastpage,area = self.cache[key]
        except KeyError:
            lastpage = 0
            area = []

        # Refresh of needed
        if time.time() > self.lastget + refreshtime:
            lastpage = 0
            area = []
            try:
                del self.cache()[key]
            except Exception:
                pass
            

        start = page * self.torperpage
        end = (page + 1) * self.torperpage
        
        while len(area) < end:
            
            print "*** Getting ", baseurl + "/%s/%d/%d" % (base, lastpage, sortid)
            r = self.session.get(baseurl + "/%s/%d/%d" % (base, lastpage, sortid), verify=False,
                                 headers={'referer': self.lastpage})
            r.raise_for_status()
        
            lastpage += 1
            
            bs = BeautifulSoup(r.content)
            
            tortable = bs.find("table", id="searchResult")
            nimg = bs.find(name="img", attrs={"src" : "/static/img/next.gif"})
            
            # Did we reach the end?
            if not tortable or not nimg:
                break
                
            for tor in tortable.find_all("tr"):  
                         
                if tor.has_attr("class") or tor.td.has_attr("colspan"):
                    continue
                    
                tds = tor.find_all("td")
                if len(tds) != 4:
                    print "Found unexpected torrent line: ", tor
                    continue
                
                # Filter torrents
                res = True
                if self.filterSeeds:
                    seeds = int(tds[2].string)

                    if seeds < self.filterSeedsMin:
                        res = False
                    if seeds > self.filterSeedsMax:
                        res = False
                
                if self.filterLeechs:
                    leechs = int(tds[3].string)

                    if leechs < self.filterLeechsMin:
                        res = False
                    if leechs > self.filterLeechsMax:
                        res = False

                if self.filterSize:
                    t = tds[1].get_text()
                    t = t[t.find("Size") + 5:t.find(", UL")]
                    size, unit = t.split(u'\xa0')
                    units = {"MiB": 1, "GiB": 1000, "KiB": 0.001, "B": 0.000001}

                    size = float(size) * units[unit]
                    
                    if size < self.filterSizeMin:
                        res = False
                    if size > self.filterSizeMax:
                        res = False
                
                if self.invertFilter:
                    res = not res
                    
                if not res:
                    continue
                
                area.append(str(tor))
        
        self.cache[key] = (lastpage, area)
        
        # Replace torrents from original page with filtered ones        
        r = self.session.get(baseurl + '/' + base + '/' + '/'.join(args), verify=False,
                             headers={'referer': self.lastpage})
        r.raise_for_status()

        bs = BeautifulSoup(r.content)

        # Take out ads
        for rem in ['sky-right', 'sky-banner']:
            d = bs.find(id=rem)
            if d:
                d.extract()

        for i in bs.find_all("iframe"):
            i.extract()

        for i in bs.find_all("script"):
            i.extract()
 
        # Do we have a separate number div? Take it out
        nd = bs.find("div", id="content").find("div", align="center")
        if nd:
            print nd
            nd.decompose()
     
        # Table replacement 
        newtable = ""
        
        # UI for filters
        
        newtable += '<div style="text-align:center;"><form action="/filters">Filters: '
        
        for p in "Seeds", "Leechs", "Size":
            if self.__dict__["filter"+p]:
                enable = "checked"
            else:
                enable = ""
            newtable += '''<input type="checkbox" name="{p}_enable" value="Enable" {enable}/>{p} Min:<input type="text" name="{p}_min" size="6" value="{min:.0f}" /> 
                            Max:<input type="text" name="{p}_max" size="6" value="{max:.0f}" />
                        '''.format(p=p, enable=enable, min=self.__dict__["filter" + p + "Min"],
                                   max=self.__dict__["filter" + p + "Max"])

        newtable += '(MB) <input type="submit" value="Change"/></form></div>'

        # Replace table
        tortable = bs.find("table", id="searchResult")

        # Empty search results?
        if not tortable:
            return str(bs)
            
        sorts = [ 13, 1, 3, 5, 7, 9 ]
        for s in xrange(len(sorts)):
            if sorts[s] == sortid:
                sorts[s] += 1
                break       

        if len(area) != 0:
            newtable += '''<table id="searchResult"><thead id="tableHead"><tr class="header">

            <th><a href="/{base}/0/{sorts[0]}" title="Order by Type">Type</a></th>
            <th><a href="/{base}/0/{sorts[1]}" title="Order by Name">Name</a>
                <a href="/{base}/0/{sorts[2]}" title="Order by Uploaded">Uploaded</a>
                <a href="/{base}/0/{sorts[3]}" title="Order by Size">Size</a></th>
            <th><abbr title="Seeders"><a href="/{base}/0/{sorts[4]}" title="Order by Seeders">SE</a></abbr></th>
            <th><abbr title="Leechers"><a href="/{base}/0/{sorts[5]}" title="Order by Leechers">LE</a></abbr></th>

            </tr></thead>'''.format(base=base, sorts=sorts)

            for t in xrange(min(start, len(area) - 1),min(end, len(area))):
                newtable += area[t]

            newtable += '<tr><td colspan="9" style="text-align:center;">'

            fp = max(page - 15, 0)
            lp = min(fp + 30, 100)

            for p in xrange(fp,lp):
                par = { "base" : base, "ppage" : page - 1, "npage" : page + 1, "p" : p, "p1" : p+1, "sort" : sortid}

                if p == fp and p != 0:
                    newtable += '<a href="/{base}/{ppage}/{sort}"><img src="/static/img/prev.gif" border="0" alt="Previous"></a> '.format(**par)
                elif p == lp - 1 and p != 99:
                    newtable += '<a href="/{base}/{npage}/{sort}"><img src="/static/img/next.gif" border="0" alt="Next"></a> '.format(**par)
                else:
                    newtable += '<a href="/{base}/{p}/{sort}">{p1}</a> '.format(**par)

            newtable += "</td></tr></table>"
        
        else:

            newtable = '<span style="text-align:center; font-size: 20;">No Results!</span>'

        tortable = tortable.replaceWith(BeautifulSoup(newtable))
                  
        return str(bs)



root = os.path.abspath(os.path.dirname(__file__))

conf = {'/' :      {'tools.sessions.on': True, 
                    'tools.sessions.storage_type': 'ram' },
        '/static/css-new/pirate6.css':    
                   {'tools.staticfile.on': True,              
                    'tools.staticfile.filename': '%s/pirate6.css' % root}
        }
    
cherrypy.config.update(conf)  
   
cherrypy.quickstart(TBPFilter())
