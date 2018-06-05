# Config defaults
DEFAULT_CONFIG_FILE = './default_config.yml'
MIN_COLUMN_SPACING = 3
VALIDATE_XML = True
# The following value is different from the one in ./default_config.yml
AUTO_USE_MED_ITEM_READER = False
WARN_ON_AUTO_USE_MED_ITEM_READER = True
ALLOW_OVERWRITING = False
COREF_TYPE_FILTER = 'ident_or_bridge'
COREF_LEVEL_FILTER = 'reference'
CONLL_EXTENSION = '.conll'
RAW_EXTENSION = '.txt'
WORDS_DIR = 'Basedata'
WORDS_FILES_EXTENSION = '_words.xml'
MARKABLES_DIR = 'Markables'
# COREF_FILES_EXTENSION = '_coref_level.xml'          # for COREA
# SENTENCES_FILES_EXTENSION = None   # for COREA
COREF_FILES_EXTENSION = '_np_level.xml'             # for SoNaR
SENTENCES_FILES_EXTENSION = '_sentence_level.xml'   # for SoNaR
LOG_ON_ERROR = False
DIRS_TO_IGNORE = {'Configuration'}

CONLL_DEFAULTS = {
    'document_id': 'UNKNOWN',
    'part_number': '0',
    'word_number': '[WORD_NUMBER]',
    'word': '[WORD]',
    'POS': '[POS]',
    'parse_bit': '*',
    'pred_lemma': '-',
    'pred_frameset_ID': '-',
    'word_sense': '-',
    'speaker': 'UNKNOWN',
    'named_entities': '*',
    'coref': '-',
}

CONLL_ON_MISSING = {
    'document_id': 'throw',
    'part_number': 'nothing',
    'word_number': 'throw',
    'word': 'throw',
    'POS': 'nothing',
    'parse_bit': 'nothing',
    'pred_lemma': 'nothing',
    'pred_frameset_ID': 'nothing',
    'word_sense': 'nothing',
    'speaker': 'nothing',
    'named_entities': 'nothing',
    'coref': 'nothing',
}

# COREA details
COREA_CGN_ID = 'CGN'
COREA_DCOI_ID = 'DCOI'
COREA_MED_ID = 'Med'


# MMAX details
def MMAX_POSITION_FROM_ID(ID):
    """
    Extract the position from a MMAX ID
    """
    return int(str(ID).split('_')[-1])


# Words files details
MMAX_WORD_TAG = 'word'
MMAX_WORDS_TAG = 'words'
MMAX_WORD_NUMBER_ATTRIBUTE = 'alppos'
COREA_MED_WORD_NUMBER_ATTRIBUTE = 'pos'
MMAX_WORD_ID_ATTRIBUTE = 'id'
MMAX_WORDS_DOCUMENT_ID_ATTRIBUTE = 'alpsent'
MMAX_PART_NUMBER_ATTRIBUTE = MMAX_WORDS_DOCUMENT_ID_ATTRIBUTE
MMAX_SENTENCE_STARTING_WORD_NUMBER = '0'    # This **must** be a string


def MMAX_WORDS_FILTER(item): return True


# Markables files details
MMAX_MARKABLE_TAG = 'markable'
MMAX_MARKABLES_TAG = 'markables'
MMAX_MARKABLE_ID_ATTRIBUTE = 'id'
MMAX_SPAN_ATTRIBUTE = 'span'
MMAX_LEVEL_ATTRIBUTE = 'mmax_level'


# Sentences files details
def MMAX_SENTENCES_FILTER(item): return True


# Coreference files details
COREF_LEVEL_ATTRIBUTE = 'level'
COREF_TYPE_ATTRIBUTE = 'type'
COREF_HEAD_ATTRIBUTE = 'head'
COREF_REF_ATTRIBUTE = 'ref'
COREF_TIME_ATTRIBUTE = 'time'
COREF_MOD_ATTRIBUTE = 'mod'
COREF_EMPTY_REF_VALUE = 'empty'

# The coreference data from the COREA dataset can be of different types:

# -- Start of quote (p.117 -- 118) from:
#    COREA: Coreference Resolution for Extracting Answers for Dutch
#    Iris Hendrickx, Gosse Bouma, Walter Daelemans, and Véronique Hoste.
#    Essential Speech and Language Technology for Dutch, Ch.7, p.115 -- 128
#    Editors: Peter Spyns, Jan Odijk
#    https://link.springer.com/book/10.1007/978-3-642-30910-6

# Annotation focuses primarily on coreference or IDENTITY relations between
# noun phrases, where both noun phrases refer to the same extra-linguistic
# entity. These multiple references to the same entity can be regarded as a
# coreferential chain of references.

# While these form the majority of coreference relations in our corpus, there
# are also a number of special cases.

# A BOUND relation exists between an anaphor and a quantified antecedent, as in
# "Everybody_i did what they_i could".

# A BRIDGE relation is used to annotate part-whole or set-subset relations, as
# in "the tournament_i ... the quarter finals_i".

# We also marked predicative (PRED) relations, as in
# "Michiel Beute_i is a writer_i". Strictly speaking, these are not coreference
# relations, but we  annotated them for a practical reason.

# (...)

# The main sources of disagreement were cases where one of the annotators fails
# to annotate a relation, where there is confusion between PRED or BRIDGE and
# IDENT, and various omissions in the guidelines (i.e. whether to consider
# headlines and other leading material in newspaper articles as part of the
# text to be annotated).

# -- End of quote

MMAX_TYPE_FILTERS = {
    'ident': lambda i: 'type' not in i or i['type'] == 'bridge',
    'ident_or_bridge': lambda i:
        'type' not in i or
        i['type'] == 'ident' or
        i['type'] == 'bound',
    'bridge': lambda i: 'type' not in i or i['type'] == 'bridge',
    'pref': lambda i: 'type' not in i or i['type'] == 'pref',
    'none': lambda i: True,
}
MMAX_LEVEL_FILTERS = {
    'reference': lambda i: 'level' not in i or i['level'] == 'reference',
    'sense': lambda i: 'level' not in i or i['level'] == 'sense',
    'none': lambda i: True,
}


def MMAX_COREF_FILTER(item):
    return MMAX_TYPE_FILTERS[COREF_TYPE_FILTER](item) and \
        MMAX_LEVEL_FILTERS[COREF_LEVEL_FILTER](item)
