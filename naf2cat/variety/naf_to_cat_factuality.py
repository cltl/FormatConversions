from KafNafParserPy import *
from lxml import etree
import sys
import os



def get_token_id_from_term(nafobj, termId):

    term = nafobj.get_term(termId)
    tokenId = term.get_span().get_span_ids()[0]
    return tokenId


def create_catfile(nafobj):

    root = etree.Element('Document', doc_name='unknown')
    number = 0
    #create token layer
    for tok in nafobj.get_tokens():
        token = tok.get_text()
        sent = tok.get_sent()
        tokId = tok.get_id().lstrip('w')
        child = etree.SubElement(root, 'token', t_id=tokId, sentence=sent, number=str(number))
        child.text = token
        number += 1
    #create event mention markables
    markables = etree.SubElement(root, 'Markables')
    mid = 1
    for fact_obj in nafobj.get_factualities():
        termId = fact_obj.get_span().get_span_ids()[0]
        tokId = get_token_id_from_term(nafobj, termId)
            
        fcertain = 'UNKNOWN'
        fpolarity = 'UNKNOWN'
        ftime = 'UNKNOWN'
        for factVal in fact_obj.get_factVals():
            if 'Certainty' in factVal.get_resource():
                fcertain = factVal.get_value()
            if 'Tense' in factVal.get_resource():
                ftime = factVal.get_value()
            if 'Polarity' in factVal.get_resource():
                fpolarity = factVal.get_value()
        mark = etree.SubElement(markables, 'EVENT_MENTION', certainty=fcertain, polarity=fpolarity, time=ftime,m_id=str(mid))
        mid += 1
        tok_anch = etree.SubElement(mark, 'token_anchor', t_id=tokId.lstrip('w'))

    print(etree.tounicode(root, pretty_print=True))


def create_catfiles(nafdir, catdir):


    for f in os.listdir(nafdir):
        nafobj = KafNafParser(nafdir + f)
        cfname = f.rstrip('naf')
        root = etree.Element('Document', doc_name=catdir+cfname)
        number = 0
        #create token layer
        for tok in nafobj.get_tokens():
            token = tok.get_text()
            sent = tok.get_sent()
            tokId = tok.get_id().lstrip('w')
            child = etree.SubElement(root, 'token', t_id=tokId, sentence=sent, number=str(number))
            child.text = token
            number += 1
        #create event mention markables
        markables = etree.SubElement(root, 'Markables')
        mid = 1
        for fact_obj in nafobj.get_factualities():
            termId = fact_obj.get_span().get_span_ids()[0]
            tokId = get_token_id_from_term(nafobj, termId)
            for factVal in fact_obj.get_factVals():
                fcertain = 'UNKNOWN'
                fpolarity = 'UNKNOWN'
                ftime = 'UNKNOWN'
                if 'Certainty' in factVal.get_resource():
                    fcertain = factVal.get_value()
                if 'Tense' in factVal.get_resource():
                    ftime = factVal.get_value()
                if 'Polarity' in factVal.get_resource():
                    fpolarity = factVal.get_value()
                mark = etree.SubElement(markables, 'EVENT_MENTION', certainty=fcertain, polarity=fpolarity, time=ftime, m_id=str(mid))
                mid += 1
                tok_anch = etree.SubElement(mark, 'token_anchor', t_id=tokId.lstrip('w'))
        
        my_out = etree.tounicode(root, pretty_print=True)
        print(my_out)
        #mycat = open(catdir + cfname,'w')
        #mycat.write(my_out)
#mycat.close()


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