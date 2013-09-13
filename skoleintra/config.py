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
import optparse
import time

ROOT = os.path.expanduser('~/.skoleintra/')
DEFAULT_FN = os.path.join(os.path.dirname(__file__), 'default.inf')
CONFIG_FN = '~/.skoleintra/skoleintra.txt'
# Name of current child
CHILDNAME = '' 

#
# Parse command line options
#
parser = optparse.OptionParser(usage = u'''%prog [options]

Se flg. side for flere detaljer:
   https://github.com/svalgaard/fskintra/''')
parser.add_option('--config-file', dest='configfilename', default=None,
                  help=u'Brug konfigurationsfilen FILNAVN - standard: %s'%CONFIG_FN,
                  metavar='FILNAVN')
parser.add_option('--config', dest='doconfig', default=False, action='store_true',
                  help=u'Opsæt skoleintra')

parser.add_option('-v', '--verbose', action='append_const', const=1, dest='verbosity', 
                  help=u'Skriv flere log-linjer', default=[1])
parser.add_option('-q',  '--quiet', action='append_const', const=-1, dest='verbosity', 
                  help=u'Skriv færre log-linjer')

(options, args) = parser.parse_args()

if args:
    parser.error(u'Ukendte argumenter: %s' % ' '.join(args))

options.verbosity = max(sum(options.verbosity),0)

CONFIG_FN = os.path.expanduser(CONFIG_FN)
if options.configfilename:
    TMP = os.path.expanduser(options.configfilename)
    if not os.path.samefile(CONFIG_FN, TMP):
        CONFIG_FN = TMP
if not os.path.isfile(CONFIG_FN) and not options.doconfig:
    parser.error(u'''Kan ikke finde konfigurationsfilen '%s'
Kør først programmet med --config for at sætte det op'''  % CONFIG_FN)

#
# setup UTF-8 on stdout
#
def ensureDanish():
    '''Ensure that we can do Danish letters on stderr, stdout by wrapping
    them using codecs.getwriter if necessary'''

    enc = locale.getpreferredencoding()
    test = u'\xe6\xf8\xe5\xc6\xd8\xc5\xe1'.encode(enc, 'replace')
    if '?' in test:
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
ensureDanish()

if options.doconfig:
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

    # if not using standard CONFIG_FN, setup prefix for cache and msg
    if options.configfilename:
      opts.append(('cacheprefix', ''))
      details['cacheprefix'] = hex(int(time.time()))[2:] + '-'
    
    config = u'[default]\n'
    for opt,_ in opts:
        config += u'%s=%s\n' % (opt, details[opt])
    
    if not os.path.isdir(ROOT):
        os.makedirs(ROOT)
    open(CONFIG_FN,'w').write(config.encode('utf-8'))
    
    print
    print u'Din nye opsætning er klar -- kør nu programmet uden --config'
    sys.exit(1)

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
    if options.configfilename:
      CACHEPREFIX = cfg.get('default', 'cacheprefix')
    else:
      CACHEPREFIX = ''
except ConfigParser.NoOptionError, e:
    parser.error(u'''Konfigurationsfilen '%s' mangler en indstilling for %s
Kør først programmet med --config for at sætte det op'''  % (CONFIG_FN, e.option))

# setup cache and msg directories, and ensure that they exist
CACHE_DN = os.path.join(ROOT, CACHEPREFIX+'cache')
MSG_DN = os.path.join(ROOT, CACHEPREFIX+'msg')
for dn in (CACHE_DN, MSG_DN):
    if not os.path.isdir(dn):
        os.makedirs(dn)
    
# logging levels:
#  0 some important stuff (requires -q)
#  1 requires one         (default value)
#  2 tiny log messages    (requires -v)
VERBOSE = options.verbosity
def log(s, level = 1):
    if type(level) != int:
        raise Exception(u'level must be an int, not %s' % repr(level))
    if level <= VERBOSE:
        sys.stderr.write(u'%s\n'%s)
        sys.stderr.flush()

