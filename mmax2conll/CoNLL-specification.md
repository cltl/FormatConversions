# CoNLL Format
[This page][CoNLL-2012] contains the CoNLL file format description.

It seems like [LDC2011T03][] is the "CoNLL-2012 training and development package from LDC" as mentioned on the [CoNLL-2012 data page][CoNLL-2012],
because the version number (= 4),
the languages (= Arabic, Chinese and English)
and the file structure (= `data/(files|train)/data/english/annotations/nw/wsj/05/`)
are the same or very similar.

Every part (see column two) starts with `#begin document ([document ID]); part [part number (zero padded to 3 digits)]` and ends with `#end document`.

Column  | Type                    | Description
-------:|-------------------------|----------
1       | Document ID             | This is a variation on the document filename. Mostly it's the path of the file without the extension.
2       | Part number             | Some files are divided into multiple parts numbered as 000, 001, 002, ... etc.
3       | Word number             | 0-based word number **of the sentence**
4       | Word itself
5       | Part-of-Speech
6       | Parse bit               | The structure of the constituency tree. This field is the bracketed structure broken before the first open parenthesis in the parse, and the word/part-of-speech leaf replaced with a `*`. The full parse can be created by substituting the asterix with the `([pos] [word])` string (or leaf) and concatenating the items in the rows of that column (= concatenate this column for all the rows (of the tokens) that are part of the same sentence). \[1\]
7       | Predicate lemma         | The predicate lemma is mentioned for the rows for which we have semantic role information. All other rows are marked with a `-`.
8       | Predicate Frameset ID   | PropBank frameset ID of the predicate in Column 7.
9       | Word sense              | Word sense of the word in Column 3.
10      | Speaker/Author          | Speaker or author name where available. Mostly in Broadcast Conversation and Web Log data.
11      | Named Entities          | Identifies the spans representing various named entities.
12:N    | Predicate Arguments     | There is one column each of predicate argument structure information for the predicate mentioned in Column 7. I.E. the arguments for the predicate first mentioned in Column 7 can be found in Column 12, those for the second predicate in Column 7 can be found in Column 13, etc. If the sentence contains no predicates, these columns are left out entirely, i.e. `N = 12`.
N       | Coreference             | Coreference chain information encoded in a parenthesis structure. The parentheses mark a span of text and the number is the (arbitrary) id of the referred entity.

\[1\] i.e.
```
for newline delimited block as sentence in file:
    for row in sentence:
        replace `*` with `(<pos> <word>)`
    parse = join(column 6 of row for row in sentence)
```

[CoNLL-2012]: http://conll.cemantix.org/2012/data.html
[LDC2011T03]: https://catalog.ldc.upenn.edu/LDC2011T03
