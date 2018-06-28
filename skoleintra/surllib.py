# -*- coding: utf-8 -*-

import cookielib
import urllib
import config
import mechanize
import bs4
import urlparse
import cgi
import os
import sys
import re
import datetime
import time


def absurl(url):
    if url and url[0] != '/':
        return url
    return 'https://%s%s' % (config.HOSTNAME, url)


def unienc(s):
    if type(s) == unicode:
        return s.encode('utf-8')
    else:
        return s


def beautify(data):
    # Maybe due to 'wide' unicode char, e.g., smiley &#128516;
    # ValueError: unichr() arg not in range(0x10000) (narrow Python build)
    return bs4.BeautifulSoup(data, 'lxml')


class Browser(mechanize.Browser):
    def __init__(self):
        mechanize.Browser.__init__(self)

        # Cookie Jar
        self._cj = cookielib.LWPCookieJar()
        self.set_cookiejar(self._cj)

        # Browser options
        self.set_handle_equiv(True)
        # self.set_handle_gzip(True)
        self.set_handle_redirect(True)
        self.set_handle_referer(True)
        self.set_handle_robots(False)

        # Follows refresh 0 but does not hang on refresh > 0
        self.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),
                                max_time=60)

        # Want debugging messages?
        if False:
            self.set_debug_http(True)
            self.set_debug_redirects(True)
            self.set_debug_responses(True)

        # User-Agent
        self.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; '
             'rv:5.0.1) Gecko/20100101 Firefox/5.0.1'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;'
             'q=0.9,*/*;q=0.8')]

        # load browser state
        sfn = self._browser_state_filename()
        self._lastIndex = ''
        if os.path.isfile(sfn):
            if not config.SKIP_CACHE:
                config.log(u'Indlæser tidligere browsertilstand fra %s' % sfn)
                self._cj.load(sfn, True, True)
                lst = open(sfn).read().strip().split()
                if len(lst) > 3 and lst[-2] == 'Index:':
                    self._lastIndex = lst[-1]
            else:
                config.log(u'Indlæser ikke tidligere browsertilstand '
                           u'fra %s pga --skipcache' % sfn)

    def _browser_state_filename(self):
        fn = '%s-%s.state' % (config.HOSTNAME, config.USERNAME)
        return os.path.join(config.CACHE_DN, fn)

    def save_state(self):
        sfn = self._browser_state_filename()
        self._cj.save(sfn, ignore_discard=True, ignore_expires=True)
        if self._lastIndex:
            open(sfn, 'a').write('# Index: %s\n' % self._lastIndex)

    def open(self, url, *args, **aargs):
        if type(url) in [str, unicode]:
            surl = url
        else:
            surl = url.get_full_url()
        config.log('Browser.open %s' % surl, 3)
        resp = mechanize.Browser.open(self, url, *args, **aargs)
        if re.match('.*/parent/[0-9]*/[^/]*/Index', surl):
            self._lastIndex = surl
        self.save_state()
        return resp

    def get_last_index(self):
        return self._lastIndex


def getBrowser():
    global _browser
    if _browser is None:
        _browser = Browser()
    return _browser


_browser = None
_skole_login_done = False


def skoleLogin():
    'Login to the SkoleIntra website'
    global _skole_login_done
    global br, resp, data
    if _skole_login_done:
        return _skole_login_done

    br = getBrowser()
    config.log(u'Login', 2)

    config.log(u'Login på skoleintra')
    url = u'https://%s/Account/IdpLogin' % config.HOSTNAME
    if br.get_last_index():
        urlL = br.get_last_index()
        if urlL.startswith('/'):
            url += urlL[1:]
        else:
            url = urlL
        config.log(u'Genbruger sidst kendte forside URL %s' % url, 2)
    else:
        config.log(u'Logger på via %s' % url, 2)

    resp = br.open(url)
    for round in range(5):  # try at most 5 times before failing
        url = resp.geturl()
        data = resp.read()
        config.log(u'Login næste skridt %s' % url, 3)

        forms = list(br.forms())
        if len(forms) == 1:
            br.form = forms[0]

        if url == br.get_last_index() and data:
            # we are fine / logged in
            config.log(u'Succesfuldt log ind til %s' % url, 1)
            _skole_login_done = beautify(data)
            return _skole_login_done

        if len(forms) == 1 and (
                '/sso/ssocomplete' in url or
                re.search('<form[^>]*name=.relay.', data)):
            # One of the intermediate small pages on the way
            resp = br.submit()
            continue

        if url.startswith('https://login.emu.dk/'):
            config.log(u'Uni-login med brugernavn %r' % config.USERNAME, 3)
            assert(config.LOGINTYPE != 'alm')  # This must be uni login
            br['user'] = 'TEST'
            br['pass'] = sys.argv[1]
            resp = br.submit()
            continue

        if '/Account/IdpLogin' in resp.geturl() \
                and len(forms) == 1 \
                and 'UserName' in br and 'Password' in br:

            if 'ikke adgang' in data:
                config.log(u'Logind giver en fejlmeddelse -- '
                           u'har du angivet korrekt kodeord? '
                           u'Check konfigurationsfilen, angiv evt. nyt '
                           u'kodeord med --password eller --config ELLER '
                           u'prøv igen senere...', -2)
                sys.exit(1)

            # this is the main login page
            if config.LOGINTYPE != 'alm':
                # UNI-login
                links = br.links(url_regex=re.compile(
                    '.*RedirectToUniLogin.*'))
                if not links:
                    config.log(u'Kan IKKE finde LOG PÅ MED UNILOGIN '
                               u'linket på siden?', -1)
                    sys.exit(1)
                config.log(u'Går videre til uni-login', 3)
                resp = br.follow_link(links[0])
                continue
            else:
                config.log(u'Bruger alm. login med brugernavn %r' %
                           config.USERNAME, 3)
                # "Ordinary login"
                br['UserName'] = config.USERNAME
                br['Password'] = config.b64dec(config.PASSWORD)
                resp = br.submit()
                continue
        break

    config.log(u'skoleLogin: Kan ikke logge på ForældreIntra?', -1)
    config.log(u'skoleLogin: Vi var nået til flg URL', -1)
    config.log(u'skoleLogin: %s' % url, -1)
    config.log(u'skoleLogin: Check at URLen er rigtig '
               u'og prøv evt. igen senere', -1)
    sys.exit(0)


def url2cacheFileName(url, postData):
    assert(type(url) == str)
    if postData:
        url += postData
    up = urlparse.urlparse(url)
    parts = [config.CACHE_DN,
             up.scheme,
             up.netloc,
             urllib.url2pathname(up.path)[1:] + '.cache']
    if up.query:
        az = re.compile(r'[^0-9a-zA-Z]')
        for (k, vs) in sorted(cgi.parse_qs(up.query).items()):
            xs = [az.sub(lambda x: hex(ord(x.group(0))), x) for x in [k] + vs]
            parts[-1] += '_' + '-'.join(xs)

    cfn = os.path.join(*parts)
    if type(cfn) == unicode and not os.path.supports_unicode_filenames:
        cfn = cfn.encode('utf-8')
    return cfn


def skoleGetURL(url, asSoup=False, noCache=False, postData=None):
    '''Returns data from url as raw string or as a beautiful soup'''
    if type(url) == unicode:
        url, uurl = url.encode('utf-8'), url
    else:
        uurl = url.decode('utf-8')

    # FIXME? fix urls without host names

    # Sometimes the URL is actually an empty string
    if not url:
        data = ''
        if asSoup:
            data = beautify(data)
            data.cachedate = datetime.date.today()
            return data
        else:
            return data

    if type(postData) == dict:
        pd = {}
        for (k, v) in postData.items():
            pd[unienc(k)] = unienc(v)
        postData = urllib.urlencode(pd)
    else:
        postData = unienc(postData)

    lfn = url2cacheFileName(url, postData)

    if os.path.isfile(lfn) and not noCache and not config.SKIP_CACHE:
        config.log('skoleGetURL: Henter fra cache %s' % uurl, 2)
        config.log('skoleGetURL: %s' % unienc(lfn), 2)
        data = open(lfn, 'rb').read()
    else:
        qurl = urllib.quote(url, safe=':/?=&%')
        config.log(u'skoleGetURL: Prøver at hente %s' % qurl, 2)
        skoleLogin()
        br = getBrowser()
        resp = br.open(qurl, postData)
        data = resp.read()
        # write to cache
        ldn = os.path.dirname(lfn)
        if not os.path.isdir(ldn):
            os.makedirs(ldn)
        open(lfn, 'wb').write(data)
        config.log(u'skoleGetURL: Gemmer siden i filen %r' % lfn, 2)

    if asSoup:
        data = beautify(data)
        data.cachedate = datetime.date.fromtimestamp(os.path.getmtime(lfn))
        data.cacheage = (time.time() - os.path.getmtime(lfn))/(24 * 3600.)
        return data
    else:
        return data
