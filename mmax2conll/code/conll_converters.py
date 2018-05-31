import itertools as it

from . import constants as c
from .util import ValidationError, is_consecutive


class CorefConverter:
    """
    Convert coreference information to a format writeable by
    `.conll_writers.CoNLLWriter`
    """

    def __init__(self, position_from_ID=c.MMAX_POSITION_FROM_ID):
        self.position_from_ID = position_from_ID

    def word_id_map_from_MMAX_sets(self, sets):
        """
        Extract a `{word_id: (reference ID, position)}` map from a reference
        chain, where `position` is either `start`, `end` or `singleton`.

        Validates whether the span refers to a consecutive collection of words.

        Assumes:
         - the span is a list of word IDs
         - `str(ID).split('_')[-1]` is the position of a word

        Incrementally assigns a reference ID to reference sets.
        """
        word_id_map = {}

        # Randomly create a reference ID for every reference refset
        for refID, refset in enumerate(sets):
            # Make sure the spans are unique
            for span in set(map(lambda ref: tuple(ref['span']), refset)):
                self.validate_span(span)
                if len(span) == 1:
                    word_id_map.setdefault(span[0], []).append(
                        (refID, 'singleton')
                    )
                else:
                    word_id_map.setdefault(span[0], []).append(
                        (refID, 'start')
                    )
                    word_id_map.setdefault(span[-1], []).append(
                        (refID, 'end')
                    )

        return word_id_map

    def validate_span(self, span):
        if not is_consecutive(map(self.position_from_ID, span)):
            raise ValidationError(
                "Coreference spans in CoNLL must be consecutive. Found:"
                f" {span}"
            )

    def add_data_from_coref_sets(self, sentences, coref_sets):
        """
        Add coreference information from reference sets to sentence data.

        !! NB !! Changes data in-place.

        Assumes every word has an ID stored in 'id'.
        """
        id_map = self.word_id_map_from_MMAX_sets(coref_sets)

        def ref_to_str(refID, pos):
            if pos == 'singleton':
                return f'({refID})'
            elif pos == 'start':
                return f'({refID}'
            elif pos == 'end':
                return f'{refID})'
            else:
                raise ValueError(
                    f"The position of the reference of {word} must be"
                    " either `start`, `end` or `singleton`. Found:"
                    f" {pos}"
                )

        for sentence in sentences:
            for word in sentence:
                if word['id'] in id_map:
                    word['coref'] = '|'.join(
                        it.starmap(ref_to_str, id_map[word['id']])
                    )
