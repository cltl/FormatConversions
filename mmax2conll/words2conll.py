#! /usr/bin/env python3

# output to CoNLL file in blocks

# - the input files exist and the output files don't,
#   or overwriting is enabled in the config

import logging

from lxml import etree

import constants as c
from mmax_readers import (
    MMAXWordsDocumentReader,
    document_ID_from_filename
)

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def main(input_file, output_file, reader=MMAXWordsDocumentReader(),
         validate_xml=c.VALIDATE_XML,
         allow_missing_document_ID=c.ALLOW_MISSING_DOCUMENT_ID,
         default_document_id=c.DEFAULT_DOCUMENT_ID):
    # Read in the data from MMAX
    document_id, sentences = read_words_file(
        input_file,
        reader,
        validate_xml,
        allow_missing_document_ID,
        default_document_id
    )

    # Save the data to CoNLL
    for sentence in sentences:
        print(sentence)
    print(document_id)


def read_words_file(input_file, reader=MMAXWordsDocumentReader(),
                    validate_xml=c.VALIDATE_XML,
                    allow_missing_document_ID=c.ALLOW_MISSING_DOCUMENT_ID,
                    default_document_id=c.DEFAULT_DOCUMENT_ID):
    """
    Read in word and sentence data and a document ID from a file from COREA.

    First tries to figure out the document ID using the xml and falls back
    on finding a document ID using the file basename.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """
    xml = etree.parse(input_file)
    sentences = reader.extract_sentences(xml)

    document_id = reader.extract_document_ID(xml)
    if document_id is None:
        document_id = document_ID_from_filename(input_file)
    if document_id is None:
        message = "No document ID could be found."
        if allow_missing_document_ID:
            logger.warn(message)
            document_id = default_document_id
        else:
            raise ValueError(message)
    return document_id, sentences


if __name__ == '__main__':
    from argparse import ArgumentParser
    from pyaml import yaml
    ARGS_FROM_CONFIG = [
        'validate_xml',
        'allow_missing_document_ID',
        'default_document_id'
    ]

    parser = ArgumentParser()
    parser.add_argument('-c', '--config', default=c.DEFAULT_CONFIG_FILE,
                        help="YAML configuration file")
    parser.add_argument('input_file',
                        help="MMAX *_words.xml file to use as input")
    parser.add_argument('output_file', help="where to save the CoNLL output")
    args = parser.parse_args()

    config_file = vars(args).pop('config')
    with open(config_file) as config_fd:
        config = yaml.load(config_fd)

    for arg in ARGS_FROM_CONFIG:
        if arg not in config:
            raise ValueError(
                f"The key {arg!r} is not in the specified configuration file"
                f" {config_file}"
            )
        setattr(args, arg, config[arg])

    main(**vars(args))
