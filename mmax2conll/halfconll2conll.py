#! /usr/bin/env python3

import logging
import os

from lxml import etree

import code.constants as c
from code.util import file_exists

from code.mmax_readers import MMAXMarkablesDocumentReader
from code.conll_writers import CoNLLWriter

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def main(input_file, output_file,
         validate_xml=c.VALIDATE_XML,
         defaults=c.CONLL_DEFAULTS,
         min_column_spacing=c.MIN_COLUMN_SPACING,
         on_missing=c.CONLL_ON_MISSING):
    # Read in the data from MMAX
    nothing = read_markables_file(
        filename=input_file,
        reader=MMAXMarkablesDocumentReader(validate=validate_xml),
    )

    # Save the data to CoNLL
    write_conll(
        filename=output_file,
        writer=CoNLLWriter(
            defaults=defaults,
            min_column_spacing=min_column_spacing,
            on_missing=on_missing
        ),
        document_id='UNKNWON',
        sentences=nothing
    )


def read_markables_file(filename, reader):
    """
    Read in coreference data from a file from COREA.

    See Ch. 7 of Essential Speech and Language Technology for Dutch
    COREA: Coreference Resolution for Extracting Answers for Dutch
    https://link.springer.com/book/10.1007/978-3-642-30910-6
    """
    xml = etree.parse(filename)

    items = reader.extract_items(xml)
    for item in items:
        print(item)
    return None


def write_conll(filename, writer, document_id, sentences):
    """
    Write sentence data to a file in CoNLL format.
    """
    with open(filename, 'w') as fd:
        writer.write(fd, document_id, sentences)


if __name__ == '__main__':
    from argparse import ArgumentParser
    from pyaml import yaml
    ARGS_FROM_CONFIG = [
        'validate_xml',
        'min_column_spacing',
        'defaults',
        'on_missing',
    ]

    # Read command line arguments
    parser = ArgumentParser()
    parser.add_argument('-l', '--log-level', default='INFO',
                        help="Logging level")
    parser.add_argument('-c', '--config', default=c.DEFAULT_CONFIG_FILE,
                        help="YAML configuration file")
    parser.add_argument('input_file', type=file_exists,
                        help="MMAX *_coref_level.xml file to use as input")
    # parser.add_argument('halfconll_file', type=file_exists,
    #                     help="*.halfconll file to use as input")
    parser.add_argument('output_file', help="where to save the CoNLL output")
    args = vars(parser.parse_args())

    # Set the logging level
    logging.basicConfig(level=args.pop('log_level'))

    # Read the configuration file
    config_file = args.pop('config')
    with open(config_file) as config_fd:
        config = yaml.load(config_fd)

    # Verify the output file is legal
    output_file = args['output_file']
    if os.path.exists(output_file):
        if not config['allow_overwriting']:
            raise ValueError(
                "The configuration specifies overwriting is not allowed, but"
                f" the output file already exists: {output_file}"
            )
    else:
        # Check if we can create it
        open(output_file, 'w').close()
        # Remove it
        os.remove(output_file)

    # Extract required arguments from configuration
    for arg in ARGS_FROM_CONFIG:
        if arg not in config:
            raise ValueError(
                f"The key {arg!r} is not in the specified configuration file"
                f" {config_file}"
            )
        args[arg] = config[arg]

    # Run the program
    main(**args)
    logger.info("Done!")
