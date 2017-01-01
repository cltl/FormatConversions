from KafNafParserPy import *
from lxml import etree
import sys
import os




def create_tok_to_term_dict(nafobj):

    tok2term = {}
    for term in nafobj.get_terms():
        tspan = term.get_span().get_span_ids()
        #spans of terms almost always have length 1 and tokens are only part of one term
        tok2term[tspan[0]] = term.get_id()

    return tok2term


def check_correspondance(events, coreferspan):
    corefset = set(coreferspan)
    for event in events:
        evset = set(event)
        if len(corefset.symmetric_difference(evset)) == 0:
            return evset
    return []


def updated_events(events, found_events):
    unfound_events = []
    for event in events:
        evset = set(event)
        found = False
        for fevent in found_events:
            fevset = set(fevent)
            if len(fevset.symmetric_difference(evset)) == 0:
                found = True
        if not found:
            unfound_events.append(event)
    return unfound_events


def adapt_header(nafobj):


    for this_node in nafobj.header.node.findall('linguisticProcessors'):
        if this_node.get('layer') == 'coreferences':
            for lp in this_node.findall('lp'):
                if 'vua-event' in lp.get('name'):
                    this_node.remove(lp)
            mynewlp = Clp(name='meantime_gold',version='oct2015')
            nafobj.add_linguistic_processor('coreferences',mynewlp)


def integrate_catevents_into_naf(nafobj, cattree, nafout):

    tok2term = create_tok_to_term_dict(nafobj)
    markables = cattree.find('Markables')
    events = []
    for mark in markables.findall('EVENT_MENTION'):
        terms=[]
        for tanch in mark.findall('token_anchor'):
            #original input naf generated from CAT, token numbers match
            tid = tanch.get('t_id')
            termId = tok2term['w' + tid]
            terms.append(termId)
        events.append(terms)

    #go through coreferences and remove events not in gold
    found_events = []
    removed = []
    
    coref_count = 1
    for coref in nafobj.get_corefs():
        coref_count += 1
        if coref.get_type() == 'event':
            span_found = False
            spans = coref.get_spans()
            for span in spans:
                my_terms = span.get_span_ids()
                matching_event = check_correspondance(events, my_terms)
                if len(matching_event) > 0:
                    found_events.append(matching_event)
                    span_found = True
                else:
                    coref.remove_span(span)
                    removed.append(my_terms)
            if not span_found:
                nafobj.coreference_layer.remove_coreference(coref.get_id())

    unfound_events = updated_events(events, found_events)
    for event in unfound_events:
        mycoref = Ccoreference()
        mycoref.set_id('coevent' + str(coref_count))
        coref_count += 1
        mycoref.add_span(event)
        mycoref.set_type('event')
        nafobj.add_coreference(mycoref)
    adapt_header(nafobj)
    nafobj.dump(nafout)


def create_gold_event_nafs_from_cat(nafin, catin, nafout):

    parser = etree.XMLParser(ns_clean=True)
    for f in os.listdir(nafin):
        nafobj = KafNafParser(nafin + f)
        cfn = f.rstrip('.naf')
        cattree = etree.parse(catin + cfn, parser)
        integrate_catevents_into_naf(nafobj, cattree, nafout + f)





def main(argv=None):
    
    if argv==None:
        argv = sys.argv
    
    if len(argv) < 4:
        print('USAGE: python integrate_cat_gold_events_in_naf.py NAFdir CATdir OUTdir')
    else:
        create_gold_event_nafs_from_cat(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    main()




