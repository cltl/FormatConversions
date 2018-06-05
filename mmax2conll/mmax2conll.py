#! /usr/bin/env python3

import os
import logging
import itertools as it

from lxml import etree

import code.constants as c
from code.util import file_exists, directory_exists

from code.mmax_document_readers import (
    document_ID_from_filename,
    add_sentence_layer_to_words,
    add_word_numbers,
    COREAWordsDocumentReader,
    SoNaRWordsDocumentReader,
    SoNaRSentencesDocumentReader,
    MMAXCorefDocumentReader,
)
from code.mmax_item_readers import COREAMedWordReader
from code.conll_converters import CorefConverter
from code.conll_writers import CoNLLWriter

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


class Main:
    @classmethod
    def find_data_dirs(cls, directory,
                       basedata_dir=c.WORDS_DIR,
                       markables_dir=c.MARKABLES_DIR,
                       dirs_to_ignore=c.DIRS_TO_IGNORE):
        """
        Recursively search `directory` for directories containing a
        `basedata_dir` and `markables_dir` directory as direct children.

        Does not return directories whose base name is in `dirs_to_ignore`,
        but does search them.
        """
        dirs_to_ignore = set(dirs_to_ignore)
        for subdir, subsubdirs, _ in os.walk(directory):
            if os.path.basename(subdir) in dirs_to_ignore:
                continue
            has_words = basedata_dir in subsubdirs
            has_markables = markables_dir in subsubdirs
            if has_words and has_markables:
                logger.debug(f"subdir: {subdir}")
                yield subdir
            elif has_markables:
                logger.warn(
                    f"{subdir} has a markables directory ({markables_dir}),"
                    f" but no words directory ({basedata_dir})."
                )
            elif has_words:
                logger.warn(
                    f"{subdir} has a words directory ({basedata_dir}), but no"
                    f" markables directory ({markables_dir})."
                )

    @classmethod
    def super_dir_main(cls, directories, output_dir,
                       basedata_dir=c.WORDS_DIR,
                       markables_dir=c.MARKABLES_DIR,
                       dirs_to_ignore=c.DIRS_TO_IGNORE,
                       allow_overwriting=c.ALLOW_OVERWRITING,
                       **kwargs):
        logger.debug(f"output_dir: {output_dir}")
        for directory in directories:
            data_dirs = cls.find_data_dirs(
                directory=directory,
                basedata_dir=basedata_dir,
                markables_dir=markables_dir,
                dirs_to_ignore=dirs_to_ignore
            )
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
                    basedata_dir=basedata_dir,
                    markables_dir=markables_dir,
                    allow_overwriting=allow_overwriting,
                    **kwargs
                )

    @classmethod
    def dir_main(cls, input_dir, output_dir,
                 basedata_dir=c.WORDS_DIR,
                 markables_dir=c.MARKABLES_DIR,
                 allow_overwriting=c.ALLOW_OVERWRITING,
                 conll_extension=c.CONLL_EXTENSION,
                 words_files_extension=c.WORDS_FILES_EXTENSION,
                 coref_files_extension=c.COREF_FILES_EXTENSION,
                 sentences_files_extension=c.SENTENCES_FILES_EXTENSION,
                 log_on_error=c.LOG_ON_ERROR,
                 **kwargs):
        """
        Batch convert all files in a directory containing a `basedata_dir` and
        `markables_dir` directory as direct children.
        """
        basedata_dir = os.path.join(input_dir, basedata_dir)
        markables_dir = os.path.join(input_dir, markables_dir)

        words_files = {
            filename[:-len(words_files_extension)]
            for filename in os.listdir(basedata_dir)
            if filename.endswith(words_files_extension)
        }

        coref_files = {
            filename[:-len(coref_files_extension)]
            for filename in os.listdir(markables_dir)
            if filename.endswith(coref_files_extension)
        }

        if sentences_files_extension is not None:
            sentences_files = {
                filename[:-len(sentences_files_extension)]
                for filename in os.listdir(markables_dir)
                if filename.endswith(sentences_files_extension)
            }

        all_files = words_files & coref_files

        if words_files - coref_files:
            logger.warn(
                "The following files seem to be words files, but do not"
                " have corresponding coreference files:\n\t" + '\n\t'.join(
                    sorted(words_files - coref_files)
                )
            )

        if coref_files - words_files:
            logger.warn(
                "The following files seem to be coreference files, but do not"
                " have corresponding words files:\n\t" + '\n\t'.join(
                    sorted(coref_files - words_files)
                )
            )

        if sentences_files_extension is not None:
            all_files &= sentences_files
            if words_files - sentences_files:
                logger.warn(
                    "The following files seem to be words files, but do not"
                    " have corresponding sentences files:\n\t" + '\n\t'.join(
                        sorted(words_files - sentences_files)
                    )
                )

            if coref_files - sentences_files:
                logger.warn(
                    "The following files seem to be coreference files, but do"
                    " not have corresponding sentences files:\n\t" +
                    '\n\t'.join(
                        sorted(coref_files - sentences_files)
                    )
                )

            if sentences_files - words_files:
                logger.warn(
                    "The following files seem to be sentences files, but do"
                    " not have corresponding words files:\n\t"
                    + '\n\t'.join(
                        sorted(sentences_files - words_files)
                    )
                )

            if sentences_files - coref_files:
                logger.warn(
                    "The following files seem to be sentences files, but do"
                    " not have corresponding coreference files:\n\t"
                    + '\n\t'.join(
                        sorted(sentences_files - coref_files)
                    )
                )

        for name in all_files:
            words_file = os.path.join(basedata_dir, name) + \
                words_files_extension

            coref_file = os.path.join(markables_dir, name) + \
                coref_files_extension

            sentences_file = None \
                if sentences_files_extension is None \
                else os.path.join(markables_dir, name) \
                + sentences_files_extension

            output_file = os.path.join(output_dir, name) + conll_extension

            if os.path.exists(output_file):
                if allow_overwriting:
                    logger.warn(f"Overwriting {output_file}")
                else:
                    raise IOError(f"Will not overwrite: {output_file}")
            try:
                cls.single_main(
                    output_file,
                    words_file,
                    coref_file,
                    sentences_file,
                    words_files_extension=words_files_extension,
                    **kwargs
                )
            except Exception as e:
                if log_on_error:
                    logger.error(
                        f"{name} from {input_dir} is skipped: " + e.args[0]
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
            words_file,
            coref_file,
            sentences_file=None,
            words_files_extension=c.WORDS_FILES_EXTENSION,
            validate_xml=c.VALIDATE_XML,
            auto_use_Med_item_reader=c.AUTO_USE_MED_ITEM_READER,
            warn_on_auto_use_Med_item_reader=c.WARN_ON_AUTO_USE_MED_ITEM_READER,  # noqa
            conll_defaults=c.CONLL_DEFAULTS,
            min_column_spacing=c.MIN_COLUMN_SPACING,
            on_missing=c.CONLL_ON_MISSING,
            coref_filter=c.MMAX_COREF_FILTER):
        # Read sentences
        if sentences_file is None:
            document_id, sentences = cls.read_COREA(
                filename=words_file,
                extension=words_files_extension,
                validate_xml=validate_xml,
                on_missing_document_ID=on_missing['document_id'],
                warn_on_auto_use_Med_item_reader=warn_on_auto_use_Med_item_reader   # noqa
            )
        else:
            document_id, sentences = cls.read_SoNaR(
                words_file=words_file,
                sentences_file=sentences_file,
                validate_xml=validate_xml,
                words_files_extension=words_files_extension,
                on_missing_document_ID=on_missing['document_id']
            )

        # Read in coreference data
        logger.debug("Read coreference data...")
        coref_sets = MMAXCorefDocumentReader(
            words=it.chain(*sentences),
            validate=validate_xml,
            item_filter=coref_filter,
        ).extract_coref_sets(
            etree.parse(coref_file)
        )

        # Merge coref data into sentences (in place)
        CorefConverter(sentences).add_data_from_coref_sets(coref_sets)

        # Save the data to CoNLL
        cls.write_conll(
            filename=output_file,
            writer=CoNLLWriter(
                defaults=conll_defaults,
                min_column_spacing=min_column_spacing,
                on_missing=on_missing
            ),
            document_id=document_id,
            sentences=sentences
        )

    @classmethod
    def read_SoNaR(cls, words_file, sentences_file,
                   validate_xml=c.VALIDATE_XML,
                   words_files_extension=c.WORDS_FILES_EXTENSION,
                   on_missing_document_ID=c.CONLL_ON_MISSING['document_id']):
        """
        Read sentences and document ID from a words_file and sentences file
        from SoNaR.

        Extracts the document ID using the file basename.
        """
        # Read document ID
        document_id = document_ID_from_filename(
            words_file,
            words_files_extension
        )
        cls.check_document_id(document_id, words_file, on_missing_document_ID)

        # Read words
        logger.debug("Read words..")
        words = list(SoNaRWordsDocumentReader(
            validate=validate_xml
        ).extract_items(
            etree.parse(words_file)
        ))

        logger.debug("Read sentences...")
        # Add sentence data
        sentence_items = SoNaRSentencesDocumentReader(
            words,
            validate=validate_xml
        ).extract_items(etree.parse(sentences_file))
        sentences = add_sentence_layer_to_words(words, sentence_items)
        del words, sentence_items

        add_word_numbers(sentences)

        return document_id, sentences

    @classmethod
    def read_COREA(
            cls,
            filename,
            extension=c.WORDS_FILES_EXTENSION,
            validate_xml=c.VALIDATE_XML,
            on_missing_document_ID=c.CONLL_ON_MISSING['document_id'],
            warn_on_auto_use_Med_item_reader=c.WARN_ON_AUTO_USE_MED_ITEM_READER
            ):
        """
        Read sentences and document ID from a words_file from COREA.

        First tries to figure out the document ID using the xml and falls back
        on finding a document ID using the file basename.

        See Ch. 7 of Essential Speech and Language Technology for Dutch
        COREA: Coreference Resolution for Extracting Answers for Dutch
        https://link.springer.com/book/10.1007/978-3-642-30910-6
        """
        reader = COREAWordsDocumentReader(validate=validate_xml)
        xml = etree.parse(filename)
        document_id = reader.extract_document_ID(xml)
        if document_id is None and extension is not None:
            document_id = document_ID_from_filename(filename, extension)
        cls.check_document_id(document_id, filename, on_missing_document_ID)

        # Automatically use COREAMedWordReader is the document ID starts with
        # the ID of the Med part of COREA.
        if document_id.startswith(c.COREA_MED_ID):
            if warn_on_auto_use_Med_item_reader:
                logger.warn(
                    "Ignoring reader.item_reader and automatically using the"
                    " item reader for COREA Med"
                )
            reader.item_reader = COREAMedWordReader()

        return document_id, reader.extract_sentences(xml)

    @classmethod
    def check_document_id(cls, document_id, filename,
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

    @classmethod
    def write_conll(cls, filename, writer, document_id, sentences):
        """
        Write sentence data to a file in CoNLL format.
        """
        with open(filename, 'w') as fd:
            writer.write(fd, document_id, sentences)

    @classmethod
    def can_output_to(cls, output, config, batch):
        if os.path.exists(output):
            if not config['allow_overwriting']:
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
    def get_args(cls, args_from_config=[
                    'validate_xml',
                    'auto_use_Med_item_reader',
                    'warn_on_auto_use_Med_item_reader',
                    'min_column_spacing',
                    'conll_defaults',
                    'words_files_extension',
                    'on_missing',
                 ], batch_args_from_config=[
                    'allow_overwriting',
                    'conll_extension',
                    'basedata_dir',
                    'markables_dir',
                    'coref_files_extension',
                    'sentences_files_extension',
                    'log_on_error',
                    'dirs_to_ignore'
                 ]):
        from argparse import ArgumentParser, RawDescriptionHelpFormatter

        # Read command line arguments
        parser = ArgumentParser(
            description="""
    Script to convert coreference data in MMAX format to CoNLL format.

    See `CoNLL-specification.md` and `MMAX-specification.md` for extensive
    descriptions of the CoNLL and MMAX formats.

    To convert a whole directory recursively, run:

        mmax2conll.py <config file> <output folder> -d <input folder> [-d <input folder> ...]


    To only convert one pair (or triple) of files, run:

        mmax2conll.py <config file> <output.conll> <*_words.xml> <*coref markables file> [<*_sentence_level.xml>]


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
        parser.add_argument('config', help="YAML configuration file")
        parser.add_argument('output',
                            help="Where to save the CoNLL output")
        parser.add_argument('words_file', type=file_exists, nargs='?',
                            help="MMAX *_words.xml file to use as input")
        parser.add_argument(
            'coref_file',
            type=file_exists,
            nargs='?',
            help="MMAX coreference level markables file to use as input"
        )
        parser.add_argument(
            'sentences_file',
            type=file_exists,
            nargs='?',
            help="MMAX *_sentence_level.xml file to use as input"
        )
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
            if args.pop('words_file') is not None or \
               args.pop('coref_file') is not None:
                parser.error(
                    "Please either specify a number of directories or the"
                    " necessary files to use as input, but not both."
                )
            args.pop('sentences_file')
        else:
            del args['directories']
            args['output_file'] = output
            if args['words_file'] is None or args['coref_file'] is None:
                parser.error(
                    "Please specify both a *_words.xml file and a"
                    " *_coref_level.xml file. You can also choose to specify a"
                    " number of directories to use as input instead."
                )

        # Read configuration
        config_file = args.pop('config')
        config = cls.read_config(config_file)

        # Read common keys
        args.update(
            cls.keys_from_config(config, args_from_config, config_file)
        )
        args['coref_filter'] = lambda i: \
            c.MMAX_TYPE_FILTERS[config['coref_type_filter']](i) and \
            c.MMAX_LEVEL_FILTERS[config['coref_level_filter']](i)

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

    @classmethod
    def keys_from_config(cls, config, keys, filename):
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

    @classmethod
    def read_config(cls, filename):
        from pyaml import yaml

        # Read the configuration file
        with open(filename) as config_fd:
            config = yaml.load(config_fd)

        return config

    @classmethod
    def main(cls):
        batch, args = cls.get_args()
        if batch:
            cls.super_dir_main(**args)
        else:
            cls.single_main(**args)
        logger.info("Done!")


if __name__ == '__main__':
    Main.main()
