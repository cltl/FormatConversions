The cat2naf/ scripts take a CAT file and NAF file as input and add specific information from CAT to NAF.

The first script assumes that the CAT and NAF tokens correspond. Scripts to fix mismatches will be added in the future.


* Conversion script:

cat2naf_entities.py

* Usage:

python cat2naf_entities.py catfile.xml naffile.naf outfile.naf

The script assumes that the entity markables are called 'NAMEDENTITY' and the entity type is defined by the attribute 'type'

* Future steps:

1. make more generic script where markable names and attributes can be defined
