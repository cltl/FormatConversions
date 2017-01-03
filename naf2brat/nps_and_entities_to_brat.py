import sys
from nps_to_brat import *
from entities_to_brat import *






def get_np_and_entities_annotations(infile, name, outfile=None, number=1):


    nafobj = KafNafParser(infile)
    nps = identify_nps(nafobj)
    entities = identify_entities(nafobj)
    all_entities = nps + entities

    tokeninfo = get_token_info(nafobj, all_entities)
    write_output(tokeninfo, number, name, outfile)






def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print(
        'Usage:\n cat infile | python nps_and_entities_to_brat.py MARKABLENAME > outfile \n python nps_and_entities_to_brat.py infile outfile MARKABLENAME (number)')
    elif len(argv) < 4:
        infile = sys.stdin
        get_np_and_entities_annotations(infile, argv[1])
    elif len(argv) < 5:
        get_np_and_entities_annotations(argv[1], argv[3], argv[2])
    else:
        get_np_and_entities_annotations(argv[1], argv[3], argv[2], argv[4])



if __name__ == '__main__':
    main()
