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



def create_catfile(nafobj):
    filename = create_file_name(nafobj, 'unknown.txt')
    root = etree.Element('Document', doc_name=filename)
    create_tokens(nafobj, root)
    

    print(etree.tounicode(root, pretty_print=True))

def create_file_name(nafobj, inputfile):

    filename = inputfile
    if '.naf' in inputfile:
        filename = inputfile.replace('.naf','.txt')
    nafheader = nafobj.get_header()
    if nafheader is not None:
        fileDesc = nafheader.get_fileDesc()
        if fileDesc is not None:
            filename = fileDesc.get_filename()
    if filename is None:
        filename = 'unknown.txt'
    if '.xml' in filename:
        filename = filename.replace('.xml','.txt')
    return filename

def create_catfiles(nafdir, catdir):


    for f in os.listdir(nafdir):
        nafobj = KafNafParser(nafdir + f)
        if '.naf' in f:
            cfname = f.replace('.naf','.txt')
        elif '.txt' in f:
            cfname = f
        else:
            cfname = f + '.txt'
        root = etree.Element('Document', doc_name=cfname)
        filename = create_file_name(nafobj, f)
        create_tokens(nafobj, root)
    
    #markables = etree.SubElement(root, 'Markables')
    #   rel_dict, mid = create_markables(nafobj, markables)
    
    #   relations = etree.SubElement(root, 'Relations')
    #    create_relations(relations, rel_dict, mid)
        
        my_out = etree.tounicode(root, pretty_print=True)
        outfile = open(catdir+cfname+'.xml', 'w')
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