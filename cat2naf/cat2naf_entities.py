import sys
import os
from KafNafParserPy import *
from lxml import etree


class catMarkable:
    '''class for markable information'''

    def __init__(self, span=[], etype = ''):
        """
        Constructor of the object
        @param span: list of tokens forming the span
        @param mtype: named entity class
        """
        self.span = span
        self.etype = etype



def get_markable_span(markable):

    span = []
    for tanch in markable.findall('token_anchor'):
        span.append(tanch.get('t_id'))

    return span


def collect_markables(catfile):
    '''
    Function that collects markables, their type and span
    Note: assumes relevant markables are called 'NAMEDENTITY' and have an attribute 'type'
    :param catfile: CAT xml file
    :return: list of catMarkables
    '''

    my_markables = []
    #go through catfile and collect span + type of each markable

    parser = etree.XMLParser(ns_clean=True)
    cattree = etree.parse(catfile, parser)
    markables = cattree.find('Markables')
    for markable in markables.findall('NAMEDENTITY'):
        etype = markable.get('type')
        mspan = get_markable_span(markable)
        cmarkable = catMarkable(mspan, etype)
        my_markables.append(cmarkable)


    return my_markables


def create_token_to_term_dict(nafobj):

    tok2term = {}

    for term in nafobj.get_terms():
        tspan = term.get_span().get_span_ids()
        for token in tspan:
            if not token in tok2term:
                tok2term[token] = term.get_id()
            else:
                print(token, 'part of multiple term spans')
    return tok2term


def convert_to_nafspan(tok2term, catspan):

    nafspan = []
    for tokId in catspan:
        termId = tok2term.get('w' + tokId)
        if termId is None:
            print('Error:', tokId, 'does not occur in naffile')
        else:
            nafspan.append(termId)
    return nafspan

def create_reference(nafspan):

    myRefs = Creferences()
    myRefs.add_span(nafspan)

    return myRefs

def add_entities_to_naf(catmarkables, nafin):

    nafobj = KafNafParser(nafin)
    tok2term = create_token_to_term_dict(nafobj)
    entity_nr = 1
    for markable in catmarkables:
        nafspan = convert_to_nafspan(tok2term, markable.span)
        nafentity = Centity()
        #set identifier
        nafentity.set_id('e' + str(entity_nr))
        entity_nr += 1
        #set type
        nafentity.set_type(markable.etype)
        #set reference (including span)
        nafref = create_reference(nafspan)
        nafentity.add_reference(nafref)

        nafobj.add_entity(nafentity)

    return nafobj

def convert_file(catfile, nafin, nafout):


    catmarkables = collect_markables(catfile)
    #go through markables and add to naffile
    nafobj = add_entities_to_naf(catmarkables, nafin)
    nafobj.dump(nafout)




def main(argv=None):

    if argv is None:
        argv = sys.argv


    if len(argv) < 4:
        print('Usage: python cat2naf_entities.py catfile.xml naffile.naf outfile.naf')
    else:
        convert_file(argv[1], argv[2], argv[3])



if __name__ == '__main__':
    main()