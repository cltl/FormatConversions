from KafNafParserPy import *
from lxml import etree
import sys
import os



def get_token_id_from_term(nafobj, termId):

    term = nafobj.get_term(termId)
    tokenId = term.get_span().get_span_ids()[0]
    return tokenId

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

def add_mention(pred, markables, mid, mention_type):

    mark = etree.SubElement(markables, mention_type, m_id=str(mid))
    pred_span = pred.get_span().get_span_ids()
    for tid in pred_span:
        toch_anch = etree.SubElement(mark, 'token_anchor', t_id=tid.lstrip('t'))

def add_entity_mention(role, markables, mid):
    
    mark = etree.SubElement(markables, 'EVENT_MENTION', m_id=str(mid), )
    role_span = role.get_span().get_span_ids()
    for tid in role_span:
        toch_anch = etree.SubElement(mark, 'token_anchor', t_id=tid.lstrip('t'))


def add_participant_relation(relations, source, target,semrole):

    rel = etree.SubElement(relations, 'HAS_PARTICIPANT', r_id=str(mid))


def create_markables(nafobj, markables):
    '''
        Create markables and stores information needed for relations
        Dictionary has target mid as key (they are unique in this case, sources are not)
    '''
    mid = 1
    relations = {}
    for pred in nafobj.get_predicates():
        add_mention(pred, markables, mid, 'EVENT_MENTION')
        pid = str(mid)
        mid +=1
        for role in pred.get_roles():
            add_mention(role, markables, mid, 'ENTITY_MENTION')
            rid = mid
            relations[rid] = [pid, role.get_sem_role()]
            mid += 1
    return relations, mid


def create_relations(relations, rel_dict, mid):
    '''
        adds relations based on rel_dict output
    '''
    for k, val in sorted(rel_dict.items()):
        relation = etree.SubElement(relations, 'HAS_PARTICIPANT', r_id=str(mid), sem_role=val[1])
        mid += 1
        source = etree.SubElement(relation, 'source', m_id=val[0])
        target = etree.SubElement(relation, 'target', m_id=str(k))



def create_catfile(nafobj):
    filename = nafobj.get_header().get_fileDesc().get_filename()
    if filename is None:
        filename = 'unknown'
    root = etree.Element('Document', doc_name=filename)
    create_tokens(nafobj, root)
    #create event mention markables; here the srl predicates
    markables = etree.SubElement(root, 'Markables')
    rel_dict, mid = create_markables(nafobj, markables)
    
    relations = etree.SubElement(root, 'Relations')
    create_relations(relations, rel_dict, mid)

    print(etree.tounicode(root, pretty_print=True))


def create_catfiles(nafdir, catdir):


    for f in os.listdir(nafdir):
        nafobj = KafNafParser(nafdir + f)
        cfname = f.rstrip('naf')
        root = etree.Element('Document', doc_name=catdir+cfname+'.txt')
        create_tokens(nafobj, root)
    
        markables = etree.SubElement(root, 'Markables')
        rel_dict, mid = create_markables(nafobj, markables)
    
        relations = etree.SubElement(root, 'Relations')
        create_relations(relations, rel_dict, mid)


# number = 0
        #create token layer
        #       for tok in nafobj.get_tokens():
        #    token = tok.get_text()
        #    sent = tok.get_sent()
        #    tokId = tok.get_id().lstrip('w')
        #    child = etree.SubElement(root, 'token', t_id=tokId, sentence=sent, number=str(number))
        #    child.text = token
        #    number += 1
        #create event mention markables
        #      markables = etree.SubElement(root, 'Markables')
        #  mid = 1
        #for fact_obj in nafobj.get_factualities():
        ##    termId = fact_obj.get_span().get_span_ids()[0]
        #   tokId = get_token_id_from_term(nafobj, termId)
        #   for factVal in fact_obj.get_factVals():
        #        fcertain = 'UNKNOWN'
        #        fpolarity = 'UNKNOWN'
        #        ftime = 'UNKNOWN'
        #        if 'Certainty' in factVal.get_resource():
        #            fcertain = factVal.get_value()
        #        if 'Tense' in factVal.get_resource():
        #            ftime = factVal.get_value()
        #        if 'Polarity' in factVal.get_resource():
        #            fpolarity = factVal.get_value()
        #       mark = etree.SubElement(markables, 'EVENT_MENTION', certainty=fcertain, polarity=fpolarity, time=ftime, m_id=str(mid))
        #       mid += 1
        #        tok_anch = etree.SubElement(mark, 'token_anchor', t_id=tokId.lstrip('w'))
        
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