import re

from . import constants as c


class SoNaRWordReader:
    """
    Reads data from an ElementTree Element from a document from the SoNaR-1
    corpus.

    See
    https://ivdnt.org/downloads/taalmaterialen/tstc-sonar-corpus
    for (a description of) the SoNaR Corpus

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, id_attr=c.MMAX_WORD_ID_ATTRIBUTE):
        self.id_attr = id_attr

    @staticmethod
    def extract_word(xml):
        """
        Extract the word from an XML-element.
        """
        return xml.text

    def extract_id(self, xml):
        """
        Extract the word ID **as a string** from an XML-element.
        """
        return xml.attrib.get(self.id_attr, None)

    def read(self, xml):
        """
        Extract a dictionary with information about a word from an XML-element.

        The dictionary contains `word` and `id`.
        """
        return {
            'word': self.extract_word(xml),
            'id': self.extract_id(xml)
        }


class COREAMedWordReader(SoNaRWordReader):
    """
    Reads data from an ElementTree Element from a document from the Med part of
    the COREA corpus.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """

    def __init__(self, id_attr=c.MMAX_WORD_ID_ATTRIBUTE,
                 word_number_attr=c.COREA_MED_WORD_NUMBER_ATTRIBUTE):
        self.id_attr = id_attr
        self.word_number_attr = word_number_attr

    def extract_word_number(self, xml):
        """
        Extract the word number **as a string** from an XML-element.
        """
        return xml.attrib.get(self.word_number_attr, None)

    def read(self, xml):
        """
        Extract a dictionary with information about a word from an XML-element.

        The dictionary contains `word`, `id` and `word_number`.
        """
        dic = super(COREAMedWordReader, self).read(xml)
        dic.update(
            word_number=self.extract_word_number(xml)
        )
        return dic


class COREAWordReader(COREAMedWordReader):
    """
    Reads data from an ElementTree Element from a MMAX words document from the
    COREA Corpus.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """
    PART_NUMBER_REGEX = re.compile(
        r'WR-P-P-H-\d+\.p\.(\d+)\.s\.\d+(.\d+)?\.xml'
    )

    def __init__(self,
                 id_attr=c.MMAX_WORD_ID_ATTRIBUTE,
                 word_number_attr=c.MMAX_WORD_NUMBER_ATTRIBUTE,
                 part_number_attr=c.MMAX_PART_NUMBER_ATTRIBUTE):
        super(COREAWordReader, self).__init__(id_attr, word_number_attr)
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

        The dictionary contains `word`, `id`, `word_number` and 'part_number'.
        """
        dic = super(COREAWordReader, self).read(xml)
        dic.update(
            part_number=self.extract_part_number(xml)
        )
        return dic


class MMAXMarkableReader:
    """
    Reads data from an ElementTree Element from a MMAX markables document.

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """
    def __init__(self,
                 referred_ids,
                 id_attr=c.MMAX_MARKABLE_ID_ATTRIBUTE,
                 span_attr=c.MMAX_SPAN_ATTRIBUTE,
                 mmax_level_attr=c.MMAX_LEVEL_ATTRIBUTE):
        self.referred_ids = list(referred_ids)
        self.referred_indices = dict(
            (ID, i) for i, ID in enumerate(self.referred_ids)
        )
        self.id_attr = id_attr
        self.span_attr = span_attr
        self.mmax_level_attr = mmax_level_attr

    def extract_id(self, xml):
        """
        Extract the markable id from an XML-element.
        """
        return xml.attrib.get(self.id_attr, None)

    def extract_span(self, xml):
        """
        Extract the span from an XML-element.
        """
        span_text = xml.attrib.get(self.span_attr, None)
        return self.span_from_text(span_text)

    def span_from_text(self, text):
        """
        Expand and split a possibly abbreviated span specification:
            span="word_1..word_5,word_7"
        """
        parts = []
        for part in text.split(','):
            split = part.split('..')

            if len(split) > 1:
                if len(split) != 2:
                    raise ValueError(
                        "Illegal span specification: only one '..' is allowed:"
                        f" between every pair of ',': {text!r}")
                first, last = map(self.referred_indices.get, split)

                if first is None:
                    raise ValueError(
                        f"Unknown ID ({split[0]!r}) in span: {text!r}"
                    )
                if last is None:
                    raise ValueError(
                        f"Unknown ID ({split[1]!r}) in span: {text!r}"
                    )

                if first > last:
                    raise ValueError(
                        "Illegal span specification: the first ID of a span"
                        " abbreviation must appear in the words before the"
                        f" second ID: {text}"
                    )
                new_parts = self.referred_ids[first:last + 1]
            else:
                new_parts = split
            parts.extend(new_parts)
        return parts

    def extract_mmax_level(self, xml):
        """
        Extract the annotation level from an XML-element.
        """
        return xml.attrib.get(self.mmax_level_attr, None)

    def read(self, xml):
        """
        Extract a dictionary with information about a markable from an
        XML-element.

        The dictionary contains 'id', 'span' and 'mmax_level'.
        """
        return {
            'id': self.extract_id(xml),
            'span': self.extract_span(xml),
            'mmax_level': self.extract_mmax_level(xml),
        }


class MMAXCorefReader(MMAXMarkableReader):
    """
    Reads data from an ElementTree Element from a MMAX markables coreference
    document.

    See `MMAX-specification.md` and
    http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
    for a description of the MMAX format.
    """
    def __init__(self,
                 referred_ids,
                 head_attr=c.COREF_HEAD_ATTRIBUTE,
                 ref_attr=c.COREF_REF_ATTRIBUTE,
                 type_attr=c.COREF_TYPE_ATTRIBUTE,
                 level_attr=c.COREF_LEVEL_ATTRIBUTE,
                 time_attr=c.COREF_TIME_ATTRIBUTE,
                 mod_attr=c.COREF_MOD_ATTRIBUTE,
                 **kwargs):
        super(MMAXCorefReader, self).__init__(referred_ids, **kwargs)
        self.head_attr = head_attr
        self.ref_attr = ref_attr
        self.level_attr = level_attr
        self.type_attr = type_attr
        self.time_attr = time_attr
        self.mod_attr = mod_attr

    def extract_head(self, xml):
        """
        Extract the head from an XML-element.
        """
        return xml.attrib.get(self.head_attr, None)

    def extract_ref(self, xml):
        """
        Extract the referred markable id from an XML-element.

        Return None if the attribute does not exist.
        """
        return xml.attrib.get(self.ref_attr, None)

    def extract_level(self, xml):
        """
        Extract the reference level from an XML-element.
        """
        return xml.attrib.get(self.level_attr, None)

    def extract_type(self, xml):
        """
        Extract the reference type from an XML-element.
        """
        return xml.attrib.get(self.type_attr, None)

    def extract_time(self, xml):
        """
        Extract the time from an XML-element.
        """
        return xml.attrib.get(self.time_attr, None)

    def extract_mod(self, xml):
        """
        Extract the 'mod' attribute from an XML-element.
        """
        return xml.attrib.get(self.mod_attr, None)

    def read(self, xml):
        """
        Extract a dictionary with information about a coreference from an
        XML-element.

        The dictionary contains everything returned by MMAXMarkableReader.read
        and 'head'. If `self.extract_mod(xml) is not None` the dictionary also
        contains 'ref', 'level', 'type', 'time' and 'mod'.
        """
        dic = super(MMAXCorefReader, self).read(xml)
        dic.update(
            head=self.extract_head(xml)
        )
        ref = self.extract_ref(xml)
        if ref is not None:
            dic.update(
                ref=ref,
                level=self.extract_level(xml),
                type=self.extract_type(xml),
                time=self.extract_time(xml),
                mod=self.extract_mod(xml)
            )
        return dic
