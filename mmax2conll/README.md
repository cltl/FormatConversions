# mmax2conll
Script to convert data in MMAX format to [CoNLL][] format.

See `CoNLL-specification.md` and `MMAX-specification.md` for extensive descriptions of the CoNLL and MMAX formats.


## Usage

To convert a whole folder (that contains a `Basedata` and `Markables` folder as direct children), run:

```sh
mmax2conll.py path/to/some/folder
```

To only convert one pair of files, run:
```sh
mmax2conll.py path/to/some_words.xml path/to/a_coref_level.xml path/to/output.conll
```

Effectively this does:

 1. `words2conll.py`: Converts `*_words.xml` to `*_no_coref.conll`, putting `*` as place holder in the coreference column (Column 12).
 2. `add_coref_to_conll.py`: Converts `*_coref_level.xml` + `*_no_coref.conll` to `*.conll`



## Columns of CoNLL output
These scripts were first used to convert data from the [COREA][] (Ch.7 p.115 -- 128) dataset to CoNLL and
COREA does not contain the following information:

 - POS tags
 - constituency tree
 - predicates
 - speaker/author information
 - named entities

Therefore **these scripts strictly do not output data in CoNLL format**.
The following values and place-holders are used.

Column  | Description           | Value                                                                         | Conform CoNLL specification?
---:    | ---                   | ---                                                                           | ---
      1 | Document ID           | file path without extension                                                   | Yes
      2 | Part number           | `0` or as extracted from `<word>.alpsent` from MMAX `*_words.xml` files \[1\] | Yes
      3 | Word number           | `<word>.alppos` or `<word>.pos` from MMAX `*_words.xml` files                 | Yes
      4 | Word itself           | content of `<word>` tags from MMAX `*_words.xml` files                        | Yes
      5 | POS                   | `[POS]`                                                                       | No
      6 | Parse bit             | `*`                                                                           | No
      7 | Predicate lemma       | `-`                                                                           | Yes
      8 | Predicate Frameset ID | `-`                                                                           | Yes
      9 | Word sense            | `-`                                                                           | Yes
     10 | Speaker/Author        | `UNKNOWN`                                                                     | ???
     11 | Named Entities        | `*`                                                                           | Yes
      - | Predicate Arguments   | None: column(s) left out entirely                                             | Yes, conform example in CoNLL 2012
     12 | Coreference           | extracted from MMAX `*_coref_level.xml` files                                 | Yes

\[1\]:
    The part numbers of DCOI start at 1, where the part numbers in a CoNLL file start at 0.
    To keep the origin of the data clear this 1-based part number is not changed,
    but instead an empty part 0 is added to those files.

[COREA]: https://link.springer.com/book/10.1007/978-3-642-30910-6
[CoNLL]: http://conll.cemantix.org/2012/data.html
