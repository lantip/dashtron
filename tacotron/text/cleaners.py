""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from .numbers import normalize_numbers
from .angka import normalize_angka


# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
    ('mrs', 'misess'),
    ('mr', 'mister'),
    ('dr', 'doctor'),
    ('st', 'saint'),
    ('co', 'company'),
    ('jr', 'junior'),
    ('maj', 'major'),
    ('gen', 'general'),
    ('drs', 'doctors'),
    ('rev', 'reverend'),
    ('lt', 'lieutenant'),
    ('hon', 'honorable'),
    ('sgt', 'sergeant'),
    ('capt', 'captain'),
    ('esq', 'esquire'),
    ('ltd', 'limited'),
    ('col', 'colonel'),
    ('ft', 'fort'),
]]


# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations_id = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
    ('dr', 'dokter'),
    ('tn', 'tuan'),
    ('ny', 'nyonya'),
    ('drs', 'dokterandes'),
    ('sh', 'sarjana hukum'),
    ('yg', 'yang'),
]]

def isDomain(str):
    regex = "^((?!-)[A-Za-z0-9-]" \
            "{1,63}(?<!-)\\.)" \
            "+[A-Za-z]{2,6}"
    p = re.compile(regex)
    if (str == None):
        return False
    if(re.search(p, str)):
        return True
    else:
        return False

def expand_abbreviations(text):
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text

def expand_abbreviations_id(text):
    for regex, replacement in _abbreviations_id:
        text = re.sub(regex, replacement, text)
    return text

def expand_domain_name(text):
    txts = text.split(' ')
    text = []
    for tx in txts:
        if '.' in tx:
            if isDomain(tx):
                tx = tx.replace('.id', '.ide')
                tx = tx.replace('.',' dot ')
        if tx == 'update':
            tx = 'apdet'
        text.append(tx)
    return ' '.join(text)

def expand_numbers(text):
    return normalize_numbers(text)


def expand_numbers_id(text):
    return normalize_angka(text)

def lowercase(text):
    return text.lower()


def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
    return unidecode(text)


def basic_cleaners(text):
    '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def transliteration_cleaners(text):
    '''Pipeline for non-English text that transliterates to ASCII.'''
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def english_cleaners(text):
    '''Pipeline for English text, including number and abbreviation expansion.'''
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = expand_numbers(text)
    text = expand_abbreviations(text)
    text = collapse_whitespace(text)
    return text


def indonesian_cleaners(text):
    '''Pipeline for Indonesian text, including number and abbreviation expansion.'''
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = expand_domain_name(text)
    text = expand_numbers_id(text)
    text = expand_abbreviations_id(text)
    text = collapse_whitespace(text)
    return text
