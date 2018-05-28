from .util import ValidationError


class CorefConverter:
    """
    Convert coreference information to a format writeable by
    `.conll_writers.CoNLLWriter`
    """

    @classmethod
    def word_id_map_from_MMAX_sets(cls, sets):
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
            for reference in refset:
                span = reference['span']
                cls.validate_MMAX_span(span)
                if len(span) == 1:
                    word_id_map[span[0]] = (refID, 'singleton')
                else:
                    word_id_map[span[0]] = (refID, 'start')
                    word_id_map[span[-1]] = (refID, 'end')

        return word_id_map

    @staticmethod
    def validate_MMAX_span(span):
        """
        Validate the words in a span are consecutive.

        Assumes:
         - the span is a list of word IDs
         - `str(ID).split('_')[-1]` is the position of a word
        """
        positions = [int(str(ID).split('_')[-1]) for ID in span]
        if any(
            expected != pos
            for expected, pos in zip(
                range(positions[0], positions[0] + len(positions)),
                positions
            )
           ):
            raise ValidationError(
                "Coreference spans in CoNLL must be consecutive. Found:"
                f" {span}"
            )

    @classmethod
    def add_data_from_coref_sets(cls, sentences, coref_sets):
        """
        Add coreference information from reference sets to sentence data.

        !! NB !! Changes data in-place.

        Assumes every word has an ID stored in 'id'.
        """
        id_map = cls.word_id_map_from_MMAX_sets(coref_sets)
        for sentence in sentences:
            for word in sentence:
                if word['id'] in id_map:
                    refID, pos = id_map[word['id']]
                    if pos == 'singleton':
                        ref_str = f'({refID})'
                    elif pos == 'start':
                        ref_str = f'({refID}'
                    elif pos == 'end':
                        ref_str = f'{refID})'
                    else:
                        raise ValueError(
                            f"The position of the reference of {word} must be"
                            " either `start`, `end` or `singleton`. Found:"
                            f" {pos}"
                        )
                    word['coref'] = ref_str
