# -*- coding: utf-8 -*-
import re
from typing import List, Pattern

USERNAME_MAX_LENGTH: int = 25
MESSAGE_MAX_LENGTH: int = 500

# Common patterns
_tmi = r'tmi\.twitch\.tv'
_tags = r'@(?P<tags>(?:[a-zA-Z0-9\-]+=[^ ;]*;?)+)'
_user = r'[a-z0-9][a-z0-9_]{2,%s}' % (USERNAME_MAX_LENGTH - 1)
_user_tmi = rf':(?P<who>{_user})!(?P=who)@(?P=who)\.{_tmi}'

USERNAME_REGEX: Pattern[str] = re.compile(rf'^@?{_user}$', flags=re.IGNORECASE)

EXPECTED_AUTH_CODES: List[str] = ['001', '002', '003', '004', '375', '372', '376']
AUTH_EXPECT_PATTERN: Pattern[str] = re.compile(rf'^:{_tmi} (?P<code>{"|".join(EXPECTED_AUTH_CODES)}) (?P<msg>.*)$')

CAP_REQ_MODES: List[str] = ['commands', 'membership', 'tags']
_cap_ack_part = rf'twitch\.tv/(?:{"|".join(CAP_REQ_MODES)})'
# noinspection RegExpUnnecessaryNonCapturingGroup
CAP_ACK_PATTERN: Pattern[str] = re.compile(rf'^:{_tmi} CAP \* ACK :(?P<cap>(?:{_cap_ack_part} )*(?:{_cap_ack_part}))$')

EXPECTED_JOIN_CODES: List[str] = ['353', '366']
JOIN_EXPECT_PATTERN: Pattern[str] = re.compile(rf'^{_user_tmi} JOIN #(?P<joined>{_user})$')

PART_EXPECT_PATTERN: Pattern[str] = re.compile(rf'^{_user_tmi} PART #(?P<left>{_user})$')

RECONNECT_PATTERN: Pattern[str] = re.compile(rf'^:{_tmi} RECONNECT$')

# Data patterns. Listed in decreasing order of approximate appearance percentage
PRIVMSG_PATTERN: Pattern[str] = re.compile(rf'^{_tags} {_user_tmi} PRIVMSG #(?P<where>{_user}) :(?P<message>.+)$')
JOIN_PART_PATTERN: Pattern[str] = re.compile(rf'^{_user_tmi} (?P<action>JOIN|PART) #(?P<where>{_user})$')
CLEARCHAT_PATTERN: Pattern[str] = re.compile(rf'^{_tags} :{_tmi} CLEARCHAT #(?P<where>{_user}) :(?P<who>{_user})$')
USERNOTICE_PATTERN: Pattern[str] = re.compile(
    rf'^{_tags} :{_tmi} USERNOTICE #(?P<where>{_user})(?: :(?P<message>.+))?$'
)
ROOMSTATE_PATTERN: Pattern[str] = re.compile(rf'^{_tags} :{_tmi} ROOMSTATE #(?P<where>{_user})$')
USERSTATE_PATTERN: Pattern[str] = re.compile(rf'^{_tags} :{_tmi} USERSTATE #(?P<where>{_user})$')
CLEARMSG_PATTERN: Pattern[str] = re.compile(rf'^{_tags} :{_tmi} CLEARMSG #(?P<where>{_user}) :(?P<message>.+)$')
NOTICE_PATTERN: Pattern[str] = re.compile(rf'^{_tags} :{_tmi} NOTICE #(?P<where>{_user}) :(?P<message>.+)$')
HOSTTARGET_PATTERN: Pattern[str] = re.compile(
    rf'^:{_tmi} HOSTTARGET #(?P<where>{_user}) :(?P<target>{_user}|-)(?: (?P<number_of_viewers>\d+|-))?$'
)
# noinspection RegExpUnnecessaryNonCapturingGroup
CODE_353_PATTERN: Pattern[str] = re.compile(
    rf'^:(?P<who>{_user})\.{_tmi} 353 (?P=who) = #(?P<where>{_user}) :(?P<users>(?:{_user} )*(?:{_user}))$'
)
CODE_366_PATTERN: Pattern[str] = re.compile(
    rf'^:(?P<who>{_user})\.{_tmi} 366 (?P=who) #(?P<where>{_user}) :End of /NAMES list$'
)
WHISPER_PATTERN: Pattern[str] = re.compile(rf'^{_tags} {_user_tmi} WHISPER #(?P<where>{_user}) :(?P<message>.+)$')

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
URL_PATTERN: Pattern[str] = re.compile(''.join(_url_pattern_parts))
