import sys
import os
from lxml import etree


version = 0.1


def get_text(infile):

    bioportxml = etree.parse(infile)
    text = bioportxml.find('biography/text').text

    return text.encode('utf8')



def extract_clean_utf_8_from_text(infile, outfile = None):

    text = get_text(infile)
    if outfile is None:
        print(text)
    else:
        myoutfile = open(outfile, 'wb')
        myoutfile.write(text)


def extract_clean_utf_8_from_text_in_dir(indir, outdir):
    '''
        Function that loops through directory and extracts texts from every bioport file in the directory
    '''
    for f in os.listdir(indir):
        text = get_text(indir + f)
        myoutfile = open(outdir + f.replace('.xml','.txt'), 'wb ')
        myoutfile.write(text)


def generate_prov_information():

    



def main():

    argv = sys.argv

    if len(argv) < 2:
        extract_clean_utf_8_from_text(sys.stdin)
    elif len(argv) < 3:
        extract_clean_utf_8_from_text(sys.stdin, argv[1])
    else:
        extract_clean_utf_8_from_text_in_dir(argv[1], argv[2])



if __name__ == '__main__':
    main()
