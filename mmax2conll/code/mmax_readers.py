import re
import logging
from os import path
import itertools as it

from . import constants as c
from .util import ValidationError

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def document_ID_from_filename(filename):
    """
    Extract the document ID (or None) from the filename of a file from the
    COREA corpus.

    !! NB !! This method is hard-coded for the COREA corpus and
             only works for the DCOI and Med parts of the corpus.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """
    bare_doc_id = path.basename(filename)[:-len('_words.xml')]
    if bare_doc_id.startswith('s'):
        return c.COREA_MED_ID + '/' + bare_doc_id
    elif bare_doc_id.startswith('WR-P-P-H-'):
        return c.COREA_DCOI_ID + '/' + bare_doc_id
    return None


class CoreaMedWordReader:
    """
    Reads data from an ElementTree Element from a document from the Med part of
    the COREA corpus.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """

    def __init__(self, word_number_attr=c.COREA_MED_WORD_NUMBER_ATTRIBUTE):
        self.word_number_attr = word_number_attr

    @staticmethod
    def extract_word(xml):
        """
        Extract the word from an XML-element.
        """
        return xml.text

    def extract_word_number(self, xml):
        """
        Extract the word number **as a string** from an XML-element.
        """
        return xml.attrib[self.word_number_attr]

    def read(self, xml):
        """
        Extract a dictionary with information about a word from an XML-element.

        The dictionary contains `word_number` and `word`.
        """
        return {
            'word_number': self.extract_word_number(xml),
            'word': self.extract_word(xml),
        }


class MMAXWordReader(CoreaMedWordReader):
    """
    Reads data from an ElementTree Element from a document in MMAX format.

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """
    PART_NUMBER_REGEX = re.compile(r'WR-P-P-H-\d+\.p\.(\d+)\.s\.\d+\.xml')

    def __init__(self,
                 word_number_attr=c.MMAX_WORD_NUMBER_ATTRIBUTE,
                 part_number_attr=c.MMAX_PART_NUMBER_ATTRIBUTE):
        super(MMAXWordReader, self).__init__(word_number_attr)
        self.part_number_attr = part_number_attr

    def extract_part_number(self, xml):
        """
        Extract the part number **as a string** from an XML-element.

        Return `None` if it cannot be extracted

        !! NB !! This method is hard-coded for the COREA corpus and only
                 returns a part number for the DCOI part of the corpus.

        See Ch. 7 of Essential Speech and Language Technology for Dutch
        COREA: Coreference Resolution for Extracting Answers for Dutch
        https://link.springer.com/book/10.1007/978-3-642-30910-6
        """
        if self.part_number_attr in xml.attrib:
            part_text = xml.attrib[self.part_number_attr]
            match = self.PART_NUMBER_REGEX.match(part_text)
            if match is not None:
                return match.group(1)
        return None

    def read(self, xml):
        """
        Extract a dictionary with information about a word from an XML-element.

        The dictionary contains `word_number` and `word`.
        """
        dic = super(MMAXWordReader, self).read(xml)
        dic.update(
            part_number=self.extract_part_number(xml)
        )
        return dic


class MMAXWordsDocumentReader:
    """
    Reads and (optionally) validates data from a MMAX words XML-tree.

    Things that are verified if `validate=True`:
     - the tag of the root element is as expected
     - the tag of all the word elements is as expected
     - the word numbers are consistent

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, word_reader=None,
                 validate=c.VALIDATE_XML,
                 document_id_attr=c.MMAX_WORDS_DOCUMENT_ID_ATTRIBUTE,
                 sent_start_word_number=c.MMAX_SENTENCE_STARTING_WORD_NUMBER,
                 expected_word_tag=c.MMAX_WORD_TAG,
                 expected_root_tag=c.MMAX_WORDS_TAG):
        self.word_reader = word_reader \
            if word_reader is not None \
            else MMAXWordReader()
        self.validate = validate
        self.document_id_attr = document_id_attr
        self.sent_start_word_number = sent_start_word_number
        self.expected_word_tag = expected_word_tag
        self.expected_root_tag = expected_root_tag

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

    def get_word_elements(self, xml):
        """
        Get the XML-elements of the words and validate:
         - the tag of the root element
         - the tag of the word elements
        """
        root = xml.getroot()
        if self.validate and not root.tag == self.expected_root_tag:
            raise ValidationError(
                f"The root element did not have the expected tag"
                f" {self.expected_root_tag!r}. Found: {root.tag!r}"
            )

        children = root.getchildren()
        if self.validate:
            for child in children:
                if child.tag != self.expected_word_tag:
                    raise ValidationError(
                        f"One of the children did not have the expected tag"
                        f" {self.expected_word_tag!r}. Found: {child.tag!r}"
                    )
        return children

    def extract_words(self, xml):
        """
        Extract all information for every word.

        Returns a list of things returned by `self.word_reader.read`
        """
        return [
            self.word_reader.read(word_element)
            for word_element in self.get_word_elements(xml)
        ]

    def extract_sentences(self, xml):
        """
        Extract all sentences and validate them.

        Returns a list of sentences, where a sentence is a list of things
        returned by `self.word_reader.read`.
        """
        words = iter(self.extract_words(xml))
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
                            )
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

    @staticmethod
    def validate_sentences(sentences):
        """
        Validate `word_number` and `part_number` of these sentences
        """
        MMAXWordsDocumentReader.validate_word_number(sentences)
        MMAXWordsDocumentReader.validate_part_number(sentences)

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
                except ValueError:
                    raise ValidationError(
                        f"The part number of {word['word']!r} is not a"
                        f" number but {word['part_number']!r}."
                        f" This is in sentence #{senti}: {sentence!r}."
                    )
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
                            )
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
