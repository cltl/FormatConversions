import sys
from KafNafParserPy import *





def get_tokids(np, nafobj):
    '''Returns list of token numbers'''
    toks = []
    for term in np:
        myterm = nafobj.get_term(term)
        termtoks = myterm.get_span().get_span_ids()
        for tok in termtoks:
            toks.append(int(tok.lstrip('w')))
    return toks



def get_token_info(nafobj, nps):

    tokensInfo = []
    for np in nps:
        beginoffset = None
        np_string = ''
        toks = get_tokids(np, nafobj)
        for toknr in sorted(toks):
            token = nafobj.get_token('w' + str(toknr))
            offset = token.get_offset()
            if beginoffset is None:
                beginoffset = offset
                endoffset = int(offset) + int(token.get_length())
            if int(offset) > endoffset:
                np_string += ' '
            np_string += token.get_text()
            endoffset = int(offset) + int(token.get_length())
        tokenInf = [beginoffset, str(endoffset), np_string]
        tokensInfo.append(tokenInf)
    return tokensInfo





def identify_nps(nafobj):

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

    return nps

def write_output(tokeninfo, number, name, outfile):

    lines = []
    for tok in tokeninfo:
        line = 'T' + str(number) + '\t' + name + '\t' + tok[0] + '\t' + tok[1] + '\t' + tok[2]
        number += 1
        lines.append(line)


    if outfile is None:
        for line in lines:
            print(line)
    else:
        myout = open(outfile, 'w')
        for line in lines:
            myout.write(line.encode('utf8') + '\n')
        myout.close()

def get_np_annotations(infile, name, outfile=None, number=1):

    nafobj = KafNafParser(infile)
    nps = identify_nps(nafobj)
    tokeninfo = get_token_info(nafobj, nps)
    write_output(tokeninfo, number, name, outfile)

def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print('Usage:\n cat infile | python nps_to_brat.py MARKABLENAME > outfile \n python nps_to_brat.py infile outfile MARKABLENAME (number)')
    elif len(argv) < 4:
        infile = sys.stdin
        get_np_annotations(infile, argv[1])
    elif len(argv) < 5:
        get_np_annotations(argv[1], argv[3], argv[2])
    else:
        get_np_annotations(argv[1], argv[3], argv[2], argv[4])



if __name__ == '__main__':
    main()

