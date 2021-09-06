# -*- coding: utf-8 -*-
import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATABASE_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

USERNAME_MAX_LENGTH = 25

# Common patterns
_tmi = r'tmi\.twitch\.tv'
_tags = r'@(?P<tags>(?:[a-zA-Z0-9\-]+=[^ ;]*;?)+)'
_user = r'[a-z0-9][a-z0-9_]{2,%s}' % (USERNAME_MAX_LENGTH - 1)
_user_tmi = rf':(?P<who>{_user})!(?P=who)@(?P=who)\.{_tmi}'

USERNAME_REGEX = re.compile(rf'^@?{_user}$', flags=re.IGNORECASE)

EXPECTED_AUTH_CODES = ['001', '002', '003', '004', '375', '372', '376']
AUTH_EXPECT_PATTERN = re.compile(rf'^:{_tmi} (?P<code>{"|".join(EXPECTED_AUTH_CODES)}) (?P<msg>.*)$')

CAP_REQ_MODES = ['commands', 'membership', 'tags']
_cap_ack_part = rf'twitch\.tv/(?:{"|".join(CAP_REQ_MODES)})'
# noinspection RegExpUnnecessaryNonCapturingGroup
CAP_ACK_PATTERN = re.compile(rf'^:{_tmi} CAP \* ACK :(?P<cap>(?:{_cap_ack_part} )*(?:{_cap_ack_part}))$')

EXPECTED_JOIN_CODES = ['353', '366']
JOIN_EXPECT_PATTERN = re.compile(rf'^{_user_tmi} JOIN #(?P<joined>{_user})$')

PART_EXPECT_PATTERN = re.compile(rf'^{_user_tmi} PART #(?P<left>{_user})$')

RECONNECT_PATTERN = re.compile(rf'^:{_tmi} RECONNECT$')

_invoke_part = r'!?(?P<invoke>[a-z0-9]{1,15})'
COMMAND_ADD_PATTERN = re.compile(r'^!?(?P<invoke>[a-z0-9]{1,15}) +(?P<response>.+)$', flags=re.IGNORECASE)
COMMAND_DELETE_PATTERN = re.compile(r'^!?(?P<invoke>[a-z0-9]{1,15})$', flags=re.IGNORECASE)
COMMAND_EDIT_PATTERN = re.compile(
    r'^!?(?P<invoke>[a-z0-9]{1,15})(?:>!?(?P<rename>[a-z0-9]+))?(?: +(?P<response>.+))?$',
    flags=re.IGNORECASE,
)

COMMAND_TIMER_PATTERNS = dict(
    add=re.compile(
        r'^add +(?P<period>\d+)/(?P<offset>\d+|-) +!?(?P<invoke>[a-z0-9]{1,15}) +(?P<response>.+)$',
        flags=re.IGNORECASE,
    ),
    drop=re.compile(r'^drop +!?(?P<invoke>[a-z0-9]{1,15})$', flags=re.IGNORECASE),
    edit_period=re.compile(
        r'^edit +time +!?(?P<invoke>[a-z0-9]{1,15}) +(?P<period>\d+)/(?P<offset>\d+|-)$',
        flags=re.IGNORECASE,
    ),
    edit_response=re.compile(
        r'^edit +response +!?(?P<invoke>[a-z0-9]{1,15}) +(?P<response>.+)$',
        flags=re.IGNORECASE,
    ),
    stop_start=re.compile(r'^(?P<action>stop|start) +!?(?P<invoke>[a-z0-9]{1,15})$', flags=re.IGNORECASE),
)
COMMAND_TIMER_HELP = '''
New 1 minute timer on 5 seconds into the minute: "!{invoke} add 60/5 !discord Join the discord!"

Change the repeat period to 2 minutes and start immediately. If the command wasn't a timer, it is now: \
"!{invoke} edit time !discord 120/-"

Change the command response: "!{invoke} edit response !discord Consider joining the discord :)"

Start or stop the repeat: "!{invoke} start !discord" "!{invoke} stop !discord"
'''.strip()

# Data patterns. Listed in decreasing order of approximate appearance percentage
PRIVMSG_PATTERN = re.compile(rf'^{_tags} {_user_tmi} PRIVMSG #(?P<where>{_user}) :(?P<message>.+)$')
JOIN_PART_PATTERN = re.compile(rf'^{_user_tmi} (?P<action>JOIN|PART) #(?P<where>{_user})$')
CLEARCHAT_PATTERN = re.compile(rf'^{_tags} :{_tmi} CLEARCHAT #(?P<where>{_user}) :(?P<who>{_user})$')
USERNOTICE_PATTERN = re.compile(rf'^{_tags} :{_tmi} USERNOTICE #(?P<where>{_user})(?: :(?P<message>.+))?$')
ROOMSTATE_PATTERN = re.compile(rf'^{_tags} :{_tmi} ROOMSTATE #(?P<where>{_user})$')
USERSTATE_PATTERN = re.compile(rf'^{_tags} :{_tmi} USERSTATE #(?P<where>{_user})$')
CLEARMSG_PATTERN = re.compile(rf'^{_tags} :{_tmi} CLEARMSG #(?P<where>{_user}) :(?P<message>.+)$')
NOTICE_PATTERN = re.compile(rf'^{_tags} :{_tmi} NOTICE #(?P<where>{_user}) :(?P<message>.+)$')
HOSTTARGET_PATTERN = re.compile(
    rf'^:{_tmi} HOSTTARGET #(?P<where>{_user}) :(?P<target>{_user}|-)(?: (?P<number_of_viewers>\d+|-))?$'
)
# noinspection RegExpUnnecessaryNonCapturingGroup
CODE_353_PATTERN = re.compile(
    rf'^:(?P<who>{_user})\.{_tmi} 353 (?P=who) = #(?P<where>{_user}) :(?P<users>(?:{_user} )*(?:{_user}))$'
)
CODE_366_PATTERN = re.compile(rf'^:(?P<who>{_user})\.{_tmi} 366 (?P=who) #(?P<where>{_user}) :End of /NAMES list$')
WHISPER_PATTERN = re.compile(rf'^{_tags} {_user_tmi} WHISPER #(?P<where>{_user}) :(?P<message>.+)$')

LINK_PERMIT_TIMEOUT = 60
_domains = '|'.join(
    [  # this is a moving target
        'com',
        'net',
        'org',
        'edu',
        'gov',
        'mil',
        'aero',
        'asia',
        'biz',
        'cat',
        'coop',
        'info',
        'int',
        'jobs',
        'mobi',
        'museum',
        'name',
        'post',
        'pro',
        'tel',
        'travel',
        'xxx',
        'ac',
        'ad',
        'ae',
        'af',
        'ag',
        'ai',
        'al',
        'am',
        'an',
        'ao',
        'aq',
        'ar',
        'as',
        'at',
        'au',
        'aw',
        'ax',
        'az',
        'ba',
        'bb',
        'bd',
        'be',
        'bf',
        'bg',
        'bh',
        'bi',
        'bj',
        'bm',
        'bn',
        'bo',
        'br',
        'bs',
        'bt',
        'bv',
        'bw',
        'by',
        'bz',
        'ca',
        'cc',
        'cd',
        'cf',
        'cg',
        'ch',
        'ci',
        'ck',
        'cl',
        'cm',
        'cn',
        'co',
        'cr',
        'cs',
        'cu',
        'cv',
        'cx',
        'cy',
        'cz',
        'dd',
        'de',
        'dj',
        'dk',
        'dm',
        'do',
        'dz',
        'ec',
        'ee',
        'eg',
        'eh',
        'er',
        'es',
        'et',
        'eu',
        'fi',
        'fj',
        'fk',
        'fm',
        'fo',
        'fr',
        'ga',
        'gb',
        'gd',
        'ge',
        'gf',
        'gg',
        'gh',
        'gi',
        'gl',
        'gm',
        'gn',
        'gp',
        'gq',
        'gr',
        'gs',
        'gt',
        'gu',
        'gw',
        'gy',
        'hk',
        'hm',
        'hn',
        'hr',
        'ht',
        'hu',
        'id',
        'ie',
        'il',
        'im',
        'in',
        'io',
        'iq',
        'ir',
        'is',
        'it',
        'je',
        'jm',
        'jo',
        'jp',
        'ke',
        'kg',
        'kh',
        'ki',
        'km',
        'kn',
        'kp',
        'kr',
        'kw',
        'ky',
        'kz',
        'la',
        'lb',
        'lc',
        'li',
        'lk',
        'lr',
        'ls',
        'lt',
        'lu',
        'lv',
        'ly',
        'ma',
        'mc',
        'md',
        'me',
        'mg',
        'mh',
        'mk',
        'ml',
        'mm',
        'mn',
        'mo',
        'mp',
        'mq',
        'mr',
        'ms',
        'mt',
        'mu',
        'mv',
        'mw',
        'mx',
        'my',
        'mz',
        'na',
        'nc',
        'ne',
        'nf',
        'ng',
        'ni',
        'nl',
        'no',
        'np',
        'nr',
        'nu',
        'nz',
        'om',
        'pa',
        'pe',
        'pf',
        'pg',
        'ph',
        'pk',
        'pl',
        'pm',
        'pn',
        'pr',
        'ps',
        'pt',
        'pw',
        'py',
        'qa',
        're',
        'ro',
        'rs',
        'ru',
        'rw',
        'sa',
        'sb',
        'sc',
        'sd',
        'se',
        'sg',
        'sh',
        'si',
        'sj',
        'Ja',
        'sk',
        'sl',
        'sm',
        'sn',
        'so',
        'sr',
        'ss',
        'st',
        'su',
        'sv',
        'sx',
        'sy',
        'sz',
        'tc',
        'td',
        'tf',
        'tg',
        'th',
        'tj',
        'tk',
        'tl',
        'tm',
        'tn',
        'to',
        'tp',
        'tr',
        'tt',
        'tv',
        'tw',
        'tz',
        'ua',
        'ug',
        'uk',
        'us',
        'uy',
        'uz',
        'va',
        'vc',
        've',
        'vg',
        'vi',
        'vn',
        'vu',
        'wf',
        'ws',
        'ye',
        'yt',
        'yu',
        'za',
        'zm',
        'zw',
    ]
)
_domains = rf'(?:{_domains})'
_url_pattern_parts = [
    r'(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+\.' + _domains + r'/)',
    _domains,
    r'(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+',
    r'''(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])''',
    r'|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*\.' + _domains + r'\b/?(?!@)))',
]
URL_PATTERN = re.compile(''.join(_url_pattern_parts))
