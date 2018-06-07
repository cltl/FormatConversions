import itertools as it

from KafNafParserPy import Cterm

from . import constants as c
from .util import split_on_numbering


class NAFReader:
    def __init__(self, validate=c.VALIDATE,
                 sentence_start_number=c.SENTENCE_START_NUMBER):
        self.validate = validate
        self.sentence_start_number = sentence_start_number

    @staticmethod
    def extract_words(nafobj):
        return (
            {
                'id': token.get_id(),
                'word': token.get_text(),
                'sentence': int(token.get_sent()),
            }
            for token in nafobj.get_tokens()
        )

    def extract_sentences(self, nafobj):
        words = self.extract_words(nafobj)
        return split_on_numbering(
            words,
            lambda w: w['sentence'],
            self.validate,
            self.sentence_start_number
        )

    @classmethod
    def extract_coref_sets(cls, nafobj):
        """
        Extract coreference sets.

        A coreference set is a list of spans referring to the same thing
        A span is a list of word IDs
        """
        # Return an iterator of [ [word ID, word Id, ...], ...]
        return (
            # One reference "set" is a list of spans
            [
                # One span is a list of word IDs
                list(cls.token_ids_from_term_ids(
                    refspan.get_span_ids(),
                    nafobj
                ))
                for refspan in ref.get_spans()
            ]
            for ref in nafobj.get_corefs()
        )

    @staticmethod
    def token_ids_from_term_ids(term_ids, nafobj):
        """
        Get a token IDs, given a list of term IDs
        """
        return it.chain(*map(           # Flatten
            Cterm.get_span_ids,         # Get token IDs
            map(
                nafobj.get_term,        # Get term object
                term_ids
            )
        ))
