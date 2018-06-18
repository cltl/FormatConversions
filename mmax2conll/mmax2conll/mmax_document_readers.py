import re
import logging
from os import path
import itertools as it

from . import constants as c
from .util import ValidationError
from .mmax_item_readers import (
    SoNaRWordReader,
    COREAWordReader,
    MMAXMarkableReader,
    MMAXCorefReader
)

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def document_ID_from_filename(filename, extension):
    """
    Extract the document ID (or None) from the base name of a file.

    !! NB !! Special case for Med adds `Med/` to the base name

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """
    basename = path.basename(filename)
    if basename.endswith(extension):
        bare_doc_id = basename[:-len(extension)]
        if re.match(r'^s\d+$', bare_doc_id):
            return c.COREA_MED_ID + '/' + bare_doc_id
        else:
            return bare_doc_id
    return None


def add_sentence_layer_to_words(words, sentence_items):
    """
    Splits a collection of words into a sequence of sentences using information
    from a sequence of sentence items.

    Returns a list of lists of words
    """
    words = {word['id']: word for word in words}
    return [
        [words.get(ID) for ID in sentence_item['span']]
        for sentence_item in sentence_items
    ]


def add_word_numbers(sentences):
    """
    Add word numbers in place
    """
    for sentence in sentences:
        for number, word in enumerate(sentence):
            word['word_number'] = number


class XMLItemReader:
    """
    Reads and (optionally) validates data from an XML-tree.

    Things that are verified if `validate=True`:
     - the tag of the root element is as expected
     - the tag of all the word elements is as expected
    """

    def __init__(self, item_reader, validate, expected_child_tag,
                 expected_root_tag, item_filter=lambda i: True):
        self.item_reader = item_reader
        self.validate = validate
        self.expected_child_tag = expected_child_tag
        self.expected_root_tag = expected_root_tag
        self.item_filter = item_filter

    def get_child_elements(self, xml):
        """
        Get the XML-elements of the direct children of the root and validate:
         - the tag of the root element
         - the tag of the child elements
        """
        root = xml.getroot()

        # Create `rm_ns` function to remove the name space
        if self.validate and None in root.nsmap:
            ns = root.nsmap[None]
            nslen = len(ns)

            def rm_ns(tag):
                if tag[0] == '{' and tag[nslen+1] == '}' and \
                   tag[1:nslen+1] == ns:
                    return tag[nslen+2:]
                else:
                    return tag
        else:
            def rm_ns(tag):
                return tag

        if self.validate:
            if rm_ns(root.tag) != self.expected_root_tag:
                raise ValidationError(
                    f"The root element did not have the expected tag"
                    f" {self.expected_root_tag!r}. Found: {root.tag!r} and"
                    f" using: {rm_ns(root.tag)!r}"
                )

        children = root.getchildren()
        if self.validate:
            for child in children:
                if rm_ns(child.tag) != self.expected_child_tag:
                    raise ValidationError(
                        f"One of the children did not have the expected tag"
                        f" {self.expected_child_tag!r}."
                        f" Found: {child.tag!r} and"
                        f" using: {rm_ns(child.tag)!r}"
                    )
        return children

    def extract_all_items(self, xml):
        """
        Extract all information for every item.

        Returns an iterator of things returned by `self.item_reader.read`
        """
        return map(self.item_reader.read, self.get_child_elements(xml))

    def extract_items(self, xml):
        """
        Extract all information for every item, filtering items using
        `self.item_filter`.

        Returns an iterator of things returned by `self.item_reader.read`
        """
        return filter(self.item_filter, self.extract_all_items(xml))


class SoNaRWordsDocumentReader(XMLItemReader):
    """
    Reads and (optionally) validates data from a MMAX words XML-tree from the
    SoNaR-1 corpus.

    Things that are verified if `validate=True`:
     - the tag of the root element is as expected
     - the tag of all the word elements is as expected

    See
    https://ivdnt.org/downloads/taalmaterialen/tstc-sonar-corpus
    for (a description of) the SoNaR Corpus

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, item_reader=None,
                 validate=c.VALIDATE_XML,
                 expected_child_tag=c.MMAX_WORD_TAG,
                 expected_root_tag=c.MMAX_WORDS_TAG,
                 item_filter=c.MMAX_WORDS_FILTER):
        # Default item_reader
        item_reader = item_reader \
            if item_reader is not None \
            else SoNaRWordReader()
        super(SoNaRWordsDocumentReader, self).__init__(
            item_reader=item_reader,
            validate=validate,
            expected_child_tag=expected_child_tag,
            expected_root_tag=expected_root_tag,
            item_filter=item_filter,
        )


class SoNaRSentencesDocumentReader(XMLItemReader):
    """
    Reads and (optionally) validates data from a MMAX sentence XML-tree from
    the SoNaR-1 corpus.

    Things that are verified if `validate=True`:
     - the tag of the root element is as expected
     - the tag of all the sentence elements is as expected
     - the span of a all sentences are consecutive within a sentence
     - the spans of a all sentences are consecutive between sentences

    See
    https://ivdnt.org/downloads/taalmaterialen/tstc-sonar-corpus
    for (a description of) the SoNaR Corpus

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, words, item_reader=None,
                 validate=c.VALIDATE_XML,
                 pos_from_sentence_ID=c.MMAX_POSITION_FROM_ID,
                 expected_child_tag=c.MMAX_MARKABLE_TAG,
                 expected_root_tag=c.MMAX_MARKABLES_TAG,
                 item_filter=c.MMAX_SENTENCES_FILTER):
        self.word_ids = [word['id'] for word in words]
        self.word_indices = dict(
            (ID, i) for i, ID in enumerate(self.word_ids)
        )

        # Default item_reader
        item_reader = item_reader \
            if item_reader is not None \
            else MMAXMarkableReader(self.word_ids)
        super(SoNaRSentencesDocumentReader, self).__init__(
            item_reader=item_reader,
            validate=validate,
            expected_child_tag=expected_child_tag,
            expected_root_tag=expected_root_tag,
            item_filter=item_filter,
        )
        self.pos_from_sentence_ID = pos_from_sentence_ID

    def extract_items(self, xml):
        """
        Extract and optionally validate a sequence of sentence items sorted by
        position, which is taken from the ID.
        """
        items = super(SoNaRSentencesDocumentReader, self).extract_items(xml)
        items = sorted(items, key=lambda s: self.pos_from_sentence_ID(s['id']))
        if self.validate:
            self.validate_sentence_spans(items)
        return items

    def validate_sentence_spans(self, sentence_items):
        first_span = []
        index = 0
        while not first_span and len(sentence_items) > index:
            first_span = sentence_items[index]['span']
            index += 1
        index -= 1
        if self.word_ids and first_span[0] != self.word_ids[0]:
            raise ValidationError(
                "The first non-empty sentence does not start with the first"
                f" word (id: {self.word_ids[0]}): {sentence_items[index]}"
            )

        prev_last_id = first_span[-1]
        for item in sentence_items[index + 1:]:
            span = item['span']
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
                raise ValidationError(
                    f"The span of this sentence should be {correct_span}:"
                    f" {item!r}"
                )
            if self.word_indices[prev_last_id] != first - 1:
                raise ValidationError(
                    f"The first word of this sentence ({span[0]}) is not"
                    " directly after the last word of the previous sentence"
                    f" ({prev_last_id}): {item}"
                )
            else:
                prev_last_id = span[-1]


class COREAWordsDocumentReader(XMLItemReader):
    """
    Reads and (optionally) validates data from a MMAX words XML-tree from the
    COREA corpus.

    Things that are verified if `validate=True`:
     - the tag of the root element is as expected
     - the tag of all the word elements is as expected
     - the word numbers are consistent
     - the part numbers are consistent

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, item_reader=None,
                 validate=c.VALIDATE_XML,
                 document_id_attr=c.MMAX_WORDS_DOCUMENT_ID_ATTRIBUTE,
                 sent_start_word_number=c.MMAX_SENTENCE_STARTING_WORD_NUMBER,
                 expected_child_tag=c.MMAX_WORD_TAG,
                 expected_root_tag=c.MMAX_WORDS_TAG,
                 item_filter=c.MMAX_WORDS_FILTER):
        # Default item_reader
        item_reader = item_reader \
            if item_reader is not None \
            else COREAWordReader()
        super(COREAWordsDocumentReader, self).__init__(
            item_reader=item_reader,
            validate=validate,
            expected_child_tag=expected_child_tag,
            expected_root_tag=expected_root_tag,
            item_filter=item_filter,
        )
        self.document_id_attr = document_id_attr
        self.sent_start_word_number = sent_start_word_number

    def extract_document_ID(self, xml):
        """
        Extract the document ID (or None) from XML-data from the COREA corpus.

        !! NB !! This method is hard-coded for the COREA corpus and
                 only works for the CGN and DCOI parts of the corpus.

        See Ch. 7 of Essential Speech and Language Technology for Dutch
        COREA: Coreference Resolution for Extracting Answers for Dutch
        https://link.springer.com/book/10.1007/978-3-642-30910-6
        """
        rough_id = next(xml.getroot().iterchildren()).attrib.get(
            self.document_id_attr,
            ''
        )

        if rough_id.startswith('comp'):
            # This is part of the CGN part of COREA
            # The id looks like this:
            #   comp-j/nl/fn007136/fn007136__1.xml
            # and I want it to look like this:
            #   CGN/comp-j/nl/fn007136
            return c.COREA_CGN_ID + '/' + '/'.join(rough_id.split('/')[:-1])
        elif rough_id.startswith('WR-P-P-H-'):
            # This is part of the DCOI part of COREA
            # The id looks like this:
            #   WR-P-P-H-0000000001.p.1.s.1.xml
            # and I want it to look like this:
            #   DCOI/WR-P-P-H-0000000001
            return c.COREA_DCOI_ID + '/' + rough_id.split('.')[0]
        else:
            return None

    def extract_sentences(self, xml):
        """
        Extract all sentences and validate them.

        Returns a list of sentences, where a sentence is a list of things
        returned by `self.item_reader.read`.
        """
        words = self.extract_items(xml)
        sentences = []
        sentence = None

        # Because sentence is None, an error will be raised if the first word
        # has a word_number different from '0'
        while True:
            # Get the next word or stop if there isn't one
            try:
                word = next(words)
            except StopIteration:
                break

            # Check if we should start a new sentence and use `continue` if
            # we should not start a new sentence.
            if word['word_number'] != self.sent_start_word_number:
                # I'm using try-catch because this is an edge case and checking
                # every time is therefore more costly than catching once.
                try:
                    sentence.append(word)
                except AttributeError as e:
                    if sentence is None:
                        # We know what's wrong!
                        # Ignore if we're not validating
                        if self.validate:
                            raise ValidationError(
                                f"The first word ({word['word']!r}) does not"
                                f" have 'word_number' =="
                                f" {self.sent_start_word_number!r}. Found:"
                                f" {word['word_number']!r}"
                            ) from e
                        # else ignore this problem and fix it by starting a new
                        # sentence. The program flow will end up in the piece
                        # of code below that creates a new sentence.
                    else:
                        # We don't know what's wrong :(
                        raise e
                else:
                    # Adding the word to the existing sentence worked just fine
                    # So prevent creating a new sentence.
                    continue

            # This is the start of a new sentence, because the previous code
            # block would have called `continue` if it wasn't.
            # This is to prevent duplication of the following two lines.
            # The word_number is now validated
            sentence = [word]
            sentences.append(sentence)

        if self.validate:
            self.validate_sentences(sentences)

        return sentences

    @classmethod
    def validate_sentences(cls, sentences):
        """
        Validate `word_number` and `part_number` of these sentences
        """
        cls.validate_word_number(sentences)
        cls.validate_part_number(sentences)

    @staticmethod
    def validate_word_number(sentences):
        """
        Validate word number of these sentences

        `word_number` must:
         - correspond to `range(len(sentence))`
        """
        expected_msg = 'invalid literal for int() with base 10: '

        for senti, sentence in enumerate(sentences):
            # First quickly check
            word_numbers = map(
                int,
                map(
                    dict.get,
                    sentence,
                    it.repeat('word_number')
                )
            )
            try:
                problem = any(i != wn for i, wn in enumerate(word_numbers))
            except ValueError as e:
                if e.args[0].startswith(expected_msg):
                    problem = True
                else:
                    raise e

            # Find out what's wrong.
            if problem:
                index = 0
                for word in sentence:
                    try:
                        word_number = int(word['word_number'])
                    except ValueError as e:
                        if e.args[0].startswith(expected_msg):
                            raise ValidationError(
                                f"The word number of {word['word']!r} is not a"
                                f" number but {word['word_number']!r}."
                                f" This is in sentence #{senti}: {sentence!r}."
                            ) from e
                        else:
                            raise e
                    else:
                        if word_number != index:
                            raise ValidationError(
                                f"The word number of {word['word']!r} is the"
                                f" wrong value. Expected {index}, found:"
                                f" {word_number}."
                                f" This is in sentence #{senti}: {sentence!r}."
                            )
                        index += 1

    @staticmethod
    def validate_part_number(sentences):
        """
        Validate part number of these sentences

        Assumes `word_number` is already validated.

        `part_number` must be:
         - an integer, None or missing
         - increasing or (missing or None) everywhere
         - the same within a sentence
        """
        prev_part_number = None
        for senti, sentence in enumerate(sentences):
            if len(sentence) == 0:
                logger.warn(f"Sentence #{senti} is empty")

            for word in sentence:
                part_number = word.get('part_number', None)
                if part_number is None:
                    break
                try:
                    part_number = int(part_number)
                except ValueError as e:
                    raise ValidationError(
                        f"The part number of {word['word']!r} is not a"
                        f" number but {word['part_number']!r}."
                        f" This is in sentence #{senti}: {sentence!r}."
                    ) from e
                if word['word_number'] == '0':
                    prev_part_number = part_number
                elif prev_part_number != part_number:
                    raise ValidationError(
                        f"The part number of {word['word']!r} is different"
                        f" from the part number of the first word of the"
                        f" sentence. Expected {prev_part_number}, found:"
                        f" {part_number}."
                        f" This is in sentence #{senti}: {sentence!r}."
                    )

            if part_number is None:
                # The first part number was None, which means _all_ part
                # numbers should be None
                others_have_number = (
                    word.get('part_number', None) is not None
                    for sentence in sentences
                    for word in sentence
                )
                if prev_part_number is not None or any(others_have_number):
                    raise ValidationError(
                        f"Sentence #{senti} is missing a part number:"
                        f" {sentence!r}."
                    )
                else:
                    # Everything is None, so we're Done!
                    break

            if prev_part_number != part_number:
                if prev_part_number > part_number:
                    raise ValidationError(
                        f"The part number of sentence #{senti} should be"
                        f" greater than {prev_part_number}."
                        f" Found: {part_number}"
                    )


class MMAXCorefDocumentReader(XMLItemReader):
    """
    Reads and (optionally) validates data from a MMAX markables XML-tree.

    Things that are verified if `validate=True`:
     - the tag of the root element is as expected
     - the tag of all the word elements is as expected

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, words, item_reader=None,
                 validate=c.VALIDATE_XML,
                 expected_child_tag=c.MMAX_MARKABLE_TAG,
                 expected_root_tag=c.MMAX_MARKABLES_TAG,
                 item_filter=c.MMAX_COREF_FILTER):
                # Default item_reader
        item_reader = item_reader \
            if item_reader is not None \
            else MMAXCorefReader(word['id'] for word in words)
        super(MMAXCorefDocumentReader, self).__init__(
            item_reader=item_reader,
            validate=validate,
            expected_child_tag=expected_child_tag,
            expected_root_tag=expected_root_tag,
            item_filter=item_filter,
        )

    def extract_coref_sets(self, xml):
        """
        Extract the sets of markables that refer to the same entity.

        !! NB !! Returns a list because dicts are not hashable
        """
        all_markables = {m['id']: m for m in self.extract_all_items(xml)}
        markables = {
            ID: m
            for ID, m in filter(
                lambda tup: self.item_filter(tup[1]),
                all_markables.items()
            )
        }

        # Create a ID -> [markables referring to ID]
        forward_refs = {}

        for markable in markables.values():
            ref = markable.get('ref', None)
            # If ref is None, this markable does not refer to anything
            if ref is not None:
                if self.validate:
                    if ref not in all_markables:
                        raise ValidationError(
                            f"Reference to unknown markable ({ref!r}):"
                            f" {markable}"
                        )
                forward_refs.setdefault(ref, []).append(markable['id'])

        sets = []
        for root in markables.values():
            if root.get('ref', None) is None or root['ref'] not in markables:
                refset = []
                stack = [root['id']]
                while stack:
                    ID = stack.pop()
                    refset.append(markables[ID])
                    if ID in forward_refs:
                        stack.extend(forward_refs[ID])
                sets.append(refset)
        if markables and not any(sets):
            raise ValueError("You lost all your markables!")
        if self.validate:
            input_total = len(markables)
            output_total = sum(map(len, sets))
            if output_total != input_total:
                out_ids = set(m['id'] for refset in sets for m in refset)
                in_ids = set(markables)
                missing = in_ids - out_ids
                raise ValidationError(
                    f"Expected {input_total} markables in output, found:"
                    f" {output_total}. Missing markable IDs: {sorted(missing)}"
                )
        return sets
