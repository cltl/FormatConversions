from lxml import etree
import sys
import os





def take_over_tokens(root, cattree):
    
    
    for token in cattree.findall('token'):
        child = etree.SubElement(root, 'token', t_id=token.get('t_id'), sentence=token.get('sentence'), number=token.get('number'))
        child.text = token.text





def take_over_markable(newmarkables, markable):

    newmark = etree.SubElement(newmarkables, markable.tag)
    for att, val in markable.items():
        newmark.set(att, val)
    for tanch in markable.findall('token_anchor'):
            #original input naf generated from CAT, token numbers match
        tid = tanch.get('t_id')
        toch_anch = etree.SubElement(newmark, 'token_anchor', t_id=tid)

def derive_markables(root, cattree):


    markables = cattree.find('Markables')
    newmarkables = etree.SubElement(root, 'Markables')
    events = []
    counter=0
    for mark in markables:
        for k, a in mark.items():
            if a == "":
                take_over_markable(newmarkables, mark)
                counter += 1
                break
    return counter



def convert_file(inputfile):
    
    parser = etree.XMLParser(ns_clean=True)
    cattree = etree.parse(inputfile, parser)
    
    filename = inputfile.split('/')[-1].rstrip('.xml')
    root = etree.Element('Document', doc_name=filename)
    take_over_tokens(root, cattree)
    counter = derive_markables(root, cattree)
    
    return root, counter




def convert_single_file():
    
    print('Sorry...to appear...')




def convert_directory(inputdir, outputdir):
    
    
    for f in os.listdir(inputdir):
        if f.endswith('.xml'):
            print(f)
            newcat, counter = convert_file(inputdir + f)
            if counter > 0:
                print(counter)
                my_out = etree.tounicode(newcat, pretty_print=True)
                outfile = open(outputdir+f, 'w')
                print(my_out, file=outfile)





def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    if len(argv) < 1:
        print('Usage for file: cat input.xml | python cat2cat_missing_attributes.py > output.xml')
        print('Usage for directory: python cat2cat_missing_attributes.py inputdir/ outputdir/')
    elif len(argv) < 2:
        convert_single_file()
    else:
        convert_directory(argv[1], argv[2])


if __name__ == '__main__':
    main()