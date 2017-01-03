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



def identify_entities(nafobj):

    myentities = []
    for entity in nafobj.get_entities():
        for ref in entity.get_references():
            myspan = ref.get_span().get_span_ids()
            myentities.append(myspan)

    return myentities




def get_entity_annotations(infile, name, outfile=None, number=1):

    nafobj = KafNafParser(infile)
    entities = identify_entities(nafobj)
    tokeninfo = get_token_info(nafobj, entities)
    write_output(tokeninfo, number, name, outfile)




def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print('Usage:\n cat infile | python entities_to_brat.py MARKABLENAME > outfile \n python entities_to_brat.py infile outfile MARKABLENAME (number)')
    elif len(argv) < 4:
        infile = sys.stdin
        get_entity_annotations(infile, argv[1])
    elif len(argv) < 5:
        get_entity_annotations(argv[1], argv[3], argv[2])
    else:
        get_entity_annotations(argv[1], argv[3], argv[2], argv[4])



if __name__ == '__main__':
    main()

