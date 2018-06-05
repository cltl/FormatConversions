#! /usr/bin/env python3

import os
import logging

from lxml import etree

import code.constants as c
from code.util import file_exists, directory_exists

from code.mmax_document_readers import (
    SoNaRWordsDocumentReader,
)

from mmax2conll import Main as CoNLLMain

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


class Main(CoNLLMain):
    @classmethod
    def dir_main(cls, input_dir, output_dir,
                 basedata_dir=c.WORDS_DIR,
                 allow_overwriting=c.ALLOW_OVERWRITING,
                 raw_extension=c.RAW_EXTENSION,
                 words_files_extension=c.WORDS_FILES_EXTENSION,
                 log_on_error=c.LOG_ON_ERROR,
                 **kwargs):
        """
        Batch convert all files in a directory containing a `basedata_dir`.
        """
        basedata_dir = os.path.join(input_dir, basedata_dir)
        # Remove this keyword argument, which is a remnant of using
        # CoNLLMain.super_dir_main
        kwargs.pop('markables_dir', None)

        words_files = {
            filename
            for filename in os.listdir(basedata_dir)
            if filename.endswith(words_files_extension)
        }

        for name in words_files:
            words_file = os.path.join(basedata_dir, name)
            output_file = os.path.join(
                output_dir,
                name[:-len(words_files_extension)]
            ) + raw_extension

            if os.path.exists(output_file):
                if allow_overwriting:
                    logger.warn(f"Overwriting {output_file}")
                else:
                    raise IOError(f"Will not overwrite: {output_file}")
            try:
                cls.single_main(
                    output_file,
                    words_file,
                    **kwargs
                )
            except Exception as e:
                if log_on_error:
                    logger.error(
                        f"{name} from {input_dir} is skipped: "
                        + e.args[0]
                    )
                else:
                    e.args = (
                        f"While processing {name} from {input_dir}: " +
                        e.args[0],
                    ) + e.args[1:]
                    raise e

    @classmethod
    def single_main(cls, output_file, words_file, validate_xml=c.VALIDATE_XML):
        words = cls.read_words(
            filename=words_file,
            validate_xml=validate_xml
        )
        with open(output_file, 'w') as fd:
            fd.write(" ".join(word['word'] for word in words))

    def read_words(filename, validate_xml=c.VALIDATE_XML):
        """
        Read words from a words_file from COREA or SoNaR.
        """
        logger.debug("Read words..")
        words = SoNaRWordsDocumentReader(
            validate=validate_xml
        ).extract_items(
            etree.parse(filename)
        )
        return words

    @classmethod
    def get_args(cls, args_from_config=['validate_xml'],
                 batch_args_from_config=[
                    'allow_overwriting',
                    'raw_extension',
                    'words_files_extension',
                    'basedata_dir',
                    'markables_dir',
                    'log_on_error',
                    'dirs_to_ignore'
                 ]):
        from argparse import ArgumentParser, RawDescriptionHelpFormatter

        # Read command line arguments
        parser = ArgumentParser(
            description="""
    Script to scrape raw text data from data in MMAX format.

    Outputs every the content of a whole words file on one line, with tokens
    separated by spaces.

    To convert a whole directory recursively, run:

        mmax2conll.py <output folder> -d <input folder> [-d <input folder> ...]


    To only convert one file, run:

        mmax2conll.py <output.txt> <*_words.xml>


    When passing folders for batch processing using -d, the passed folders are
    searched for a data folder containing both a `Basedata` and `Markables` folder.
    The output is saved using the same path relative to the output folder as the
    original folder has relative to the passed folder the data folder was found in.

    !! NB !! This means that the data of two folders is merged if they happen
             to have the same path relative to passed folders. No files will be
             overwritten if overwriting isn't allowed in the configuration. If
             overwriting is allowed according to the configuration, a warning will
             be issued.

    """,  # noqa
            formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument('-l', '--log-level', default='INFO',
                            help="Logging level")
        parser.add_argument('-d', '--directory', action='append',
                            dest='directories', type=directory_exists,
                            help="Directory to batch convert files from")
        parser.add_argument('-c', '--config', help="YAML configuration file",
                            default='config/raw_config.yml')
        parser.add_argument('output',
                            help="Where to save the CoNLL output")
        parser.add_argument('words_file', type=file_exists, nargs='?',
                            help="MMAX *_words.xml file to use as input")
        args = vars(parser.parse_args())

        # Set the logging level
        logging.basicConfig(level=args.pop('log_level'))
        logger.debug(f"Args: {args}")

        batch = bool(args['directories'])
        output = args.pop('output')

        # Verify that the command line arguments are legal
        # AND remove the ones not needed
        if batch:
            args['output_dir'] = output
            if args.pop('words_file') is not None:
                parser.error(
                    "Please either specify a number of directories or the"
                    " necessary files to use as input, but not both."
                )
        else:
            del args['directories']
            args['output_file'] = output
            if args['words_file'] is None:
                parser.error(
                    "Please specify a *_words.xml file."
                    " You can also choose to specify a"
                    " number of directories to use as input instead."
                )

        # Read configuration
        config_file = args.pop('config')
        config = cls.read_config(config_file)

        # Read common keys
        args.update(
            cls.keys_from_config(config, args_from_config, config_file)
        )

        # Read batch keys
        if batch:
            args.update(
                cls.keys_from_config(
                    config,
                    batch_args_from_config,
                    config_file
                )
            )

        # Verify the output location
        cls.can_output_to(output, config, batch)

        return batch, args


if __name__ == '__main__':
    Main.main()
