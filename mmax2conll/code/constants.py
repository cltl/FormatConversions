# COREA details
COREA_CGN_ID = 'CGN'
COREA_DCOI_ID = 'DCOI'
COREA_MED_ID = 'Med'

MMAX_WORD_TAG = 'word'
MMAX_WORDS_TAG = 'words'
MMAX_WORD_NUMBER_ATTRIBUTE = 'alppos'
COREA_MED_WORD_NUMBER_ATTRIBUTE = 'pos'
MMAX_WORD_ID_ATTRIBUTE = 'id'
MMAX_WORDS_DOCUMENT_ID_ATTRIBUTE = 'alpsent'
MMAX_PART_NUMBER_ATTRIBUTE = MMAX_WORDS_DOCUMENT_ID_ATTRIBUTE
MMAX_SENTENCE_STARTING_WORD_NUMBER = '0'    # This **must** be a string

MMAX_MARKABLE_TAG = 'markable'
MMAX_MARKABLES_TAG = 'markables'
MMAX_MARKABLE_ID_ATTRIBUTE = 'id'
MMAX_SPAN_ATTRIBUTE = 'span'
MMAX_HEAD_ATTRIBUTE = 'head'
MMAX_REF_ATTRIBUTE = 'ref'
MMAX_LEVEL_ATTRIBUTE = 'level'
MMAX_TYPE_ATTRIBUTE = 'type'
MMAX_TIME_ATTRIBUTE = 'time'
MMAX_MOD_ATTRIBUTE = 'mod'

# Config defaults
DEFAULT_CONFIG_FILE = './default_config.yml'
MIN_COLUMN_SPACING = 3
VALIDATE_XML = True
# The following value is different from the one in ./default_config.yml
AUTO_USE_MED_ITEM_READER = False

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
    'coref': '*',
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
