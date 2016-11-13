This directory contains scripts that converts annotations in cat for purposes of inspection or correction.
It currently contains two scripts

1. cat2cat_attribute_to_markable.py
This script converts markables to markables that are named after one of their attributes. It is meant to make differences in attributes explicit.

2. cat2cat_missing_attributes.py
This script is meant to identify markables where at least one attribute did not receive a value. It creates a copy of the original annotations where only markables with missing attributes are maintained, so annotators can correct them easily.

* Program 1 cat2cat_attribute_to_markable.py

How to run this program:

python cat2cat_attribute_to_markable.py MARKABLENAME ATTRIBUTENAME indir/ outdir/

where, 
* MARKABLENAME is the name of the markable you want to differentiate
* ATTRIBUTENAME is the name of the attribute that you want to distinguish

e.g.

python cat2cat_attribute_to_markable.py NAMEDENTITY type indir/ outdir/

converts all markables NAMEDENTITY into markables with the name of the type:

<NAMEDENTITY m_id="141" type="PERSON" tokenization_error="FALSE"  >
<token_anchor t_id="1452"/>
<token_anchor t_id="1453"/>
<token_anchor t_id="1454"/>
</NAMEDENTITY>

becomes:

<PERSON m_id="141">
<token_anchor t_id="1452"/>
<token_anchor t_id="1453"/>
<token_anchor t_id="1454"/>
</PERSON>


* Program 2 cat2cat_missing_attributes.py

How to run this program:

python cat2cat_missing_attributes.py inputdir/ outputdir/

The program checks all markables of an annotated file and retains those with missing attributes.
If the file contains at least one such markable, a copy with only those that require completion is placed in the output directory.
