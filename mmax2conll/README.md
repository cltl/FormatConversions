# mmax2conll
Script to convert coreference data in MMAX format to [CoNLL][] format.

See `CoNLL-specification.md` and `MMAX-specification.md` for extensive descriptions of the CoNLL and MMAX formats.


## Usage

To convert a whole folder (that contains a `Basedata` and `Markables` folder as direct children), run:

```sh
mmax2conll.py path/to/config.yml path/to/output_dir -d path/to/some/folder [-d path/to/another/folder ...]
```

To only convert one pair of files, run:
```sh
mmax2conll.py path/to/config.yml path/to/output.conll path/to/some_words.xml path/to/a_coref_level.xml [path/to/a_sentence_level.xml]
```


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
     12 | Coreference           | extracted from MMAX `*_coref_level.xml` files (ISSUE! \[2\])                  | Yes

\[1\]:
    The part numbers of DCOI start at 1, where the part numbers in a CoNLL file start at 0.
    To keep the origin of the data clear this 1-based part number is not changed,
    but instead an empty part 0 is added to those files.

\[2\]:
    The reference spans are not closed in the correct order if they end at the same word. The following is an example of output from `mmax2conll.py`:
    ```
              (10
                -
          (52|(55
              52)
                -
    10)|55)|(133)
    ```
    While pedantically correct would be:
    ```
              (10
                -
          (55|(52
              52)
                -
    (133)|55)|10)
    ```


# Issues

 - [ ] 'on_missing' config key is not validated before use
 - [ ] `basedata_dir` and `markables_dir` should not be configuration keys

# References
Multi-Level Annotation in MMAX (2003)<br>
... (To Do)<br>
http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf


COREA: Coreference Resolution for Extracting Answers for Dutch<br>
Iris Hendrickx, Gosse Bouma, Walter Daelemans, and Véronique Hoste.<br>
Essential Speech and Language Technology for Dutch, Ch.7, p.115 -- 128<br>
Editors: Peter Spyns, Jan Odijk<br>
https://link.springer.com/book/10.1007/978-3-642-30910-6<br>


[COREA]: https://link.springer.com/book/10.1007/978-3-642-30910-6
[CoNLL]: http://conll.cemantix.org/2012/data.html
