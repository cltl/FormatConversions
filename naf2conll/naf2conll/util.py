import os
import re
from argparse import ArgumentTypeError

from . import constants as c


class ValidationError(ValueError):
    pass


def file_exists(filename):
    """
    Ensure a path exists

    Raise ArgumentTypeError if it doesn't.
    """
    if not os.path.exists(filename):
        raise ArgumentTypeError(f"No such file: {filename}")
    return filename


def directory_exists(dirname):
    """
    Ensure a path exists and that it has a trailing slash

    Raise ArgumentTypeError if it doesn't.
    """
    return os.path.join(file_exists(dirname), '')


def document_ID_from_filename(filename, extension):
    """
    Extract the document ID (or None) from the base name of a file.

    !! NB !! Special case for Med adds `Med/` to the base name

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """
    basename = os.path.basename(filename)
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


def split_on_numbering(sequence, get_number, validate=c.VALIDATE,
                       start_number=0):
    """
    Split a sequence into subsequences using the number returned by
    `get_number(element)`.

    If `validate` is truthy, the following is validated:
     - `get_number(first_element)` is `start_number`
     - `get_number(element)` is equal to or exactly one greater than
       `get_number(previous_element)`
    """
    current_inner = []
    new_outer = [current_inner]
    sequence = iter(sequence)
    try:
        current_inner.append(next(sequence))
    except StopIteration:
        return []
    prev_number = get_number(current_inner[0])
    if validate and prev_number != start_number:
        raise ValidationError(
            "The first number of the sequence must be `start_number`"
            f" ({start_number}), found: {prev_number}"
        )

    for element in sequence:
        current_number = get_number(element)
        if current_number != prev_number:
            if validate and current_number != prev_number + 1:
                raise ValidationError(
                    f"The number of an element ({current_number}) must either"
                    " be equal to, or exactly one greater than the number of"
                    f" the previous element ({prev_number})."
                )
            current_inner = []
            new_outer.append(current_inner)
        current_inner.append(element)
        prev_number = current_number

    return new_outer
