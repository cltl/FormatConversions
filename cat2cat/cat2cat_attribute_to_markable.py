from lxml import etree
import sys
import os



def take_over_tokens(root, cattree):


    for token in cattree.findall('token'):
        child = etree.SubElement(root, 'token', t_id=token.get('t_id'), sentence=token.get('sentence'), number=token.get('number'))
        child.text = token.text


def derive_markables(root, cattree, markable, attribute):

    markables = cattree.find('Markables')
    newmarkables = etree.SubElement(root, 'Markables')
    events = []
    for mark in markables.findall(markable):
        newmarkname = mark.get(attribute)
        if newmarkname is None or newmarkname == '':
            newmarkname = 'FORGOTTEN'
        newmark = etree.SubElement(newmarkables, newmarkname, m_id=mark.get('m_id'))
        for tanch in mark.findall('token_anchor'):
            #original input naf generated from CAT, token numbers match
            tid = tanch.get('t_id')
            toch_anch = etree.SubElement(newmark, 'token_anchor', t_id=tid)



def convert_file(inputfile, markable, attribute):

    parser = etree.XMLParser(ns_clean=True)
    cattree = etree.parse(inputfile, parser)

    filename = inputfile.split('/')[-1].rstrip('.xml')
    root = etree.Element('Document', doc_name=filename)
    take_over_tokens(root, cattree)
    derive_markables(root, cattree, markable, attribute)

    return root



def convert_single_file(markable, attributename):

    print('Sorry...to appear...')


def convert_directory(markable, attribute, inputdir, outputdir):


    for f in os.listdir(inputdir):
        if f.endswith('.xml'):
            print(f)
            newcat = convert_file(inputdir + f, markable, attribute)
            my_out = etree.tounicode(newcat, pretty_print=True)
            outfile = open(outputdir+f, 'w')
            print(my_out, file=outfile)


def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage for file: cat input.xml | python cat2cat_attribute_to_markable.py markable attributename > output.xml')
        print('Usage for directory: python cat2cat_attribute_to_markable.py markable attributename inputdir/ outputdir/')
    elif len(argv) < 4:
        convert_single_file(argv[1], argv[2])
    else:
        convert_directory(argv[1], argv[2], argv[3], argv[4])


if __name__ == '__main__':
    main()