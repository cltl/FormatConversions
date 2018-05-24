#! /usr/bin/env python3

# output to CoNLL file in blocks

# - the input files exist and the output files don't,
#   or overwriting is enabled in the config

import logging

from lxml import etree

import constants as c
from mmax_readers import (
    document_ID_from_filename,
    MMAXWordsDocumentReader,
    CoreaMedWordReader,
)
from conll_writers import CoNLLWriter

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def main(input_file, output_file,
         validate_xml=c.VALIDATE_XML,
         allow_missing_document_ID=c.ALLOW_MISSING_DOCUMENT_ID,
         auto_use_Med_word_reader=c.AUTO_USE_MED_WORD_READER,
         defaults=c.CONLL_DEFAULTS,
         min_column_spacing=c.MIN_COLUMN_SPACING,
         on_missing=c.CONLL_ON_MISSING):
    # Read in the data from MMAX
    document_id, sentences = read_words_file(
        input_file,
        MMAXWordsDocumentReader(validate=validate_xml),
        allow_missing_document_ID,
        auto_use_Med_word_reader
    )

    # Save the data to CoNLL
    write_conll(
        output_file,
        CoNLLWriter(
            defaults=defaults,
            min_column_spacing=min_column_spacing,
            on_missing=on_missing
        ),
        document_id,
        sentences
    )


def read_words_file(filename, reader,
                    allow_missing_document_ID=c.ALLOW_MISSING_DOCUMENT_ID,
                    auto_use_Med_word_reader=c.AUTO_USE_MED_WORD_READER):
    """
    Read in word and sentence data and a document ID from a file from COREA.

    First tries to figure out the document ID using the xml and falls back
    on finding a document ID using the file basename.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """
    xml = etree.parse(filename)

    document_id = reader.extract_document_ID(xml)
    if document_id is None:
        document_id = document_ID_from_filename(filename)
    if document_id is None:
        message = "No document ID could be found."
        if allow_missing_document_ID:
            logger.warn(message)
        else:
            raise ValueError(message)
    logger.debug(f"auto_use_Med_word_reader: {auto_use_Med_word_reader}")
    logger.debug(f"document_id: {document_id}")
    if auto_use_Med_word_reader and document_id.startswith(c.COREA_MED_ID):
        logger.warn("Ignoring reader.word_reader and automatically using the"
                    " word reader for COREA Med")
        reader.word_reader = CoreaMedWordReader()

    sentences = reader.extract_sentences(xml)
    return document_id, sentences


def write_conll(filename, writer, document_id, sentences):
    """
    Write sentence data to a file in CoNLL format.

    !! NB !! Does not write coreference data
    """
    with open(filename, 'w') as fd:
        writer.write(fd, document_id, sentences)


if __name__ == '__main__':
    from argparse import ArgumentParser
    from pyaml import yaml
    ARGS_FROM_CONFIG = [
        'validate_xml',
        'allow_missing_document_ID',
        'auto_use_Med_word_reader',
        'min_column_spacing',
        'defaults',
        'on_missing',
    ]

    parser = ArgumentParser()
    parser.add_argument('-l', '--log-level', default='INFO',
                        help="Logging level")
    parser.add_argument('-c', '--config', default=c.DEFAULT_CONFIG_FILE,
                        help="YAML configuration file")
    parser.add_argument('input_file',
                        help="MMAX *_words.xml file to use as input")
    parser.add_argument('output_file', help="where to save the CoNLL output")
    args = vars(parser.parse_args())

    logging.basicConfig(level=args.pop('log_level'))

    config_file = args.pop('config')
    with open(config_file) as config_fd:
        config = yaml.load(config_fd)

    for arg in ARGS_FROM_CONFIG:
        if arg not in config:
            raise ValueError(
                f"The key {arg!r} is not in the specified configuration file"
                f" {config_file}"
            )
        args[arg] = config[arg]

    main(**args)
