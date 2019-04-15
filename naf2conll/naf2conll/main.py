#! /usr/bin/env python3

import os
import logging

from KafNafParserPy import KafNafParser

from . import constants as c
from .util import (
    file_exists,
    directory_exists,
    document_ID_from_filename,
    add_word_numbers,
)
from .naf_readers import NAFReader
from .conll_converters import CorefConverter
from .conll_writers import CoNLLWriter

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


class Main:
    @classmethod
    def find_data_dirs(cls, directory,
                       naf_extension=c.NAF_EXTENSION,
                       dirs_to_ignore=c.DIRS_TO_IGNORE):
        """
        Recursively search `directory` for directories containing NAF files.

        Does not return directories whose base name is in `dirs_to_ignore`,
        but does search them.
        """
        dirs_to_ignore = set(dirs_to_ignore)
        for subdir, _, files in os.walk(directory):
            if os.path.basename(subdir) in dirs_to_ignore:
                continue
            if any(file.endswith(naf_extension) for file in files):
                logger.debug(f"subdir: {subdir}")
                yield subdir

    @classmethod
    def super_dir_main(cls, directories, output_dir,
                       naf_extension=c.NAF_EXTENSION,
                       dirs_to_ignore=c.DIRS_TO_IGNORE,
                       allow_overwriting=c.ALLOW_OVERWRITING,
                       **kwargs):
        logger.debug(f"output_dir: {output_dir}")
        for directory in directories:
            data_dirs = sorted(cls.find_data_dirs(
                directory=directory,
                naf_extension=naf_extension,
                dirs_to_ignore=dirs_to_ignore
            ))
            for data_dir in data_dirs:
                cur_output_dir = os.path.join(
                    output_dir,
                    data_dir[len(directory):]
                )
                if not allow_overwriting and os.path.exists(cur_output_dir):
                    logger.warn(
                        f"Merging output converted from {data_dir} into"
                        f" {cur_output_dir}"
                    )
                else:
                    logger.debug(f"Creating: {cur_output_dir}")
                    os.makedirs(cur_output_dir, exist_ok=True)
                    logger.info(
                        f"Saving data converted from {data_dir} in"
                        f" {cur_output_dir}"
                    )

                cls.dir_main(
                    input_dir=data_dir,
                    output_dir=cur_output_dir,
                    naf_extension=naf_extension,
                    allow_overwriting=allow_overwriting,
                    **kwargs
                )

    @classmethod
    def dir_main(cls, input_dir, output_dir,
                 allow_overwriting=c.ALLOW_OVERWRITING,
                 conll_extension=c.CONLL_EXTENSION,
                 naf_extension=c.NAF_EXTENSION,
                 log_on_error=c.LOG_ON_ERROR,
                 **kwargs):
        """
        Batch convert all NAF files in `input_dir`.
        """
        files = sorted(
            filename
            for filename in os.listdir(input_dir)
            if filename.endswith(naf_extension)
        )

        for name in files:
            naf_file = os.path.join(input_dir, name)
            output_file = os.path.join(
                output_dir,
                name[:-len(naf_extension)]
            ) + conll_extension

            if os.path.exists(output_file):
                if allow_overwriting:
                    logger.warn(f"Overwriting {output_file}")
                else:
                    raise IOError(f"Will not overwrite: {output_file}")
            try:
                cls.single_main(
                    output_file,
                    naf_file,
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
    def single_main(
           cls,
           output_file,
           naf_file,
           naf_extension=c.NAF_EXTENSION,
           validate=c.VALIDATE,
           uniqueyfy=c.UNIQUEYFY,
           fill_non_consecutive_coref_spans=c.FILL_NON_CONSECUTIVE_COREF_SPANS,
           sentence_filter=c.SENTENCE_DEFAULT_FILTER,
           conll_columns=c.CONLL_COLUMNS,
           conll_defaults=c.CONLL_DEFAULTS,
           min_column_spacing=c.MIN_COLUMN_SPACING,
           on_missing=c.CONLL_ON_MISSING,
           ):
        # Read document ID
        document_id = document_ID_from_filename(
            naf_file,
            naf_extension
        )
        cls.check_document_id(document_id, naf_file, on_missing['document_id'])

        # Read data
        reader = NAFReader(validate=validate)
        nafobj = KafNafParser(naf_file)
        sentences = reader.extract_sentences(nafobj)
        coref_sets = reader.extract_coref_sets(nafobj)
        del reader, nafobj

        add_word_numbers(sentences)

        CorefConverter(
            sentences,
            uniqueyfy=uniqueyfy,
            fill_spans=fill_non_consecutive_coref_spans,
        ).add_data_from_coref_sets(
            coref_sets
        )
        del coref_sets

        sentences = filter(sentence_filter, sentences)

        # Save the data to CoNLL
        cls.write_conll(
            filename=output_file,
            writer=CoNLLWriter(
                defaults=conll_defaults,
                min_column_spacing=min_column_spacing,
                on_missing=on_missing,
                columns=conll_columns
            ),
            document_id=document_id,
            sentences=sentences
        )

    @staticmethod
    def check_document_id(document_id, filename,
                          on_missing=c.CONLL_ON_MISSING['document_id']):
        """
        Check the document ID of a document.
        """
        message = f"No document ID could be found for {filename}."
        if on_missing == 'warn':
            if document_id is None:
                logger.warn(message)
        elif on_missing == 'throw':
            if document_id is None:
                logger.warn(message)
        elif on_missing != 'nothing':
            raise ValueError(
                    "`on_missing` should be either 'nothing', 'warn' or"
                    " 'throw', but `on_missing['document_id']` is"
                    f" {on_missing!r}"
                )

    @staticmethod
    def write_conll(filename, writer, document_id, sentences):
        """
        Write sentence data to a file in CoNLL format.
        """
        with open(filename, 'w') as fd:
            writer.write(fd, document_id, sentences)

    @staticmethod
    def can_output_to(output, batch, allow_overwriting=None):
        """
        Check whether the specified output location is legal.

        Handles batch and single file separately.

        :param output:              specified output location (may be both a
                                    directory or a file)
        :param batch:               whether the output location is for batch
                                    processing or a single file
        :param allow_overwriting:   whether to allow overwriting existing
                                    files or directories. Defaults to
                                    c.ALLOW_OVERWRITING if `None`.
        """
        if allow_overwriting is None:
            allow_overwriting = c.ALLOW_OVERWRITING

        if os.path.exists(output):
            if not allow_overwriting:
                thing = "folder" if batch else "file"
                raise ValueError(
                    "The configuration specifies overwriting is not allowed,"
                    f" but the output {thing} already exists: {output}"
                )
        else:
            # (Check if we can) create it
            if batch:
                os.makedirs(output)
                # This will keep some directories, but not the leaf one
                # that's annoying but at least we don't get a warning
                os.rmdir(output)
            else:
                open(output, 'w').close()
                os.remove(output)

    @classmethod
    def get_args(cls, cmdline_args=None, args_from_config=[
                    'validate',
                    'uniqueyfy',
                    'fill_non_consecutive_coref_spans',
                    'sentence_filter',
                    'naf_extension',
                    'min_column_spacing',
                    'conll_columns',
                    'conll_defaults',
                    'on_missing',
                 ], batch_args_from_config=[
                    'allow_overwriting',
                    'conll_extension',
                    'log_on_error',
                    'dirs_to_ignore'
                 ]):
        from argparse import ArgumentParser, RawDescriptionHelpFormatter

        # Read command line arguments
        parser = ArgumentParser(
            prog='python -m naf2conll',
            description="""
    Script to convert coreference data in NAF format to CoNLL format.

    !! NB !! At the moment, this script only supports the following columns:

     -  1: Document ID
     -  3: Word number
     -  4: Word itself
     - 12: Coreference

    See `CoNLL-specification.md` for an extensive description of the CoNLL format:
    https://github.com/cltl/FormatConversions/blob/master/mmax2conll/CoNLL-specification.md

    To automatically find all (sub)folders that contain NAF files and convert all
    data in those folders, run:

        python -m naf2conll <output folder> -d <input folder> [-d <input folder> ...]

    To only convert one file, run:

        python -m naf2conll <output.conll> <naf file>


    When passing folders for batch processing using -d, the output is saved using
    the same path relative to the output folder as the original folder has relative
    to the folder passed using `-d`.

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
                            type=file_exists)
        parser.add_argument('output',
                            help="Where to save the CoNLL output")
        parser.add_argument('naf_file', type=file_exists, nargs='?',
                            help="NAF file to use as input")
        args = vars(parser.parse_args(cmdline_args))
        del cmdline_args

        # Set the logging level
        logging.basicConfig(level=args.pop('log_level'))
        logger.debug(f"Args: {args}")

        batch = bool(args['directories'])
        output = args.pop('output')

        # Verify that the command line arguments are legal
        # AND remove the ones not needed
        if batch:
            args['output_dir'] = output
            if args.pop('naf_file') is not None:
                parser.error(
                    "Please either specify a number of directories or the"
                    " necessary files to use as input, but not both."
                )
        else:
            del args['directories']
            args['output_file'] = output
            if args['naf_file'] is None:
                parser.error(
                    "Please specify both a naf file and a"
                    " *_coref_level.xml file. You can also choose to specify a"
                    " number of directories to use as input instead."
                )

        if batch:
            args_from_config.extend(batch_args_from_config)
            del batch_args_from_config

        cls.process_config(args, args_from_config)

        # Verify the output location
        cls.can_output_to(output, batch, args.get('allow_overwriting', None))

        return batch, args

    @classmethod
    def process_config(cls, args, args_from_config):
        """
        Read arguments from configuration file if a configuration file is given
        in the `config` key of `args`.

        Changes `args` in place.
        """
        filename = args.pop('config', None)
        if filename is not None:
            # Read configuration
            config = cls.read_config(filename)

            # Read common keys
            args.update(
                cls.keys_from_config(config, args_from_config, filename)
            )

            args['sentence_filter'] = c.SENTENCE_FILTERS[
                args['sentence_filter']
            ]

    @staticmethod
    def keys_from_config(config, keys, filename):
        """
        Select some `keys` with their values from a dictionary

        `filename` is only used for the error message if a key is missing
        """
        args = {}
        # Extract required arguments from configuration
        for arg in keys:
            if arg not in config:
                raise ValueError(
                    f"The key {arg!r} is not in the specified configuration"
                    f" file {filename}"
                )
            args[arg] = config[arg]

        return args

    @staticmethod
    def read_config(filename):
        from pyaml import yaml

        # Read the configuration file
        with open(filename) as config_fd:
            config = yaml.safe_load(config_fd)

        return config

    @classmethod
    def main(cls, cmdline_args=None):
        batch, args = cls.get_args(cmdline_args)
        del cmdline_args
        if batch:
            cls.super_dir_main(**args)
        else:
            cls.single_main(**args)
        logger.info("Done!")


if __name__ == '__main__':
    Main.main()
