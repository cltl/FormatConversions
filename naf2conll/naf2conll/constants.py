#  ---- Configuration defaults ---- start
# Data processing
VALIDATE = True
UNIQUEYFY = False
FILL_NON_CONSECUTIVE_COREF_SPANS = False
SENTENCE_FILTER = 'none'

# Reporting
ALLOW_OVERWRITING = False
LOG_ON_ERROR = True

# NAF
NAF_EXTENSION = '.naf'
DIRS_TO_IGNORE = []

# CoNLL
CONLL_EXTENSION = '.conll'
MIN_COLUMN_SPACING = 3

CONLL_COLUMNS = [
    # 'part_number',
    'word_number',
    'word',
    'problem',
    # 'POS',
    # 'parse_bit',
    # 'pred_lemma',
    # 'pred_frameset_ID',
    # 'word_sense',
    # 'speaker',
    # 'named_entities',
    'coref',
]

CONLL_ON_MISSING = {
    'document_id': 'throw',
    'part_number': 'nothing',
    'word_number': 'throw',
    'word': 'throw',
    'problem': 'nothing',
    'POS': 'nothing',
    'parse_bit': 'nothing',
    'pred_lemma': 'nothing',
    'pred_frameset_ID': 'nothing',
    'word_sense': 'nothing',
    'speaker': 'nothing',
    'named_entities': 'nothing',
    'coref': 'nothing',
}

CONLL_DEFAULTS = {
    'document_id': 'UNKNOWN',
    'part_number': 0,
    'word_number': '[WORD_NUMBER]',
    'word': '[WORD]',
    'problem': '',
    'POS': '[POS]',
    'parse_bit': '*',
    'pred_lemma': '-',
    'pred_frameset_ID': '-',
    'word_sense': '-',
    'speaker': 'UNKNOWN',
    'named_entities': '*',
    'coref': '-',
}
#  ---- Configuration defaults ---- end

SENTENCE_START_NUMBER = 1

SENTENCE_FILTERS = {
    'none': lambda x: x,
    'has_problem': lambda s: any('problem' in w for w in s),
    'no_problem': lambda s: all('problem' not in w for w in s),
}
SENTENCE_DEFAULT_FILTER = SENTENCE_FILTERS[SENTENCE_FILTER]


# MMAX details
def MMAX_POSITION_FROM_ID(ID):
    """
    Extract the position from a MMAX ID
    """
    return int(str(ID).split('_')[-1])


def MMAX_SAFE_POSITION_FROM_ID(ID):
    """
    Extract the position from a MMAX ID and return ID on failure
    """
    try:
        return MMAX_POSITION_FROM_ID(ID)
    except ValueError:
        return ID
