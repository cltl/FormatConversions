# naf2conll
Script to convert coreference data in NAF format to [CoNLL][] format.

!! NB !! At the moment, this script only supports the following columns:

 -  1: Document ID
 -  3: Word number
 -  4: Word itself
 - 12: Coreference

The following CoNLL columns are supported by NAF, but are not (yet) processed (correctly) by this script:

 -  5: POS tag
 -  6: constituency tree
 - ...?
 - 11: named entities

See `CoNLL-specification.md` for an extensive description of the CoNLL format.


## Usage

### `naf2conll.py`
To automatically find all (sub)folders that contain NAF files and convert all data in those folders, run:

```sh
naf2conll.py path/to/output_dir -d path/to/some/folder [-d path/to/another/folder ...]
```

To only convert one file, run:
```sh
naf2conll.py path/to/output.conll path/to/input.naf
```

## Columns of CoNLL output
By default only Column 1, 3, 4 and 12 are output.

If you choose to output more columns, the following values and place-holders are used.

| Column      | Description           | Value                                                    | Conform CoNLL specification?
| ---:        | ---                   | ---                                                      | ---
|       **1** | Document ID           | file path without extension                              | Yes
|         2   | Part number           | `0`                                                      | Yes
|       **3** | Word number           | generated                                                | Yes
|       **4** | Word itself           | extracted from text layer of NAF                         | Yes
|         5   | POS                   | `[POS]`                                                  | No
|         6   | Parse bit             | `*`                                                      | No
|         7   | Predicate lemma       | `-`                                                      | Yes
|         8   | Predicate Frameset ID | `-`                                                      | Yes
|         9   | Word sense            | `-`                                                      | Yes
|        10   | Speaker/Author        | `UNKNOWN`                                                | ???
|        11   | Named Entities        | `*`                                                      | Yes
|         -   | Predicate Arguments   | None: column(s) left out entirely                        | Yes, conform example in CoNLL 2012
|      **12** | Coreference           | extracted from coreference layer of NAF (ISSUE! \[1\])   | Yes

\[1\]:
  The reference spans are not closed in the correct order if they end at the same word. The following is an example of output from `naf2conll.py`:

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

 - [ ] 'on_missing' config key is not validated before use

