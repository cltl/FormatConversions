from lxml import etree
import sys
import os


def create_token_dict(cat):

    mytoks = {}
    for token in cat.findall('token'):
        tid = token.get('t_id')
        mytoks[int(tid)] = [token.get('number'), token.get('sentence'), token.text]
    return mytoks


def map_tokens(newcat, oldcat, root):

    oldtoks = create_token_dict(oldcat)
    for token in newcat.findall('token'):
        mytid = int(token.get('t_id'))
        if mytid in oldtoks:
            oldinfo = oldtoks.get(mytid)
            if oldinfo[-1] == token.text:
                newtok = etree.SubElement(root, 'token', number=token.get('number'), sentence=token.get('sentence'), t_id=str(mytid))
                newtok.text = token.text
            else:
                print(oldinfo[-1],token.text)
                #print for now assuming correspondance in tokenization
                print('WARNING TOKEN MISMATCH')
    return oldtoks


def add_markables_from_file(markables, newcat, mid):

    omarkables = newcat.find('Markables')
    for mark in omarkables.getchildren():
        newmark = mark
        newmark.set('m_id',str(mid))
        mid += 1
    return mid



def create_new_cat_from_files(nf, of, outf):
    
    parser = etree.XMLParser(ns_clean=True)
    newcat = etree.parse(nf, parser)
    origcat = etree.parse(of, parser)
    
    
    root = etree.Element('Document', doc_name=outf)
    oldtoks = map_tokens(newcat, origcat, root)
    markables = etree.SubElement(root, 'Markables')
    mid = add_markables_from_file(markables, newcat, 1)
    #2. add markables file 1 and count
    #3. add markables file 2 from count point.

    return 'catfile'


def merge_directory(ndir, odir, outdir):

    for f in os.listdir(ndir):
        if f.endswith('.xml'):
            if os.path.exists(odir + f):
                catfile = create_new_cat_from_files(ndir + f, odir + f, outdir + f)




def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    if len(argv) < 3:
        print('Usage for directory: python cat2cat_merge_annotations.py newdir/ originaldir/' 'outdir/')
    else:
        merge_directory(argv[1], argv[2], argv[3])


if __name__ == '__main__':
    main()