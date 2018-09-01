# -*- coding: utf-8 -*-

import argparse
import codecs
import ConfigParser
import getpass
import inspect
import locale
import os
import re
import sys

# Default location of configuration files
ROOT = os.path.expanduser('~/.skoleintra/')
CONFIG_FN = os.path.join(ROOT, 'skoleintra.txt')

# Sections / different types of sections/pages (Section)
PAGE_SECTIONS = []

# Default value
options = argparse.Namespace(verbosity=1)

# Options that must/can be set in the CONFIG file
CONFIG_OPTIONS = (
    (u'logintype',
     re.compile(ur'^(alm|uni)$'),
     u"Logintype - enten 'alm' (almindeligt) eller 'uni' (UNI-Login)"),
    (u'username',
     re.compile(ur'^[-.a-zA-Z0-9]+$'),
     u'Brugernavn, fx. petjen'),
    (u'password',
     re.compile(ur'^.+$'),
     u'Kodeord fx kaTTx24'),
    (u'hostname',
     re.compile(ur'^[-.a-zA-Z0-9]+$'),
     u'Skoleintra domæne fx aaskolen.m.skoleintra.dk'),
    (u'cacheprefix',
     re.compile(ur''),
     u'Præfix til cache+msg katalogerne (evt. \'-\' hvis du blot vil bruge '
     u'../cache hhv. ../msg)'),
    (u'email',
     re.compile(ur'^.+$'),
     u'Modtageremailadresse (evt. flere adskilt med komma)'),
    (u'senderemail',
     re.compile(ur'^.+$'),
     u'Afsenderemailadresse (evt. samme adresse som ovenover)'),
    (u'smtphostname',
     re.compile(ur'^[-.a-zA-Z0-9]+$'),
     u'SMTP servernavn (evt. localhost hvis du kører din egen server)'
     u' fx smtp.gmail.com eller asmtp.mail.dk'),
    (u'smtpport',
     re.compile(ur'^[0-9]+$'),
     u'SMTP serverport fx 25 (localhost), 587 (gmail, tdc)'),
    (u'smtpusername',
     re.compile(ur''),
     u'SMTP Login (evt. tom hvis login ikke påkrævet)'),
    (u'smtppassword',
     re.compile(ur''),
     u'SMTP password (evt. tom hvis login ikke påkrævet)'))


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


# logging levels:
#  0 only important stuff (always printed)
#  1 requires one         (default value, requires -q to ignore)
#  2 tiny log messages    (requires -v)
#  3 micro log messages   (requires -vv)
def log(s, level=1):
    if type(level) != int:
        raise Exception(u'level SKAL være et tal, ikke %r' % level)
    if level <= options.verbosity:
        sys.stderr.write(u'%s\n' % s)
        sys.stderr.flush()


def clog(cname, s, level=1):
    return log(u'[%s] %s' % (cname, s), level)


class ProfileConf(ConfigParser.ConfigParser):
    def __init__(self, profile):
        ConfigParser.ConfigParser.__init__(self)
        self.profile = profile
        # Add 'default' section
        self._sections['default'] = self._dict()

    def writeTo(self, filename):
        dn = os.path.dirname(filename)
        if dn and not os.path.isdir(dn):
            os.makedirs(dn)
        with open(filename, 'w') as fp:
            self.write(fp)

    def __getitem__(self, option):
        option = str(option)  # Ensure this is a 8-bit string
        for section in [self.profile, 'default']:
            try:
                value = self.get(section, option)
                if 'password' in option:
                    value = self.b64dec(value)
                return value.decode('utf-8')
            except ConfigParser.Error:
                continue
        return ''

    def __setitem__(self, option, value):
        option = str(option)  # Ensure this is a 8-bit string
        value = value.encode('utf-8') if type(value) == unicode else str(value)

        if 'password' in option:
            value = self.b64enc(value)
        if self.profile != 'default' and not self.has_section(self.profile):
            self.add_section(self.profile)

        self.set(self.profile, option, value)

    def b64enc(self, pswd):
        return ('pswd:' + pswd.encode('base64')).strip() if pswd else ''

    def b64dec(self, pswd):
        if pswd.startswith('pswd:'):
            return pswd[5:].decode('base64')
        return pswd


def configure(configfilename, profile):
    cfg = ProfileConf(profile)
    print u'Din nye opsætning gemmes her:', configfilename
    if os.path.isfile(configfilename):
        if cfg.read(configfilename):
            if cfg.sections() == [profile]:
                print u'Din tidligere opsætning bliver helt nulstillet'
            else:
                print u'Tidligere opsætning indlæst fra konfigurationsfilen'
                print u'Opsætning i afsnittet [%s] bliver nulstillet' % profile
        else:
            print u'Kunne IKKE læse tidligere indhold fra konfigurationsfilen'
            print u'Din opsætning bliver HELT nulstillet,'

    print u'Tryk CTRL-C for evt. at stoppe undervejs'

    for (key, check, question) in CONFIG_OPTIONS:
        if key == 'cacheprefix':
            cfg['cacheprefix'] = cfg['hostname'].split('.')[0]
            question += ', default: ' + cfg['cacheprefix']
        while True:
            print
            print question + u':'
            try:
                if key.endswith('password'):
                    a = getpass.getpass('')
                else:
                    a = raw_input()
                a = a.decode(sys.stdin.encoding).strip()
            except KeyboardInterrupt:
                print u'\nOpsætning afbrydes!'
                sys.exit(1)
            if check.match(a):
                if a or key != 'cacheprefix':
                    cfg[key] = a
                break
            else:
                if a:
                    print u'Angiv venligst en lovlig værdi'
                else:
                    print u'Angiv venligst en værdi'

    cfg.writeTo(configfilename)

    print
    print u'Din nye opsætning er klar -- kør nu programmet uden --config'
    sys.exit(0)


def parseArgs(argv):
    '''Parse command line options. Fails if one or more errors are found'''
    global parser

    parser = argparse.ArgumentParser(
        usage=u'''%(prog)s [options]

Hent nyt fra ForældreIntra og send det som e-mails.

Se flg. side for flere detaljer:
https://github.com/svalgaard/fskintra/
''', add_help=False)

    group = parser.add_argument_group(u'Vælg konfigurationsfil og profil')
    group.add_argument(
        '--config-file', metavar='FILENAME',
        dest='configfilename', default=CONFIG_FN,
        help=u'Brug konfigurationsfilen FILENAME - standard: %s' % CONFIG_FN)
    group.add_argument(
        '-p', '--profile', metavar='PROFILE',
        dest='profile', default='default',
        help=u'Brug afsnittet [PROFILE] dernæst [default] fra '
             u'konfigurationsfilen')

    group = parser.add_argument_group(u'Opsætning')
    group.add_argument(
        '--config',
        dest='doconfig', default=False, action='store_true',
        help=u'Opsæt fskintra')
    group.add_argument(
        '--password', dest='password', metavar='PASSWORD',
        default=None,
        help=u'Opdatér kodeord til ForældreIntra i konfigurationsfilen')
    group.add_argument(
        '--smtppassword', dest='smtppassword', metavar='PASSWORD',
        default=None,
        help=u'Opdatér kodeord til SMTP (smtppassword) i konfigurationsfilen')

    group = parser.add_argument_group(u'Hvad/hvor meget skal hentes')
    group.add_argument(
        '-s', '--section', metavar='SECTION',
        dest='sections', default=[],
        action='append',
        help=u'Kommasepareret liste af et eller flere afsnit/dele af '
             u'hjemmesiden der skal hentes nyt fra. '
             u"Brug '--section list' for at få en liste over mulige afsnit.")
    group.add_argument(
        '-Q', '--quick',
        dest='fullupdate', default=True,
        action='store_false',
        help=u'Kør ikke fuld check af alle sider medmindre der forventes nyt')
    group.add_argument(
        '-c', '--catch-up',
        dest='catchup', default=False,
        action='store_true',
        help=u'Hent & marker alt indhold som set uden at sende nogen e-mails')
    group.add_argument(
        '--skip-cache',
        dest='skipcache', default=False,
        action='store_true',
        help=u'Brug ikke tidligere hentet indhold/cache')

    group = parser.add_argument_group('Diverse')
    group.add_argument(
        '-h', '--help',
        action='help',
        help=u"Vis denne hjælpetekst og afslut")
    group.add_argument(
        '-v', '--verbose',
        dest='verbosity', default=[1],
        action='append_const', const=1,
        help=u'Skriv flere log-linjer')
    group.add_argument(
        '-q', '--quiet',
        dest='verbosity',  # See --verbose above
        action='append_const', const=-1,
        help=u'Skriv færre log-linjer')

    args, other = parser.parse_known_args(argv)

    # Extra checks that we have a valid set of options
    if other:
        parser.error(u'Ugyldige flag/argumenter: %r' % ' '.join(other))
    if not re.match('^[-_.a-z0-9]+$', args.profile):
        parser.error(u'PROFILE må kun indeholde a til z, 0-9, _, . og -')
    if args.doconfig and args.password:
        parser.error(u'--config og --password kan ikke bruges samtidigt')
    if args.doconfig and args.smtppassword:
        parser.error(u'--config og --smtppassword kan ikke bruges samtidigt')

    # Setup (default) values
    args.verbosity = max(sum(args.verbosity), 0)

    # Check that the --section SECTION setup is sane
    assert(PAGE_SECTIONS)  # at least one section must be defined earlier
    defsecs = set(s.section for s in PAGE_SECTIONS)

    if not args.sections:
        # Run everything by default
        args.sections = defsecs.copy()
    else:
        secs = filter(None, u','.join(args.sections).lower().split(u','))
        args.sections = defsecs.copy()

        if u'list' in secs:
            msg = u'''
Det er muligt at angive følgende mulige afsnit som argument til --section:

%s

Brug fx. --section frp,doc for kun at se efter nyt fra forsiden og beskeder.
Eller --section ,-pht,-doc for at se efter nyt på alle sider undtagen billeder
og dokumenter. Det ekstra komma er nødvendig for at -pht ikke bliver set som
om du har kaldt fskintra med argumenterne -p, -h og -t.
''' % u'\n'.join(u'  %-5s %s' % (s.section, s.desc) for s in PAGE_SECTIONS)
            sys.stderr.write(msg.lstrip())
            sys.exit(0)

        # check that all sections are valid
        if secs and not secs[0].startswith(u'-'):
            args.sections.clear()
        illegal = []
        for sec in secs:
            if sec in defsecs:
                args.sections.add(sec)
            elif sec.startswith('-') and sec[1:] in defsecs:
                args.sections.discard(sec[1:])
            else:
                illegal.append(sec)

        if illegal:
            illegal = u', '.join(repr(i) for i in illegal)
            parser.error((u'Ugyldig(e) navne på afsnit angivet: %s\nBrug '
                          u'--section LIST for at få en liste over lovlige '
                          u'lovlige nane') % illegal)

    if args.doconfig:
        configure(args.configfilename, args.profile)
        sys.exit(0)

    cfg = ProfileConf(args.profile)
    if os.path.isfile(args.configfilename):
        if cfg.read(args.configfilename):
            err = ''  # Everything ok
        else:
            err = u"Konfigurationsfilen %s kan ikke læses korrekt."
    else:
        err = u"Kan ikke finde konfigurationsfilen '%s'."
    if err:
        parser.error(
            err % args.configfilename +
            '\nKør evt fskintra med --config for at sætte det op.')

    if not cfg.has_section(args.profile):
        parser.error((u'Konfigurationsfilen %s har ikke afsnittet [%s] '
                      u'angivet med --profile') %
                     (args.configfilename, args.profile))

    # Do we actaully want to set a password/smtppassword
    if args.password is not None or args.smtppassword is not None:
        if args.password is not None:
            cfg['password'] = args.password
            print u'Kodeord opdateret'
        if args.smtppassword is not None:
            cfg['smtppassword'] = args.smtppassword
            print u'SMTP-kodeord opdateret'
        cfg.writeTo(args.configfilename)
        print u"Konfigurationsfilen '%s' opdateret" % args.configfilename
        sys.exit(0)

    # Check that the configuration in cfg is sane
    for (key, check, question) in CONFIG_OPTIONS:
        val = cfg[key]
        setattr(args, key, val)  # Copy the (possibly empty) value to args
        extraErr = u''
        if check.match(val):
            if key == 'hostname':
                args.hostname = str(args.hostname)
            if key == 'smtpport':
                args.smtpport = int(args.smtpport, 10)

            if key == 'smtpusername' and val and not cfg['smtppassword']:
                extraErr = (u'\nsmtpusername må ikke angives uden at '
                            u'smtppassword også er angivet.')
            elif key == 'smtppassword' and val and not cfg['smtpusername']:
                extraErr = u'\nsmtppassword kræves da smtpusername er angivet.'
            else:
                continue

        msg = u'''
Konfigurationsfilen mangler en lovlig indstilling for %s.%s

Konfig.fil     : %s
Profil         : %s
Indstilling    : %s
Forklaring     : %s
Nuværende værdi: %s

Ret direkte i konfigurationsfilen ved at tilføje en linje/rette linjen med
%s = NY_VÆRDI
Eller kør fskintra med --config'''.strip() + '\n'
        msg %= (key, extraErr, args.configfilename, args.profile,
                key, question, cfg[key] if cfg[key] else '[TOM]', key)
        if key.endswith('password'):
            msg += u'Eller kør fskintra med --%s\n' % key
        if key.endswith('smtpusername'):
            msg += u'Eller kør fskintra med --smtppassword\n'
        sys.stderr.write(msg)
        sys.exit(1)

    # Setup cache and msg directories, and ensure that they exist
    args.cacheprefix = args.cacheprefix.strip('-')
    if args.cacheprefix:
        args.cacheprefix += '-'
    args.cachedir = os.path.join(ROOT, args.cacheprefix + 'cache')
    args.msgdir = os.path.join(ROOT, args.cacheprefix + 'msg')
    for dn in (args.cachedir, args.msgdir):
        if not os.path.isdir(dn):
            os.makedirs(dn)

    global options
    options = args


class Section:
    def __init__(self, section):
        assert(len(section) == 3)
        self.section = section

    def __call__(self, f):
        self.f = f
        self.name = name = f.__name__
        self.desc = f.__doc__
        if not self.desc:
            raise TypeError('%s.__doc__ cannot be empty!' % name)
        self.args = inspect.getargspec(f).args
        if self.args not in [['cname'], ['cnames']]:
            raise TypeError('%s must take one parameter with name cname/cnames'
                            % name)
        self.multi = self.args == ['cnames']
        PAGE_SECTIONS.append(self)

        return self

    def maybeRun(self, cnames):
        if self.section in options.sections:
            self.run(cnames)
        else:
            log(u'Kører ikke %s da dette afsnit er fravalgt via --section'
                % self, 1)

    def run(self, cnames):
        if self.multi:
            self.f(cnames)
        else:
            for cname in cnames:
                self.f(cname)

    def __str__(self):
        return u'%s (%s)' % (self.section, self.desc)
