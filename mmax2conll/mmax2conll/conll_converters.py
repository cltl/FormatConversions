import logging
import itertools as it

from . import constants as c
from .util import ValidationError

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


class CorefConverter:
    """
    Convert coreference information to a format writeable by
    `.conll_writers.CoNLLWriter`
    """

    def __init__(self, sentences, uniqueyfy=c.UNIQUEYFY):
        self.sentences = sentences
        self.should_uniqueyfy = uniqueyfy
        self.word_ids = [word['id'] for word in it.chain(*sentences)]
        self.word_indices = dict(
            (ID, i) for i, ID in enumerate(self.word_ids)
        )

    @staticmethod
    def uniqueyfy(sets):
        """
        Make sure all spans within a refset are unique and that all refsets
        have a unique set of spans (i.e. no other refset has exactly the same
        set of spans).

        Also discards empty reference sets
        """
        all_spans = set()
        unique_sets = []
        for refset in sets:
            refset = list(map(tuple, refset))
            spans = frozenset(refset)
            if spans not in all_spans:
                all_spans.add(spans)
                spans = set()
                new_refset = []
                for span in refset:
                    if span not in spans:
                        spans.add(span)
                        new_refset.append(list(span))
                    else:
                        logger.debug(f"Discarding reference: {span}")
                if new_refset:
                    unique_sets.append(new_refset)
                else:
                    logger.debug("Discarding empty reference set")
            else:
                logger.debug(f"Discarding reference set: {refset}")
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug(
                f"Kept {len(all_spans)} reference sets"
                f" with {sum(map(len, all_spans))} references"
            )
        return unique_sets

    @staticmethod
    def coref_sets_from_MMAX_chains(chains):
        """
        Extract spans from MMAX coreference markable chains
        """
        return ([markable['span'] for markable in chain] for chain in chains)

    def word_id_map_from_coref_sets(self, sets):
        """
        Extract a `{word_id: (reference ID, position)}` map from a reference
        set, where `position` is either `start`, `end` or `singleton`.

        Validates whether the span refers to a consecutive collection of words.

        Assumes:
         - a reference set is a list of lists of word IDs

        Incrementally assigns a reference ID to reference sets.
        """
        if self.should_uniqueyfy:
            sets = self.uniqueyfy(sets)

        word_id_map = {}

        # Randomly create a reference ID for every reference refset
        for refID, refset in enumerate(sets):
            for span in refset:
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
        first = self.word_indices[span[0]]
        last = self.word_indices[span[-1]]
        if first > last:
            raise ValueError(
                "Illegal span specification: the first ID of a span"
                " abbreviation must appear in the words before the"
                f" last ID: {span}"
            )
        correct_span = self.word_ids[first:last + 1]

        if span != correct_span:
            raise ValueError(
                "Coreference spans in CoNLL must be consecutive. Found:"
                f" {span} which should be {correct_span}"
            )

    def add_data_from_MMAX_chains(self, chains):
        """
        Add coreference information from reference sets to sentence data.

        !! NB !! Changes data in-place.

        Assumes every word has an ID stored in 'id'.
        """
        self.add_data_from_coref_sets(
            self.coref_sets_from_MMAX_chains(chains)
        )

    def add_data_from_coref_sets(self, coref_sets):
        """
        Add coreference information from reference sets to sentence data.

        !! NB !! Changes data in-place.

        Assumes every word has an ID stored in 'id'.
        """
        id_map = self.word_id_map_from_coref_sets(coref_sets)

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

        for sentence in self.sentences:
            for word in sentence:
                if word['id'] in id_map:
                    word['coref'] = '|'.join(
                        it.starmap(ref_to_str, id_map[word['id']])
                    )
