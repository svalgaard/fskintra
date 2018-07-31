# -*- coding: utf-8 -*-

import codecs
import ConfigParser
import getpass
import locale
import optparse
import os
import re
import sys
import time

ROOT = os.path.expanduser('~/.skoleintra/')
CONFIG_FN = os.path.join(ROOT, 'skoleintra.txt')
LOGIN_TYPES = ['alm', 'uni']


def ensureDanish():
    '''Ensure that we can do Danish letters on stderr, stdout by wrapping
    them using codecs.getwriter if necessary'''

    enc = locale.getpreferredencoding() or 'ascii'
    test = u'\xe6\xf8\xe5\xc6\xd8\xc5\xe1'.encode(enc, 'replace')
    if '?' in test or sys.version_info < (2, 6):
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)


ensureDanish()

# Also ensure that we can parse Danish time stamps
locale.setlocale(locale.LC_TIME, "da_DK")


#
# Parse command line options
#
parser = optparse.OptionParser(usage=u'''%prog [options]

Se flg. side for flere detaljer:
   https://github.com/svalgaard/fskintra/''', add_help_option=False)

parser.add_option(
    '--help', '-h', action='help',
    help=u"Vis denne besked og afslut")
parser.add_option(
    '--config-file', dest='configfilename', default=None,
    help=u'Brug konfigurationsfilen FILENAME - standard: %s' % CONFIG_FN,
    metavar='FILENAME')
parser.add_option(
    '--profile', '-P', dest='profile', default=None,
    help=u'Brug afsnittet [PROFILE] dernæst [default] fra konfigurationsfilen',
    metavar='PROFILE')
parser.add_option(
    '--password', '-p', dest='password', default=None,
    help=u'Opdatér kodeord. Dette skrives om muligt til konfigurationsfilen. '
         u'Alternativt udskrives det "krypterede" kodeord, så du selv kan '
         u'rette filen',
    metavar='PASSWORD')
parser.add_option(
    '--config', dest='doconfig', default=False, action='store_true',
    help=u'Opsæt skoleintra')
parser.add_option(
    '--skip-cache', dest='skipcache', default=False, action='store_true',
    help=u'Brug ikke tidligere hentet indhold/cache')
parser.add_option(
    '--catchup', '-c', dest='catchup', default=False, action='store_true',
    help=u'Hent & marker alt indhold som set uden at sende nogen e-mails')
parser.add_option(
    '--quick', '-Q', dest='full_update', default=True, action='store_false',
    help=u'Kør ikke fuld check af alle sider medmindre der forventes nyt')
parser.add_option(
    '-v', '--verbose', action='append_const', const=1, dest='verbosity',
    help=u'Skriv flere log-linjer', default=[1])
parser.add_option(
    '-q',  '--quiet', action='append_const', const=-1, dest='verbosity',
    help=u'Skriv færre log-linjer')

(options, args) = parser.parse_args()

if args:
    parser.error(u'Ukendte argumenter: %s' % ' '.join(args))

if options.configfilename:
    CONFIG_FN = os.path.expanduser(options.configfilename)
if not os.path.isfile(CONFIG_FN) and not options.doconfig:
    parser.error(u'''Kan ikke finde konfigurationsfilen
%s
Kør først programmet med --config for at sætte det op.''' % CONFIG_FN)

if options.doconfig:
    if options.password is not None:
        parser.error(u'--config og --password kan ikke bruges samtidigt')
    if options.profile:
        parser.error(u'--config og --profile kan ikke bruges samtidigt')

PROFILE = options.profile or ''
CATCHUP = options.catchup
FULL_UPDATE = options.full_update
SKIP_CACHE = options.skipcache


# logging levels:
#  0 only important stuff (always printed)
#  1 requires one         (default value, requires -q to ignore)
#  2 tiny log messages    (requires -v)
#  3 micro log messages   (requires -vv)
VERBOSE = max(sum(options.verbosity), 0)


def log(s, level=1):
    if type(level) != int:
        raise Exception(u'level SKAL være et tal, ikke %r' % level)
    if level <= VERBOSE:
        sys.stderr.write(u'%s\n' % s)
        sys.stderr.flush()


def clog(cname, s, level=1):
    return log(u'[%s] %s' % (cname, s), level)


def b64enc(pswd):
    return 'pswd:' + pswd.encode('base64')


def b64dec(pswd):
    if pswd.startswith('pswd:'):
        return pswd[5:].decode('base64')
    return pswd


if options.doconfig:
    if os.path.isfile(CONFIG_FN):
        print u'Din opsætning bliver nulstillet,',
        print u'når du har besvareret nedenstående spørgsmål'
    print u'Din nye opsætning gemmes her:', CONFIG_FN

    details = {}
    opts = [
        ('logintype',
         u"Logintype - enten 'alm' (almindeligt) eller 'uni' (UNI-Login)"),
        ('username',
         u'Brugernavn, fx. petjen:'),
        ('password',
         u'Kodeord fx kaTTx24:'),
        ('hostname',
         u'Skoleintra domæne fx aaskolen.m.skoleintra.dk:'),
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
            if var == 'logintype' and a not in LOGIN_TYPES:
                print u"Angiv venligst en af flg.: %s" % ', '.join(LOGIN_TYPES)
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
class MyConf(ConfigParser.ConfigParser):
    def getOpt(self, option, default=None):
        global PROFILE
        if PROFILE and self.has_option(PROFILE, option):
            return self.get(PROFILE, option)

        if self.has_option('default', option):
            return self.get('default', option)

        if default is not None:
            return default

        raise ConfigParser.NoOptionError(option, 'default')


cfg = MyConf()
cfg.read(CONFIG_FN)

if PROFILE and not cfg.has_section(PROFILE):
    log((u'Konfigurationsfilen %s har ikke afsnittet [%s] '
         u'angivet med --profile') %
        (CONFIG_FN, repr(PROFILE)[1:-1]))
    sys.exit(1)

# Maybe write new password to CONFIG_FN
if options.password is not None:
    pswd = b64enc(options.password)
    if cfg.getOpt('password', '') == pswd:
        log(u'Nyt kodeord angivet med --password er ens med nuværende'
            u' kodeord i %s' % CONFIG_FN, -2)
    else:
        cfg.set(PROFILE or 'default', 'password', pswd)

        data = open(CONFIG_FN, 'r').read()
        r = re.compile(ur'(?m)^password\s*=.*$')
        if PROFILE:
            log(u'Du har brugt --profile sammen med --password', -2)
            log(u'I dette tilfælde er du nødt til selv at opdatere '
                u'konfigurationsfilen %s med' % CONFIG_FN, -2)
            log(u'password=%s' % pswd)
        elif not r.findall(data):
            log(u'Kan ikke finde linjen med password', -2)
            log(u'I dette tilfælde er du nødt til selv at opdatere '
                u'konfigurationsfilen %s med' % CONFIG_FN, -2)
            log(u'password=%s' % pswd)
        else:
            data = r.sub('password=%s' % pswd, data)
            try:
                open(CONFIG_FN, 'w').write(data)
                log(u'Nyt kodeord er skrevet til'
                    u'konfigurationsfilen %s' % CONFIG_FN, -2)
            except IOError:
                log(u'Kan ikke skrive til '
                    u'konfigurationsfilen %s' % CONFIG_FN, -2)
                log(u'Nyt kodeord bliver ikke skrevet', -2)
    sys.exit(1)


try:
    LOGINTYPE = cfg.getOpt('logintype', 'alm')
    USERNAME = cfg.getOpt('username')
    PASSWORD = b64dec(cfg.getOpt('password'))
    HOSTNAME = cfg.getOpt('hostname')
    SENDER = cfg.getOpt('senderemail')
    EMAIL = cfg.getOpt('email')
    if options.configfilename:
        CACHEPREFIX = cfg.getOpt('cacheprefix')
    else:
        CACHEPREFIX = cfg.getOpt('cacheprefix', '')
    SMTPHOST = cfg.getOpt('smtpserver', '')
    SMTPPORT = cfg.getOpt('smtpport', '')
    SMTPLOGIN = cfg.getOpt('smtplogin', '')
    SMTPPASS = cfg.getOpt('smtppassword', '')
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
        SMTPPASS = b64dec(SMTPPASS)
else:
    SMTPPORT = ''
    SMTPLOGIN = ''
    SMTPPASS = ''
