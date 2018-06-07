import logging

from . import constants as c

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


class CoNLLWriter:
    """
    Write data in CoNLL format.

    !! NB !! No support for predicate arguments (Columns 12:N)

    # CoNLL Format
    [This page][CoNLL-2012] contains the CoNLL file format description.

    Every part (see column two) starts with
    `#begin document ([document ID]); part [number (0-padded to 3 digits)]`
    and ends with `#end document`. Every sentence is followed by an empty line.
    The columns are aligned per sentence and can differ between sentences,
    because of the predicate arguments.
    Columns are right aligned.

    Column  | Type                    | Description
    -------:|-------------------------|----------
    1       | Document ID             | This is a variation on the document
                                        filename. Mostly it's the path of the
                                        file without the extension.
    2       | Part number             | Some files are divided into multiple
                                        parts numbered as 000, 001, 002, etc.
    3       | Word number             | 0-based word number **of the sentence**
    4       | Word itself
    5       | Part-of-Speech
    6       | Parse bit               | The structure of the constituency tree.
                                        This field is the bracketed structure
                                        broken before the first open
                                        parenthesis in the parse, and the
                                        word/part-of-speech leaf replaced with
                                        a `*`. The full parse can be created by
                                        substituting the asterix with the
                                        `([pos] [word])` string (or leaf) and
                                        concatenating the items in the rows of
                                        that column (= concatenate this column
                                        for all the rows (of the tokens) that
                                        are part of the same sentence). \[1\]
    7       | Predicate lemma         | The predicate lemma is mentioned for
                                        the rows for which we have semantic
                                        role information. All other rows are
                                        marked with a `-`.
    8       | Predicate Frameset ID   | PropBank frameset ID of the predicate
                                        in Column 7.
    9       | Word sense              | Word sense of the word in Column 3.
    10      | Speaker/Author          | Speaker or author name where available.
                                        Mostly in Broadcast Conversation and
                                        Web Log data.
    11      | Named Entities          | Identifies the spans representing
                                        various named entities.
    12:N    | Predicate Arguments     | There is one column each of predicate
                                        argument structure information for the
                                        predicate mentioned in Column 7. I.E.
                                        the arguments for the predicate first
                                        mentioned in Column 7 can be found in
                                        Column 12, those for the second
                                        predicate in Column 7 can be found in
                                        Column 13, etc. If the sentence
                                        contains no predicates, these columns
                                        are left out entirely, i.e. `N = 12`.
    N       | Coreference             | Coreference chain information encoded
                                        in a parenthesis structure. The
                                        parentheses mark a span of text and the
                                        number is the (arbitrary) id of the
                                        referred entity.

    \[1\] i.e.
    ```
    for newline delimited block as sentence in file:
        for row in sentence:
            replace `*` with `(<pos> <word>)`
        parse = join(column 6 of row for row in sentence)
    ```

    [CoNLL-2012]: http://conll.cemantix.org/2012/data.html
    [LDC2011T03]: https://catalog.ldc.upenn.edu/LDC2011T03

    """

    def __init__(self, defaults=c.CONLL_DEFAULTS,
                 min_column_spacing=c.MIN_COLUMN_SPACING,
                 on_missing=c.CONLL_ON_MISSING,
                 columns=c.CONLL_COLUMNS):
        self.min_column_spacing = min_column_spacing
        self.defaults = defaults
        self.on_missing = on_missing
        self.columns = columns

    def write(self, writeable, document_id, sentences):
        """
        Write sentences to a writeable in CoNLL format.

        Take the specified action when something is missing.

        Enforces `part_number` to be a number and to be increasing.
        Assumes all words in a sentence have the same `part_number`.
        Does not validate any other values.
        """
        prev_part = 0
        self.write_part_start(writeable, document_id, prev_part)
        for sentence in sentences:
            current_part = sentence[0].get(
                'part_number',
                None
            ) if sentence else None
            if current_part is None:
                current_part = self.defaults['part_number']
            try:
                current_part = int(current_part)
            except ValueError as e:
                raise ValueError(
                    f"The part number should be a number in : {sentence}"
                ) from e

            if prev_part != current_part:
                if prev_part > current_part:
                    raise ValueError(
                        "The part number should be a increasing in:"
                        f" {sentence}"
                    )
                while prev_part != current_part:
                    # First end the previous part
                    self.write_part_end(writeable)
                    prev_part += 1
                    # Now start the new part
                    self.write_part_start(writeable, document_id, prev_part)

            self.write_sentence(writeable, document_id, sentence)

        self.write_part_end(writeable)

    @staticmethod
    def write_part_start(writeable, document_id, part_number):
        """
        Write the head of a new part
        """
        writeable.write(
            f'#begin document ({document_id}); part {part_number:0>3}\n'
        )

    @staticmethod
    def write_part_end(writeable):
        """
        Write the foot of a finished part
        """
        writeable.write('#end document\n')

    def write_sentence(self, writeable, document_id, sentence):
        """
        Write a sentence

        Take the specified action when something is missing.
        """
        self.clean_sentence(sentence)
        column_sizes = self.get_column_sizes(sentence)
        for word in sentence:
            self.write_word(writeable, document_id, word, column_sizes)
        # Sentences are delimited by a newline.
        writeable.write('\n')

    def write_word(self, writeable, document_id, word, column_sizes):
        """
        Write a row for a word

        Always raises an exception if something is missing.
        """
        writeable.write(document_id)
        for column in self.columns:
            writeable.write(self.min_column_spacing * ' ')
            value = word[column]
            writeable.write((column_sizes[column] - len(value)) * ' ')
            writeable.write(value)
        writeable.write('\n')

    def clean_sentence(self, sentence):
        """
        Make sure all columns are present in all words of the sentence and
        all values are strings.

        Changes the sentence in place!
        Complains according to self.on_missing if data is missing.
        """
        self.add_missing_data_to_sentence(sentence)
        self.convert_values_to_string(sentence)

    def convert_values_to_string(self, sentence):
        """
        Make sure all values are strings.

        Changes the sentence in place!
        """
        for word in sentence:
            for column in self.columns:
                value = word[column]
                word[column] = str(value) if value is not None else ''

    def add_missing_data_to_sentence(self, sentence):
        """
        Make sure all columns are present in all words of the sentence.

        Changes the sentence in place!
        Complains according to self.on_missing if data is missing.
        """
        for column in self.columns:
            on_missing = self.on_missing[column]
            if on_missing == 'nothing':
                default = self.defaults[column]
                for word in sentence:
                    if word.get(column, None) is None:
                        word[column] = default
            elif on_missing == 'warn':
                default = self.defaults[column]
                for word in sentence:
                    if word.get(column, None) is None:
                        word[column] = default
                        logger.warn(self.get_missing_message(column, word))
            elif on_missing == 'throw':
                for word in sentence:
                    if word.get(column, None) is None:
                        raise ValueError(
                            self.get_missing_message(column, word)
                        )
            else:
                raise ValueError(
                    f"`on_missing` should be either 'nothing', 'warn' or"
                    f" 'throw', but `on_missing[{column!r}]` is {on_missing!r}"
                )

    @staticmethod
    def get_missing_message(column, word):
        """
        Get the message for when an item is missing
        """
        return f"The column {column!r} is missing from the word: {word!r}"

    def get_column_sizes(self, sentence):
        """
        Calculate the size of the columns for this sentence
        """
        return {
            column: self.get_max_length(
                word[column] for word in sentence
            )
            for column in self.columns
        }

    @staticmethod
    def get_max_length(iterable):
        """
        Get the length of the largest element
        """
        return max(len(s) for s in iterable)
