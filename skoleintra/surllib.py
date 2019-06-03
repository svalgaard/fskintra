# -*- coding: utf-8 -*-

import cgi
import cookielib
import datetime
import mechanize
import hashlib
import os
import re
import sys
import time
import urllib
import urllib2
import urlparse

import config
import sbs4
import pgConfirm


def absurl(url):
    '''Turn an URL into an absolute URL'''
    if url and url[0] != '/':
        return url
    return 'https://%s%s' % (config.options.hostname, url)


def unienc(s):
    '''Ensure that s is encoded as a binary string (not unicode)'''
    if type(s) == unicode:
        return s.encode('utf-8')
    else:
        return s


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

        # Browser-state (not including cookies)
        self.state = {
            'index': None,
            'dialogue': None,
            'lastUpdateTime': None,
            'lastUpdateURL': None,
            'header': [],
        }
        self.firstPass = True

        # Load browser state
        sfn = self._browser_state_filename()
        if os.path.isfile(sfn):
            if not config.options.skipcache:
                config.log(u'Henter tidligere browsertilstand fra %s' % sfn, 2)
                self._cj.load(sfn, True, True)
                for st in open(sfn).read().strip().split('\n'):
                    sp = st.split()
                    if st.startswith('# fskintra: ') and len(sp) == 4:
                        self.state[sp[-2]] = sp[-1]
                    if st.startswith('# fskintra-header: '):
                        _, header = st.split(': ', 1)
                        k, v = header.split(': ')
                        self.state['header'].append((k, v))
                if self.state['header']:
                    self.addheaders = self.state['header']
            else:
                config.log(u'Indlæser ikke tidligere browsertilstand '
                           u'fra %s pga --skipcache' % sfn)

    def _browser_state_filename(self):
        fn = '%s-%s.state' % (config.options.hostname, config.options.username)
        return os.path.join(config.options.cachedir, fn)

    def saveState(self):
        sfn = self._browser_state_filename()
        self._cj.save(sfn, ignore_discard=True, ignore_expires=True)
        fd = open(sfn, 'a')
        for (k, v) in sorted(self.state.items()):
            if v:
                if k == 'header':
                    for k, v in v:
                        fd.write('# fskintra-header: %s: %s\n' % (k, v))
                    pass
                else:
                    fd.write('# fskintra: %s %s\n' % (k, v))
        fd.close()

    def open(self, url, *args, **aargs):
        ofp, self.firstPass = self.firstPass, False
        if type(url) in [str, unicode]:
            furl = url
        else:
            furl = url.get_full_url()
        config.log('Browser.open == %s' % furl, 4)
        resp = mechanize.Browser.open(self, url, *args, **aargs)
        surl = resp.geturl()
        config.log('Browser.open => %s' % surl, 4)
        self.firstPass = ofp
        if ofp and re.match('.*/parent/[0-9]*/[^/]*/Index', surl):
            self.state['index'] = absurl(surl)
            for a in br.links(text_regex=re.compile('Besked')):
                dt = a.url.split('/')[-1]
                if dt:
                    self.state['dialogue'] = dt

        self.saveState()
        return resp

    def getState(self, key):
        return self.state.get(key)

    def setState(self, key, value):
        assert(type(value) == str)
        self.state[key] = value.strip()
        if not self.state[key]:
            del self.state[key]


def getBrowser():
    '''Get the currently used browser instance'''
    global _browser
    if _browser is None:
        _browser = Browser()
    _browser.set_handle_equiv(False)
    return _browser


_browser = None
_skole_login_done = False


def skoleLogin():
    'Login to the ForældreIntra website'
    global _skole_login_done
    global br, resp, data
    if _skole_login_done:
        return _skole_login_done

    br = getBrowser()
    config.log(u'Login', 2)

    config.log(u'Log ind på ForældreIntra')
    url = absurl('/Account/IdpLogin')
    if br.getState('index'):
        url = br.getState('index')
        config.log(u'Genbruger sidst kendte forside URL %s' % url, 2)
    else:
        config.log(u'Logger på via %s' % url, 2)

    try:
        resp = br.open(url)
    except urllib2.HTTPError as e:
        config.log(u'skoleLogin: Kan ikke logge på ForældreIntra?', -1)
        config.log(u'skoleLogin: URL: %s' % url, -1)
        config.log(u'skoleLogin: Fejlkode: %d' % e.code, -1)
        if e.code == 404 and not br.getState('index'):
            # Login tried at the default URL
            config.log(u'skoleLogin: Bruger du det rette `hostname` til det '
                       u'nye ForældreIntra i konfigurationsfilen?', -1)

        config.log(u'skoleLogin: Check at URLen er rigtig '
                   u'og prøv evt. igen senere', -1)
        sys.exit(1)

    N = 6
    for round in range(N):  # try at most N times before failing
        url = resp.geturl()
        data = resp.read()
        config.log(u'Log ind skridt %d/%d: %s' % (round + 1, N, url), 3)

        forms = list(br.forms())
        if len(forms) == 1:
            br.form = forms[0]

        if url.endswith('/ConfirmContacts'):
            # Confirm contact details
            config.log(u'Bekræfter kontaktoplysninger på %s' % url, 1)
            pgConfirm.skoleConfirm(sbs4.beautify(data))
            # Click "Bekræft"
            for form in br.forms():
                if form.attrs.get('action').endswith('/Confirm'):
                    br.form = form
                    break
            else:
                config.log(u'Kunne ikke bekræfte kontaktoplysninger på %s'
                           % url, -1)
                sys.exit(1)
            resp = br.submit(nr=0)
            continue

        if url == br.getState('index') and data:
            # we are fine / logged in
            config.log(u'Succesfuldt log ind til %s' % url, 2)
            _skole_login_done = sbs4.beautify(data)
            return _skole_login_done

        if len(forms) == 1 and (
                '/sso/ssocomplete' in url or
                re.search('<form[^>]*name=.relay.', data)):
            # One of the intermediate small pages on the way
            resp = br.submit()
            continue

        if url.startswith('https://login.emu.dk/'):
            config.log(u'Uni-login med brugernavn %r' %
                       config.options.username, 3)

            if 'forkert brugernavn' in data.lower():
                config.log(u'Log ind giver en fejlmeddelse -- '
                           u'har du angivet korrekt kodeord?')
                config.log(u'Check konfigurationsfilen, angiv evt. nyt '
                           u'kodeord med --password eller --config ELLER '
                           u'prøv igen senere...', -2)
                sys.exit(1)

            assert(config.options.logintype != 'alm')  # This must be uni login
            for form in br.forms():
                if form.attrs.get('id') == 'pwd':
                    br.form = form
                    break
            else:
                config.log(u'Kunne ikke finde logind formular på %s' % url, -1)
                config.log(u'Måske er Javascript logind beskyttelse '
                           u'slået til? Prøv igen senere eller se '
                           u'https://svalgaard.github.io/fskintra/'
                           u'troubleshooting', -1)
                sys.exit(1)
            br['user'] = config.options.username
            br['pass'] = config.options.password
            resp = br.submit()
            continue

        if urlparse.urlparse(resp.geturl()).path == '/Account/IdpLogin':
            if 'ikke adgang' in data:
                config.log(u'Log ind giver en fejlmeddelse -- '
                           u'har du angivet korrekt kodeord?')
                config.log(u'Check konfigurationsfilen, angiv evt. nyt '
                           u'kodeord med --password eller --config ELLER '
                           u'prøv igen senere...', -2)
                sys.exit(1)

            # This is the main login page
            if config.options.logintype != 'alm':
                # UNI-login
                links = list(br.links(url_regex=re.compile(
                    '.*RedirectToUniLogin.*')))
                if not links:
                    config.log(u'Kan IKKE finde LOG PÅ MED UNILOGIN '
                               u'linket på siden?', -1)
                    sys.exit(1)
                config.log(u'Går videre til uni-login', 3)
                resp = br.follow_link(links[0])
                continue
            else:
                config.log(u'Bruger alm. login med brugernavn %r' %
                           config.options.username, 3)
                # "Ordinary login"
                try:
                    br['UserName'] = config.options.username
                    br['Password'] = config.options.password
                except mechanize.ControlNotFoundError:
                    config.log(u'Kan IKKE finde ALM LOGIN på siden.', -1)
                    config.log(u'Skal du måske bruge unilogin i stedet?', -1)
                    sys.exit(1)

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
    '''For a given URL, return the filename used for caching the result'''
    assert(type(url) == str)
    if postData:
        url += postData
    up = urlparse.urlparse(url)
    p = urllib.url2pathname(up.path)
    p = p.decode('utf-8', 'replace').replace(u'\ufffd', '_')
    parts = [config.options.cachedir,
             up.scheme,
             up.netloc,
             p[1:] + '.cache']
    if up.query:
        qq = ''
        az = re.compile(r'[^0-9a-zA-Z]')
        for (k, vs) in sorted(cgi.parse_qs(up.query).items()):
            xs = [az.sub(lambda x: hex(ord(x.group(0))), x) for x in [k] + vs]
            qq += '_' + '-'.join(xs)
        if len(qq) > 32:
            # Some queries are too long - this may fail when writing to disk
            qq = '_' + hashlib.md5(qq).hexdigest()
        parts[-1] += qq

    cfn = os.path.join(*parts)
    cfn = cfn.replace('\\', '/')
    if type(cfn) == unicode and not os.path.supports_unicode_filenames:
        cfn = cfn.encode('utf-8')
    return cfn


def skoleGetURL(url, asSoup=False, noCache=False, postData=None,
                addTimeSuffix=False):
    '''Returns data from url as raw string or as a beautiful soup'''

    # Sometimes the URL is actually an empty string
    if not url:
        data = ''
        if asSoup:
            data = sbs4.beautify(data)
            data.cachedate = datetime.date.today()
            return data
        else:
            return data

    if type(url) == unicode:
        url, uurl = url.encode('utf-8'), url
    else:
        uurl = url.decode('utf-8')
    if url.startswith('/'):
        url = absurl(url)

    if type(postData) == dict:
        pd = {}
        for (k, v) in postData.items():
            pd[unienc(k)] = unienc(v)
        postData = urllib.urlencode(pd)
    else:
        postData = unienc(postData)

    lfn = url2cacheFileName(url, postData)

    if type(noCache) in [int, float] and os.path.isfile(lfn):
        # noCache is a "max-age" in days of the file
        age = (time.time() - os.path.getmtime(lfn))/(24. * 3600)
        if age > noCache:
            config.log('skoleGetURL: Bruger ikke gammel cache for %s'
                       % uurl, 2)
            noCache = True
        else:
            noCache = False

    if os.path.isfile(lfn) and not noCache and not config.options.skipcache:
        config.log(u'skoleGetURL: Henter fra cache %s' % uurl, 2)
        config.log(u'skoleGetURL: %r' % lfn, 2)
        data = open(lfn, 'rb').read()
    else:
        if addTimeSuffix:
            if '?' in url:
                url += '&_=' + str(int(time.time()*1000))
            else:
                url += '?_=' + str(int(time.time()*1000))
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
        data = sbs4.beautify(data)
        data.url = url
        data.cachedate = datetime.date.fromtimestamp(os.path.getmtime(lfn))
        data.cacheage = (time.time() - os.path.getmtime(lfn))/(24 * 3600.)
        return data
    else:
        return data
