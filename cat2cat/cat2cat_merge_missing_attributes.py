from lxml import etree
import sys
import os


def get_token_list(mark):
    
    tanch = ''
    for token in mark.findall('token_anchor'):
        tanch += token.get('t_id')

    return tanch


def create_annotation_dict(fname):

    parser = etree.XMLParser(ns_clean=True)
    correctedcat = etree.parse(fname, parser)

    mark_dict = {}
    markables = correctedcat.find('Markables')
    for mark in markables:
        mtype = mark.get('type')
        tokenerr = mark.get('tokenization_error')
        tanch = get_token_list(mark)
        mark_dict[tanch] = [mtype, tokenerr]
    
                  
    return mark_dict


def merge_annotations(originfile, corrected_mark, outfname):
        
    parser = etree.XMLParser(ns_clean=True)
    correctedcat = etree.parse(originfile, parser)
                  
    markables = correctedcat.find('Markables')
    for mark in markables:
        tanch = get_token_list(mark)
        if tanch in corrected_mark:
            corrected_values = corrected_mark.get(tanch)
            mark.set('type', corrected_values[0])
            mark.set('tokenization_error', corrected_values[1])
        
 
    my_out = etree.tounicode(correctedcat, pretty_print=True)
    outfile = open(outfname, 'w')
    print(my_out, file=outfile)
                  

def merge_directory(cordir, oridir, outdir):

    for f in os.listdir(cordir):
        if f.endswith('xml'):
            corrected_mark = create_annotation_dict(cordir + f)
            merge_annotations(oridir + f, corrected_mark, outdir + f)



def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    if len(argv) < 3:
        print('Usage for directory: python cat2cat_missing_attributes.py correctedir/ originaldir/' 'outdir/')
    else:
        merge_directory(argv[1], argv[2], argv[3])


if __name__ == '__main__':
    main()