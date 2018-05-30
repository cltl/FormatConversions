#! /usr/bin/env python3

import logging
import os

from lxml import etree

import code.constants as c
from code.util import file_exists

from code.mmax_readers import (
    document_ID_from_filename,
    MMAXWordsDocumentReader,
    MMAXMarkablesDocumentReader,
    CoreaMedWordReader,
)
from code.conll_converters import CorefConverter
from code.conll_writers import CoNLLWriter

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def main(words_file, coref_file, output_file,
         validate_xml=c.VALIDATE_XML,
         auto_use_Med_item_reader=c.AUTO_USE_MED_ITEM_READER,
         defaults=c.CONLL_DEFAULTS,
         min_column_spacing=c.MIN_COLUMN_SPACING,
         on_missing=c.CONLL_ON_MISSING,
         markables_filter=c.MMAX_MARKABLES_FILTER):
    # Read in the data from MMAX *_words.xml file
    document_id, sentences = read_words_file(
        filename=words_file,
        reader=MMAXWordsDocumentReader(validate=validate_xml),
        on_missing_document_ID=on_missing['document_id'],
        auto_use_Med_item_reader=auto_use_Med_item_reader
    )

    # Read in coreference data
    coref_sets = MMAXMarkablesDocumentReader(
        validate=validate_xml,
        item_filter=markables_filter,
    ).extract_coref_sets(
        etree.parse(coref_file)
    )

    # Merge coref data into sentences (in place)
    CorefConverter.add_data_from_coref_sets(sentences, coref_sets)

    # Save the data to CoNLL
    write_conll(
        filename=output_file,
        writer=CoNLLWriter(
            defaults=defaults,
            min_column_spacing=min_column_spacing,
            on_missing=on_missing
        ),
        document_id=document_id,
        sentences=sentences
    )


def read_words_file(filename, reader,
                    on_missing_document_ID=c.CONLL_ON_MISSING['document_id'],
                    auto_use_Med_item_reader=c.AUTO_USE_MED_ITEM_READER):
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

    message = "No document ID could be found."
    if on_missing_document_ID == 'warn':
        if document_id is None:
            logger.warn(message)
    elif on_missing_document_ID == 'throw':
        if document_id is None:
            logger.warn(message)
    elif on_missing_document_ID != 'nothing':
        raise ValueError(
                "`on_missing` should be either 'nothing', 'warn' or 'throw',"
                " but `on_missing['document_id']` is"
                f" {on_missing_document_ID!r}"
            )

    logger.debug(f"auto_use_Med_item_reader: {auto_use_Med_item_reader}")
    logger.debug(f"document_id: {document_id}")
    if auto_use_Med_item_reader and document_id.startswith(c.COREA_MED_ID):
        logger.warn("Ignoring reader.item_reader and automatically using the"
                    " item reader for COREA Med")
        reader.item_reader = CoreaMedWordReader()

    sentences = reader.extract_sentences(xml)
    return document_id, sentences


def write_conll(filename, writer, document_id, sentences):
    """
    Write sentence data to a file in CoNLL format.
    """
    with open(filename, 'w') as fd:
        writer.write(fd, document_id, sentences)


def can_output_to(output, config, batch):
    if os.path.exists(output):
        if not config['allow_overwriting']:
            thing = "folder" if batch else "file"
            raise ValueError(
                "The configuration specifies overwriting is not allowed, but"
                f" the output {thing} already exists: {output}"
            )
    else:
        # (Check if we can) create it
        if batch:
            os.makedirs(output)
        else:
            open(output, 'w').close()
            # Remove it, because if something goes wrong empty files are more
            # annoying than empty directories
            os.remove(output)


def get_args(args_from_config=[
                 'validate_xml',
                 'auto_use_Med_item_reader',
                 'min_column_spacing',
                 'defaults',
                 'on_missing',
             ]):
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    from pyaml import yaml

    # Read command line arguments
    parser = ArgumentParser(
        description="""
Script to convert coreference data in MMAX format to CoNLL format.

See `CoNLL-specification.md` and `MMAX-specification.md` for extensive
descriptions of the CoNLL and MMAX formats.

To convert a whole directory recursively, run:

    mmax2conll.py <output folder> -d <input folder> [-d <input folder> ...]


To only convert one pair of files, run:

    mmax2conll.py <output.conll> <*_words.xml> <*_coref_level.xml>


When passing folders for batch processing using -d, the passed folders are
searched for a folder containing both a `Basedata` and `Markables` folder. The
output is saved in using the same path relative to the output folder as the
original folder has relative to the passed folder it was found in.

!! NB !! This means that the data of two folders is merged if they happen
         to have the same path relative to passed folders. No files will be
         overwritten if overwriting isn't allowed in the configuration. If
         is allowed according to the configuration, a warning will be issued.

""",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument('-l', '--log-level', default='INFO',
                        help="Logging level")
    parser.add_argument('-c', '--config', default=c.DEFAULT_CONFIG_FILE,
                        help="YAML configuration file")
    parser.add_argument('-d', '--directory', action='append',
                        help="Directory to batch convert files from")
    parser.add_argument('output',
                        help="Where to save the CoNLL output")
    parser.add_argument('words_file', type=file_exists, nargs='?',
                        help="MMAX *_words.xml file to use as input")
    parser.add_argument('coref_file', type=file_exists, nargs='?',
                        help="MMAX *_coref_level.xml file to use as input")
    args = vars(parser.parse_args())

    # Set the logging level
    logging.basicConfig(level=args.pop('log_level'))
    logger.debug(f"Args: {args}")

    # Read the configuration file
    config_file = args.pop('config')
    with open(config_file) as config_fd:
        config = yaml.load(config_fd)

    # Extract required arguments from configuration
    for arg in args_from_config:
        if arg not in config:
            raise ValueError(
                f"The key {arg!r} is not in the specified configuration file"
                f" {config_file}"
            )
        args[arg] = config[arg]

    args['markables_filter'] = lambda i: \
        c.MMAX_TYPE_FILTERS[config['markables_type_filter']](i) and \
        c.MMAX_LEVEL_FILTERS[config['markables_level_filter']](i)

    batch = bool(args['directory'])
    output = args.pop('output')

    # Verify that the command line arguments are legal
    # AND remove the ones not needed
    if batch:
        args['output_dir'] = output
        if args.pop('words_file') is not None or \
           args.pop('coref_file') is not None:
            parser.error(
                "Please either specify a number of directories or the"
                " necessary files to use as input, but not both."
            )
    else:
        del args['directory']
        args['output_file'] = output
        if args['words_file'] is None or args['coref_file'] is None:
            parser.error(
                "Please specify both a *_words.xml file and a"
                " *_coref_level.xml file. You can also choose to specify a"
                " number directories to use as input instead."
            )

    # Verify the output location
    can_output_to(output, config, batch)

    return batch, args


if __name__ == '__main__':
    batch, args = get_args()
    if batch:
        for directory in args.pop('directory'):
            ...
    else:
        main(**args)
    logger.info("Done!")
