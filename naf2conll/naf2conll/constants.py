# Data processing
VALIDATE = True
UNIQUEYFY = False

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
    'POS': '[POS]',
    'parse_bit': '*',
    'pred_lemma': '-',
    'pred_frameset_ID': '-',
    'word_sense': '-',
    'speaker': 'UNKNOWN',
    'named_entities': '*',
    'coref': '-',
}
