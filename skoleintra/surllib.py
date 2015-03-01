#
# -*- encoding: utf-8 -*-
#
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import hex

import http.cookiejar
import urllib.request, urllib.parse, urllib.error
from . import config
import mechanize
import BeautifulSoup
import urllib.parse
import cgi
import os
import sys
import re
import datetime
import hashlib


def beautify(data):
    return BeautifulSoup.BeautifulSoup(
        data,
        convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)


_browser = None


def getBrowser():
    global _browser
    if _browser is None:
        # Start browser
        _browser = mechanize.Browser()

        # Cookie Jar
        cj = http.cookiejar.LWPCookieJar()
        _browser.set_cookiejar(cj)

        # Browser options
        _browser.set_handle_equiv(True)
        # _browser.set_handle_gzip(True)
        _browser.set_handle_redirect(True)
        _browser.set_handle_referer(True)
        _browser.set_handle_robots(False)

        # Encoding
        #_browser._factory.encoding = ENC
        #_browser._factory._forms_factory.encoding = ENC
        #_browser._factory._links_factory._encoding = ENC

        # Follows refresh 0 but does not hang on refresh > 0
        _browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),
                                    max_time=1)

        # Want debugging messages?
        #_browser.set_debug_http(True)
        #_browser.set_debug_redirects(True)
        #_browser.set_debug_responses(True)

        # User-Agent
        _browser.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; '
             'rv:5.0.1) Gecko/20100101 Firefox/5.0.1'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;'
             'q=0.9,*/*;q=0.8')]
    return _browser

_skole_login_done = False


def skoleLogin():
    global br, resp
    'Login to the SkoleIntra website'
    global _skole_login_done
    if _skole_login_done:
        return
    br = getBrowser()
    config.log(u'Login', 2)

    URL_LOGIN = u'https://%s/Infoweb/Fi2/Login.asp' % config.HOSTNAME
    config.log(u'Login på skoleintra')
    config.log(u'skoleLogin: URL %s' % URL_LOGIN, 2)
    br.open(URL_LOGIN)
    config.log(u'skoleLogin: Brugernavn %s' % config.USERNAME, 2)
    br.select_form(name='FrontPage_Form1')
    br.form.set_all_readonly(False)
    cNames = [c.name for c in br.form.controls]
    br['fBrugernavn'] = config.USERNAME

    # send password
    if config.PASSWORD.startswith('pswd:'):
        pswdReal = config.b64dec(config.PASSWORD)
        pswdMD5 = hashlib.md5(pswdReal).hexdigest()
    else:
        pswdReal = None  # not possible to "decrypt" an md5 password
        pswdMD5 = config.PASSWORD
    if 'MD5kode' in cNames:
        # send md5 encoded password
        br['MD5kode'] = pswdMD5
    elif 'fAdgangskode' in cNames:
        # send real password
        if pswdReal is None:
            config.log(u'Din skoleintra installation er skiftet til at sende kodeord via https i stedet for md5 over http', -2)
            config.log(u'I den forbindelse bliver du nødt til at angive dit kodeord', -2)
            config.log(u'Anvend augumentet --password KODEORD for at lægge kodeordet ind igen', -2)
            sys.exit(256)
        br['fAdgangskode'] = pswdReal
    else:
        # something is wrong
        config.log(u'Kan ikke finde kodeordsfeltet på loginskærmen? Du får nok en loginfejl om lidt', -2)
    resp = br.submit()
    if u'Fejlmeddelelse' in resp.geturl():
        config.log(u'Login giver en fejlmeddelse -- har du angivet korrekt '
                   u'kodeord? Check konfigurationsfilen, angiv evt. nyt '
                   u'kodeord med --password eller --config ELLER '
                   u'prøv igen senere...', -2)
        sys.exit(256)
    # otherwise we ignore the response and assume that things are ok

    _skole_login_done = True


def url2cacheFileName(url):
    assert(type(url) == str)
    up = urllib.parse.urlparse(url)
    parts = [config.CACHE_DN,
             up.scheme,
             up.netloc,
             urllib.request.url2pathname(up.path)[1:]]
    if up.query:
        az = re.compile(r'[^0-9a-zA-Z]')
        for (k, vs) in sorted(cgi.parse_qs(up.query).items()):
            xs = [az.sub(lambda x: hex(ord(x.group(0))), x) for x in [k] + vs]
            parts[-1] += '_' + '-'.join(xs)
    return os.path.join(*parts)


def skoleGetURL(url, asSoup=False, noCache=False):
    '''Returns data from url as raw string or as a beautiful soup'''
    if type(url) == str:
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

    lfn = url2cacheFileName(url)

    if os.path.isfile(lfn) and not noCache and not config.SKIP_CACHE:
        config.log('skoleGetURL: Henter fra cache %s' % uurl, 2)
        data = open(lfn, 'rb').read()
    else:
        qurl = urllib.parse.quote(url, safe=':/?=&%')
        config.log(u'skoleGetURL: Trying to fetch %s' % qurl, 2)
        skoleLogin()
        br = getBrowser()
        resp = br.open(qurl)
        data = resp.read()
        # write to cache
        ldn = os.path.dirname(lfn)
        if not os.path.isdir(ldn):
            os.makedirs(ldn)
        open(lfn, 'wb').write(data)

    if asSoup:
        data = beautify(data)
        data.cachedate = datetime.date.fromtimestamp(os.path.getmtime(lfn))
        return data
    else:
        return data
