#
# -*- encoding: utf-8 -*-
#

import os
import sys
import ConfigParser
import hashlib
import codecs
import locale
import getpass

ROOT = os.path.expanduser('~/.skoleintra/')
CACHE_DN = os.path.join(ROOT, 'cache')
MSG_DN = os.path.join(ROOT, 'msg')
CONFIG_FN = os.path.join(ROOT, 'skoleintra.txt')
DEFAULT_FN = os.path.join(os.path.dirname(__file__), 'default.inf')

# Name of current child
CHILDNAME = '' 

# setup UTF-8 on stdout
def getNiceEncoding():
    enc = locale.getpreferredencoding()
    if not enc: enc = 'utf-8'

    # try to write æøå to this and see if we fail
    try:
        x = u'æøåÆØÅá'.decode(enc)
    except UnicodeEncodeError, u:
        # ignore the locale since this does not allow us to write what we want
        enc = 'UTF-8'
    return enc
def niceStream(fd):
    return codecs.getwriter(getNiceEncoding())(fd)
def ensureDanish():
    '''Ensure that we can do Danish letters on stderr, stdout by wrapping them in a codecs thing'''
    sys.stderr = niceStream(sys.stderr)
    sys.stdout = niceStream(sys.stdout)
ensureDanish()


def pleaseSetup(msg = ''):
    if msg: print msg
    print u'Kør venligst programmet med --config for at sætte din SkoleIntra konto op'
    sys.exit(1)

if not os.path.isfile(CONFIG_FN):
    if not '--config' in sys.argv:
        pleaseSetup('%s eksisterer ikke.' % CONFIG_FN)

if '--config' in sys.argv:
    if os.path.isfile(CONFIG_FN):
        print u'Din opsætning bliver nulstillet, når du har besvareret nedenstående spørgsmål'
    print u'Din nye opsætning gemmes her:', CONFIG_FN

    details = {}
    opts = [('username',    u'Brugernavn, fx. petjen:'),
            ('password',    u'Kodeord fx kaTTx24:'),
            ('hostname',    u'Skoleintra domæne fx www.xskolen.yby.dk:'),
            ('email',       u'Modtageremailadresse (evt. flere adskilt med komma):'),
            ('senderemail', u'Afsenderemailadresse (evt. samme adresse(r) som ovenover):')]
    for (var,question) in opts:
        while True:
            q = u'\n%s\n' % question
            if var == 'password':
                a = getpass.getpass(q).strip().decode(sys.stdin.encoding)
            else:
                a = raw_input(q).strip().decode(sys.stdin.encoding)
            if a: break
            print u'Angiv venligst en værdi'
        details[var] = a
    
    #md5 "encrypt" the password
    details['password'] = hashlib.md5(details['password']).hexdigest()
    
    config = u'[default]\n'
    for opt,_ in opts:
        config += u'%s=%s\n' % (opt, details[opt])
    
    if not os.path.isdir(ROOT):
        os.makedirs(ROOT)
    open(CONFIG_FN,'w').write(config.encode('utf-8'))
    
    print
    print u'Din nye opsætning er klar -- kør nu programmet uden --config'
    sys.exit(1)

# ensure that we have all directories setup
for dn in (CACHE_DN, MSG_DN):
    if not os.path.isdir(dn):
        os.makedirs(dn)
    
# read configuration
cfg = ConfigParser.ConfigParser()
cfg.read(DEFAULT_FN)
cfg.read(CONFIG_FN)

try:
    USERNAME = cfg.get('default', 'username')
    PASS_MD5 = cfg.get('default', 'password')
    HOSTNAME = cfg.get('default', 'hostname')
    SENDER   = cfg.get('default', 'senderemail')
    EMAIL    = cfg.get('default', 'email')
except ConfigParser.NoOptionError, e:
    pleaseSetup(u'Mangler indstilling for: %s' % e.option)

# logging levels:
#  0 some important stuff (requires -q)
#  1 requires one         (default value)
#  2 tiny log messages    (requires -v)
VERBOSE = 1
for (k,v) in [('-v',1),('-q',-1)]:
    while k in sys.argv:
        sys.argv.remove(k)
        VERBOSE += v
def log(s, level = 1):
    if type(level) != int:
        raise Exception(u'level must be an int, not %s' % repr(level))
    if level <= VERBOSE:
        sys.stderr.write(u'%s\n'%s)
        sys.stderr.flush()

