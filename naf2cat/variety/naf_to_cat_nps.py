from KafNafParserPy import *
from lxml import etree
import sys
import os




def create_tokens(nafobj, root):
    '''
        Adds the tokens from NAF to CAT
        '''
    number = 0
    sent_nr = '0'
    for tok in nafobj.get_tokens():
        token = tok.get_text()
        sent = tok.get_sent()
        if sent != sent_nr:
            number = 0
            sent_nr = sent
        tokId = tok.get_id().lstrip('w')
        child = etree.SubElement(root, 'token', t_id=tokId, sentence=sent, number=str(number))
        child.text = token
        number += 1



def get_token_id_from_term(nafobj, termId):
    
    term = nafobj.get_term(termId)
    tokenId = term.get_span().get_span_ids()[0]
    return tokenId


def turn_term_ids_to_catids(nafobj, term_ids):

    m_ids = set()
    for term_id in term_ids:
        tok_id = get_token_id_from_term(nafobj, term_id)
        catid = tok_id.lstrip('w')
        m_ids.add(int(catid))
    cat_ids = []
    for mid in sorted(m_ids):
        cat_ids.append(str(mid))
    return cat_ids



def add_markable(markables, spanids, mid):
    
    mark = etree.SubElement(markables, 'NP', m_id=str(mid))
    for tid in spanids:
        toch_anch = etree.SubElement(mark, 'token_anchor', t_id=tid)

def create_markables(nafobj, markables):

    nominal_heads = []
    #collect all nominal heads
    for term in nafobj.get_terms():
        if term.get_pos() in ['pron', 'noun']:
            nominal_heads.append(term.get_id())

    #for each nominal head, get full constituent
    dep_extractor = nafobj.get_dependency_extractor()
    nps = []
    for nom_head in nominal_heads:
        mydeps = dep_extractor.get_full_dependents(nom_head, [])
        mydeps.append(nom_head)
        nps.append(mydeps)

    mid = 1
    for np in nps:
        cat_ids = turn_term_ids_to_catids(nafobj, np)
        add_markable(markables, cat_ids, mid)
        mid += 1




def create_catfiles(nafdir, catdir):
    
    
    for f in os.listdir(nafdir):
        nafobj = KafNafParser(nafdir + f)
        cfname = f.rstrip('xml')
        root = etree.Element('Document', doc_name=catdir+cfname+'.txt')
        create_tokens(nafobj, root)
        
        markables = etree.SubElement(root, 'Markables')
        create_markables(nafobj, markables)
        
        my_out = etree.tounicode(root, pretty_print=True)
        outfile = open(catdir+cfname+'txt.xml', 'w')
        print(my_out, file=outfile)



def main(argv=None):
    
    
    if argv==None:
        argv = sys.argv
    
    if len(argv) < 3:
        nafobj = KafNafParser(sys.stdin)
        create_catfile(nafobj)
    elif len(argv) < 4:
        create_catfiles(argv[1], argv[2])

if __name__ == '__main__':
    main()