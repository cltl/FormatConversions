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

<PERSON m_id="141" >
<token_anchor t_id="1452"/>
<token_anchor t_id="1453"/>
<token_anchor t_id="1454"/>
</PERSON>

