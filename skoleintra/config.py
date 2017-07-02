# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
import codecs
import locale
import getpass
import optparse
import time
import re

ROOT = os.path.expanduser('~/.skoleintra/')
DEFAULT_FN = os.path.join(os.path.dirname(__file__), 'default.inf')
CONFIG_FN = '~/.skoleintra/skoleintra.txt'
# Name of current child
CHILDNAME = ''

#
# Parse command line options
#
parser = optparse.OptionParser(usage=u'''%prog [options]

Se flg. side for flere detaljer:
   https://github.com/svalgaard/fskintra/''')

parser.add_option(
    '--config-file', dest='configfilename', default=None,
    help=u'Brug konfigurationsfilen FILNAVN - standard: %s' % CONFIG_FN,
    metavar='FILNAVN')
parser.add_option(
    '--password', '-p', dest='password', default=None,
    help=u'Opdatér kodeord. Dette skrives om muligt til konfigurationsfilen',
    metavar='PASSWORD')
parser.add_option(
    '--config', dest='doconfig', default=False, action='store_true',
    help=u'Opsæt skoleintra')
parser.add_option(
    '--skip-cache', dest='skipcache', default=False, action='store_true',
    help=u'Do not use previously cached files')
parser.add_option(
    '-v', '--verbose', action='append_const', const=1, dest='verbosity',
    help=u'Skriv flere log-linjer', default=[1])
parser.add_option(
    '-q',  '--quiet', action='append_const', const=-1, dest='verbosity',
    help=u'Skriv færre log-linjer')

(options, args) = parser.parse_args()

if args:
    parser.error(u'Ukendte argumenter: %s' % ' '.join(args))

options.verbosity = max(sum(options.verbosity), 0)

CONFIG_FN = os.path.expanduser(CONFIG_FN)
if options.configfilename:
    TMP = os.path.expanduser(options.configfilename)
    if not os.path.samefile(CONFIG_FN, TMP):
        CONFIG_FN = TMP
if not os.path.isfile(CONFIG_FN) and not options.doconfig:
    parser.error(u'''Kan ikke finde konfigurationsfilen
%s
Kør først programmet med --config for at sætte det op.''' % CONFIG_FN)

if options.doconfig and options.password is not None:
    parser.error(u'''--config og --password kan ikke bruges samtidigt''')

SKIP_CACHE = options.skipcache


def ensureDanish():
    '''Ensure that we can do Danish letters on stderr, stdout by wrapping
    them using codecs.getwriter if necessary'''

    enc = locale.getpreferredencoding() or 'ascii'
    test = u'\xe6\xf8\xe5\xc6\xd8\xc5\xe1'.encode(enc, 'replace')
    if '?' in test or sys.version_info < (2, 6):
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
ensureDanish()


# logging levels:
#  0 some important stuff (requires -q)
#  1 requires one         (default value)
#  2 tiny log messages    (requires -v)
VERBOSE = options.verbosity


def log(s, level=1):
    if type(level) != int:
        raise Exception(u'level must be an int, not %s' % repr(level))
    if level <= VERBOSE:
        sys.stderr.write('%s\n' % s)
        sys.stderr.flush()


def b64enc(pswd):
    return 'pswd:' + pswd.encode('base64')


def b64dec(pswd):
    assert(pswd.startswith('pswd:'))
    return pswd[5:].decode('base64')


if options.doconfig:
    if os.path.isfile(CONFIG_FN):
        print u'Din opsætning bliver nulstillet,',
        print u'når du har besvareret nedenstående spørgsmål'
    print u'Din nye opsætning gemmes her:', CONFIG_FN

    details = {}
    opts = [
        ('username',
         u'Brugernavn, fx. petjen:'),
        ('password',
         u'Kodeord fx kaTTx24:'),
        ('hostname',
         u'Skoleintra domæne fx www.xskolen.yby.dk:'),
        ('email',
         u'Modtageremailadresse (evt. flere adskilt med komma):'),
        ('senderemail',
         u'Afsenderemailadresse (evt. samme adresse(r) som ovenover):'),
        ('smtpserver',
         u'SMTP servernavn (evt. tom hvis localhost skal bruges) '
         u'fx smtp.gmail.com eller asmtp.mail.dk:'),
        ('smtpport',
         u'SMTP serverport fx 25 (localhost), 587 (gmail, tdc):'),
        ('smtplogin',
         u'SMTP Login (tom hvis login ikke påkrævet):'),
        ('smtppassword',
         u'SMTP password (tom hvis login ikke påkrævet):')]
    for (var, question) in opts:
        while True:
            print
            print question
            if var.endswith('password'):
                a = getpass.getpass('').strip().decode(sys.stdin.encoding)
            else:
                a = raw_input().strip().decode(sys.stdin.encoding)
            if a or var.startswith('smtp'):
                break
            print u'Angiv venligst en værdi'
        details[var] = a

    # "encrypt" the password
    details['password'] = b64enc(details['password'])
    # "encrypt" smtp password
    if details['smtppassword']:
        details['smtppassword'] = b64enc(details['smtppassword'])

    # if not using standard CONFIG_FN, setup prefix for cache and msg
    if options.configfilename:
        opts.append(('cacheprefix', ''))
        details['cacheprefix'] = hex(int(time.time()))[2:] + '-'

    config = u'[default]\n'
    for opt, _ in opts:
        config += u'%s=%s\n' % (opt, details[opt])

    if not os.path.isdir(ROOT):
        os.makedirs(ROOT)
    open(CONFIG_FN, 'w').write(config.encode('utf-8'))

    print
    print u'Din nye opsætning er klar -- kør nu programmet uden --config'
    sys.exit(1)


# read configuration
cfg = ConfigParser.ConfigParser()
cfg.read(DEFAULT_FN)
cfg.read(CONFIG_FN)


# Maybe write new password to CONFIG_FN
if options.password is not None:
    pswd = b64enc(options.password)
    if cfg.get('default', 'password') == pswd:
        log(u'Nyt kodeord angivet med --password er ens med nuværende'
            u' kodeord i %s' % CONFIG_FN, -2)
    else:
        cfg.set('default', 'password', pswd)

        data = open(CONFIG_FN, 'r').read()
        r = re.compile(ur'(?m)^password\s*=.*$')
        if not r.findall(data):
            log(u'Kan ikke finde linjen med password', -2)
            log(u'Nyt kodeord bliver ikke skrevet i '
                u'konfigurationsfilesn %s' % CONFIG_FN, -2)
        else:
            data = r.sub('password=%s' % pswd, data)
            try:
                open(CONFIG_FN, 'w').write(data)
                log(u'Nyt kodeord er skrevet til'
                    u'konfigurationsfilen %s' % CONFIG_FN, -2)
            except:
                log(u'Kan ikke skrive til '
                    u'konfigurationsfilen %s' % CONFIG_FN, -2)
                log(u'Nyt kodeord bliver ikke skrevet', -2)


def softGet(cp, section, option):
    if cp.has_option(section, option):
        return cp.get(section, option)
    else:
        return ''

try:
    USERNAME = cfg.get('default', 'username')
    PASSWORD = cfg.get('default', 'password')
    HOSTNAME = cfg.get('default', 'hostname')
    SENDER = cfg.get('default', 'senderemail')
    EMAIL = cfg.get('default', 'email')
    if options.configfilename:
        CACHEPREFIX = cfg.get('default', 'cacheprefix')
    else:
        CACHEPREFIX = ''
    SMTPHOST = softGet(cfg, 'default', 'smtpserver')
    SMTPPORT = softGet(cfg, 'default', 'smtpport')
    SMTPLOGIN = softGet(cfg, 'default', 'smtplogin')
    SMTPPASS = softGet(cfg, 'default', 'smtppassword')
except ConfigParser.NoOptionError, e:
    parser.error(u'''Konfigurationsfilen '%s' mangler en indstilling for %s.
Kør først programmet med --config for at sætte det op.
Eller ret direkte i '%s'.''' % (CONFIG_FN, e.option, CONFIG_FN))

# setup cache and msg directories, and ensure that they exist
CACHE_DN = os.path.join(ROOT, CACHEPREFIX + 'cache')
MSG_DN = os.path.join(ROOT, CACHEPREFIX + 'msg')
for dn in (CACHE_DN, MSG_DN):
    if not os.path.isdir(dn):
        os.makedirs(dn)

#
# Ensure that SMTP options are sane
#
if SMTPHOST:
    try:
        SMTPPORT = int(SMTPPORT)
    except ValueError:
        parser.error(u'''
Konfigurationsfilen '%s' mangler en korrekt indstilling for smtpport.
Nuværende indstilling er %s - en korrekt værdi kunne være fx. 25 eller 587.
Ret evt direkte i konfigurationsfilen ved at tilføje en linje svarende til
smtpport=25.'''.strip() % (CONFIG_FN, repr(SMTPPORT)))

        log(u'Ugyldigt SMTP portnummer angivet %s - bruger 587' %
            repr(SMTPPORT))
        SMTPPORT = 587

    if not SMTPLOGIN:
        SMTPPASS = ''

    if SMTPPASS:
        if SMTPPASS.startswith('pswd:'):
            SMTPPASS = b64dec(SMTPPASS)
else:
    SMTPPORT = ''
    SMTPLOGIN = ''
    SMTPPASS = ''
