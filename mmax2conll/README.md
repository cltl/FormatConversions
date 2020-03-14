# mmax2conll
Script to convert coreference data in MMAX (Müller and Strube, 2003) format to [CoNLL][] format or raw text files.

See `CoNLL-specification.md` and `MMAX-specification.md` for extensive descriptions of the CoNLL and MMAX formats.

If you're trying to use this, you probably want to use https://github.com/andreasvc/dutchcoref/blob/master/mmaxconll.py instead. (14-03-2014)

## Usage

### `mmax2conll.py`
Because the [COREA][] corpus saves its sentence information in the `*_words.xml` files
but the SoNaR-1 part of the [SoNaR][] corpus saves this separately in `*_sentence_level.xml` files,
specifying a sentences file is optional.

To automatically find all (sub)folders that contain a `Basedata` and `Markables` folder as direct children and convert all data in those folders, run:

```sh
python -m mmax2conll path/to/config.yml path/to/output_dir -d path/to/some/folder [-d path/to/another/folder ...]
```

To only convert one pair (or triple) of files, run:
```sh
python -m mmax2conll path/to/config.yml path/to/output.conll path/to/some_words.xml path/to/a_coref_level.xml [path/to/a_sentence_level.xml]
```

### `mmax2raw.py`
To automatically find all (sub)folders that contain a `Basedata` and `Markables` folder as direct children and convert all data in those folders, run:

```sh
mmax2raw.py path/to/output_dir -d path/to/some/folder [-d path/to/another/folder ...]
```

To only convert one file, run:
```sh
mmax2raw.py path/to/output.txt path/to/some_words.xml
```


## Columns of CoNLL output
These scripts were first used to convert data from the COREA dataset (Hendrickx et al., 2013) to CoNLL and
COREA does not contain the following information:

 - POS tags
 - constituency tree
 - predicates
 - speaker/author information
 - named entities

Therefore **these scripts strictly do not output data in CoNLL format**.
The following values and place-holders are used.

| Column  | Description           | Value                                                                         | Conform CoNLL specification?
| ---:    | ---                   | ---                                                                           | ---
|       1 | Document ID           | file path without extension                                                   | Yes
|       2 | Part number           | `0` or as extracted from `<word>.alpsent` from MMAX `*_words.xml` files \[1\] | Yes
|       3 | Word number           | `<word>.alppos` or `<word>.pos` from MMAX `*_words.xml` files                 | Yes
|       4 | Word itself           | content of `<word>` tags from MMAX `*_words.xml` files                        | Yes
|       5 | POS                   | `[POS]`                                                                       | No
|       6 | Parse bit             | `*`                                                                           | No
|       7 | Predicate lemma       | `-`                                                                           | Yes
|       8 | Predicate Frameset ID | `-`                                                                           | Yes
|       9 | Word sense            | `-`                                                                           | Yes
|      10 | Speaker/Author        | `UNKNOWN`                                                                     | ???
|      11 | Named Entities        | `*`                                                                           | Yes
|       - | Predicate Arguments   | None: column(s) left out entirely                                             | Yes, conform example in CoNLL 2012
|      12 | Coreference           | extracted from MMAX `*_coref_level.xml` files (ISSUE! \[2\])                  | Yes

\[1\]:
  The part numbers of DCOI start at 1, where the part numbers in a CoNLL file start at 0.
  To keep the origin of the data clear this 1-based part number is not changed,
  but instead an empty part 0 is added to those files.

\[2\]:
  The reference spans are not closed in the correct order if they end at the same word. The following is an example of output from `mmax2conll`:

              (10
                -
          (52|(55
              52)
                -
    10)|55)|(133)

  While pedantically correct would be:

              (10
                -
          (55|(52
              52)
                -
    (133)|55)|10)


# Issues

 - [ ] Skipping a whole file one any error is too wasteful
 - [ ] 'on_missing' config key is not validated before use
 - [ ] `basedata_dir` and `markables_dir` should not be configuration keys
 - [ ] Too many methods in `main.py` are marked as class methods

# References
Christoph Müller and Michael Strube.<br>
Multi-Level Annotation in MMAX<br>
In Proceedings of the 4th SIGDIAL Workshop. 2003.<br>
URL http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf


Iris Hendrickx, Gosse Bouma, Walter Daelemans and Véronique Hoste.<br>
COREA: Coreference Resolution for Extracting Answers for Dutch<br>
Essential Speech and Language Technology for Dutch, Ch.7, p.115 -- 128. 2013.<br>
Editors: Peter Spyns, Jan Odijk<br>
https://link.springer.com/book/10.1007/978-3-642-30910-6<br>
DOI: [10.1007/978-3-642-30910-6](https://doi.org/10.1007/978-3-642-30910-6)<br>

SoNaR: https://ivdnt.org/downloads/taalmaterialen/tstc-sonar-corpus<br>
COREA: https://ivdnt.org/downloads/taalmaterialen/tstc-corea-coreferentiecorpus

[COREA]: https://ivdnt.org/downloads/taalmaterialen/tstc-corea-coreferentiecorpus
[CoNLL]: http://conll.cemantix.org/2012/data.html
[SoNaR]: https://ivdnt.org/downloads/taalmaterialen/tstc-sonar-corpus
