from KafNafParserPy import *
from xml.etree.ElementTree import ElementTree
from collections import defaultdict
import sys
import os



version = "0.1"
pid = 0
sid = 0

missed_rels = 0


class cDependent():
    '''
    Class that captures structure of dependents for multiword descriptions
    '''

    def __init__(self,from_id, to_id, rel):
        '''
        Initiates dependent
        :param dep_id: identifier of dependent (term id)
        :param form: surface form or lemma
        :param rel: dependency relation to head
        '''

        self.from_id = from_id
        self.to_id = to_id
        self.rel = rel
        self.lemma_from = ''
        self.lemma_to = ''



def get_tokens(alpino_node, word_count, token_dict = {}, highest_count = 0):
    #identifier = word_count
    for child in alpino_node.getchildren():
        if child.get('word') is not None:
            identifier = int(child.get('begin')) + word_count
            if identifier > highest_count:
                highest_count = identifier
            token_dict[identifier] = [child.get('word'), child.get('lemma'), child.get('pos'), child.get('postag')]
        token_dict, highest_count = get_tokens(child, word_count, token_dict, highest_count)
    return token_dict, highest_count + 1


def get_constituent(alpino_node, word_count, words=[]):
    
    for child in alpino_node.getchildren():
        if child.get('word') is not None:
            if len(words) < 1:
                words.append([])
            identifier = int(child.get('begin')) + word_count
            words[0].append('t' + str(identifier))
            #FIXME: this is not the right way to identify the head (ignoring for now)
            if child.get('rel') == 'hd' and len(words) < 2:
                words.append('t' + str(identifier))
        else:
            words = get_constituent(child, word_count, words)
    return words

def create_span(target_ids):

    span = Cspan()
    span.create_from_ids(target_ids)

    return span

def add_role(pred, role, span):
    
    global sid
    
    sid += 1
    s_id = 's' + str(sid)

    my_role = Crole()
    my_role.set_id(s_id)
    my_role.set_sem_role(role)
    rspan = create_span(span)
    my_role.set_span(rspan)
    pred.add_role(my_role)


def add_pb_obj_to_naf(nafobj, pbdict):
    global pid
    
    pid += 1
    p_id = 'p' + str(pid)
    mypred = Cpredicate()
    mypred.set_id(p_id)
    pspan = create_span(pbdict.get('rel')[0][0])
    mypred.set_span(pspan)
    for k, val in pbdict.items():
        if not k == 'rel':
            for v in val:
                if len(v) > 0:
                    add_role(mypred, k, v[0])
    nafobj.add_predicate(mypred)




def find_propbank_rels(elem, nafobj, word_count):

    global missed_rels
    
    pb_dict = {}
    for ch in elem.getchildren():
        pb = ch.get('pb')
        if pb is not None:
            myconstituent = []
            if ch.get('word') is None:
                myconstituent = get_constituent(ch, word_count, myconstituent)
            else:
                identifier = int(ch.get('begin')) + word_count
                myconstituent = [['t' + str(identifier)], ch.get('begin')]
            if not pb in pb_dict:
                pb_dict[pb] = [myconstituent]
            else:
                pb_dict[pb].append(myconstituent)
    
        find_propbank_rels(ch, nafobj, word_count)

    if 'rel' in pb_dict:
        add_pb_obj_to_naf(nafobj, pb_dict)
    else:
        missed_rels += len(pb_dict)


def identify_head_and_dependents(elem, word_count, deps, indeces):

    head_node = None
    dep_word = None
    local_deps = defaultdict(list)
    equal_rel = False
    for ch in elem.getchildren():
        dep_rel = ch.get('rel')
        if dep_rel in ['hd','cmp','mwp','rhd','crd','dp','nucl','cnj','whd'] and not equal_rel:

            if ch.get('word') is None:
                if ch.get('index') is not None:
                    my_head_node = indeces.get('index_' + ch.get('index'))
                    head_node = my_head_node[0]
                    head_word = my_head_node[1]
                else:
                    head_node, head_rel, head_word = identify_head_and_dependents(ch, word_count, deps, indeces)
            else:
                head_word = ch.get('word')
                head_node = int(ch.get('begin')) + word_count
            head_rel = dep_rel
            if not ch.get('index') is None:
                indeces['index_' + ch.get('index')] = [head_node, head_word]

            if dep_rel in ['mwp','dp']:
                equal_rel = True
        else:
            #if this is a node, then analyze local tree
            if ch.get('word') is None:
                if len(ch.getchildren()) > 0:
                    dependent_id, dep_head_rel, dep_word = identify_head_and_dependents(ch, word_count, deps, indeces)
                    if not ch.get('index') is None:
                        indeces['index_' + ch.get('index')] = [dependent_id, dep_word]
                elif ch.get('index') is not None:
                    dependent_id = 'index_' + ch.get('index')
            else:
                dependent_id = int(ch.get('begin')) + word_count
                dep_word = ch.get('word')
                if not ch.get('index') is None:
                    indeces['index_' + ch.get('index')] = [dependent_id, dep_word]
            if dependent_id in local_deps:
                old_info = local_deps.get(dependent_id)[0]
                if old_info[0] != dep_rel or old_info[1] != dep_word:
                    print('problem: multiple relations in local dependency')
                    print(dependent_id, local_deps.get(dependent_id), dep_rel, dep_word)
            local_deps[dependent_id].append([dep_rel, dep_word])

    if head_node is None and elem.get('index') is not None:
        my_head_node = indeces.get('index_' + elem.get('index'))
        head_node = my_head_node[0]
        head_word = my_head_node[1]

    #example found where head was indeed missing (grammar error)
    if head_node is None:
        for ch in elem.getchildren():
            print(ch.get('rel'), 'grandchildren trick (should only be employed when head is truly missing)', ch.get('id'))
            for gch in ch.getchildren():
                if gch.get('rel') in ['hd','rhd','whd']:
                    #otherwise function get head
                    head_word = gch.get('word')
                    head_node = int(gch.get('begin')) + word_count
                    head_rel = elem.get('rel')
        if head_node is None:
            #hack: example of non-headed phrase consisting of a determiner and modifiers
            head_node = int(ch.get('begin')) + word_count
            head_word = ch.get('word')
            head_rel = ch.get('rel')
            print('CHECK THIS FILE')

    if head_node is None:
        print('Error: no head node identified even for looking at grandchildren', elem.get('id'))

    else:
        for dep_id, relations in local_deps.items():
            for rel_word in relations:
                dep_word = rel_word[1]
                if type(dep_id) is str:
                    dep_info = indeces.get(dep_id)
                    dep_id = dep_info[0]
                    dep_word = dep_info[1]
                if not dep_id is None:
                    dependency = cDependent(head_node, dep_id,head_rel + '/' + rel_word[0])
                    dependency.lemma_from = head_word
                    dependency.lemma_to = dep_word
                    deps[dep_id].append(dependency)
                else:
                    print(dep_id,head_node,rel,'dep_id is None')

        return head_node, head_rel, head_word


def remove_duplicates(deps):

    unique_deps = defaultdict(list)
    for dep_id, rels in deps.items():
        found_pairs = []
        for rel in rels:
            rel_description = str(rel.from_id) + rel.rel
            if not rel_description in found_pairs:
                unique_deps[dep_id].append(rel)
                found_pairs.append(rel_description)
    return unique_deps


def identify_head(elem, indeces, word_count):
    '''
    Function that identifies the head word and identifier of a node
    :param elem: node whose head is sought
    :return: head_word as string and identifier as integer
    '''

    for ch in elem.getchildren():
        if ch.get('rel') in ['hd','cmp','mwp','rhd','crd','dp','nucl','cnj','whd']:
            word = ch.get('word')
            local_id = int(ch.get('begin'))
            if word is None:
                if ch.get('index') is not None:
                    index_id = 'index_' + ch.get('index')
                    if index_id in indeces:
                        known_info = indeces.get(index_id)
                        word = known_info[1]
                        local_id = known_info[0] - word_count
            if word is None:
                word, local_id = identify_head(ch, indeces, word_count)

            return word, local_id
    #A bit of a hack, but only example found so far of no head being found meant that the head was indeed missing...
  #  for ch in elem.getchildren():
  #      for gch in ch.getchildren():
  #          word, local_id = identify_head(gch)
  #          return word, local_id
    print(elem.get('id'))
    print('Error: no head was found or word was None')


def collect_indeces(elem, indeces, word_count):
    '''
    Function that collects all index information for description
    :param elem: input xml for Alpino
    :return:
    '''
    for ch in elem.getchildren():
        if ch.get('index') is not None:
            #stored as integer, later summed with word count
            local_id = int(ch.get('begin')) + word_count
            word = ch.get('word')
            index_id = 'index_' + ch.get('index')
            if index_id not in indeces:
                if word is not None:
                    indeces[index_id] = [local_id, word]
                elif len(ch.getchildren()) > 0:
                    word, local_id = identify_head(ch, indeces, word_count)
                    indeces[index_id] = [local_id + word_count, word]

        collect_indeces(ch, indeces, word_count)



def add_dependencies_to_naf(elem, nafobj, word_count):

    deps = defaultdict(list)
    indeces = {}
    collect_indeces(elem, indeces, word_count)
    for ch in elem.getchildren():
        if ch.get('rel') == '--' and len(ch.getchildren()) > 0:
            identify_head_and_dependents(ch,word_count,deps,indeces)

    deps = remove_duplicates(deps)
    for dependent_id, head_rels in sorted(deps.items()):
        for rel_info in head_rels:
            naf_dependency = Cdependency()
            try:
                comment = ' '+rel_info.rel+'('+rel_info.lemma_from+','+rel_info.lemma_to+') '
            except:
                print(rel_info.rel, rel_info.lemma_from, rel_info.lemma_to)
            naf_dependency.set_comment(comment)
            naf_dependency.set_from('t' + str(rel_info.from_id))
            naf_dependency.set_to('t' + str(dependent_id))
            naf_dependency.set_function(rel_info.rel)
            nafobj.add_dependency(naf_dependency)


def create_token_and_term_layer(token_dict, token_info, nafobj):

    global offset
    
    for idnr, val in sorted(token_dict.items()):
        if offset != 0:
            offset += 1
        word_id = 'w' + str(idnr)
        tok = Cwf(type="NAF")
        tok.set_id(word_id)
        tok.set_para(token_info[0])
        tok.set_sent(token_info[1])
        tok.set_text(val[0])
        tok.set_offset(str(offset))
        length = len(val[0])
        tok.set_length(str(length))
        offset += length
        nafobj.add_wf(tok)
        term_id = 't' + str(idnr)
        term = Cterm()
        term.set_id(term_id)
        term.set_lemma(val[1])
        term.set_pos(val[2])
        term.set_morphofeat(val[3])
        span = create_span([word_id])
        term.set_span(span)
        nafobj.add_term(term)




def convert2naf_file(inputfile, nafobj, token_info, raw):

    myinput = ElementTree().parse(inputfile)
    token_dict = None
    word_count = token_info[2]
    for elem in myinput.getchildren():
        if elem.tag == 'node':
            token_dict = {}
            token_dict, updated_word_count = get_tokens(elem, word_count, token_dict)
            create_token_and_term_layer(token_dict, token_info, nafobj)
            #code from Ruben to create constituent and dependency layers
            find_propbank_rels(elem, nafobj, word_count)
            add_dependencies_to_naf(elem, nafobj, word_count)
        elif elem.tag == 'sentence':
            raw += ' ' + elem.text

    return updated_word_count, raw

def create_lp_object():

    global version
    mylp = Clp()
    mylp.set_name("vua-sonar2naf")
    mylp.set_version(version)
    mylp.set_timestamp()
    return mylp

def create_layer_for_header(header, layer):

    lingproc = ClinguisticProcessors()
    lingproc.set_layer(layer)
    mylp = create_lp_object()
    lingproc.add_linguistic_processor(mylp)

    header.add_linguistic_processors(lingproc)


def set_metadata(nafobj, filename):
    
    nafobj.set_language("nl")
    header = CHeader()
    filedesc = CfileDesc()
    filedesc.set_title(filename)
    header.set_fileDesc(filedesc)
    create_layer_for_header(header, 'text')
    create_layer_for_header(header, 'terms')
    create_layer_for_header(header, 'srl')

    nafobj.set_header(header)


def make_sure_input_file_exists(filename, paragraph, sentence, dir, f):

    cleanedfn = filename + '.p.' + str(paragraph) + '.s.' + str(sentence) + '.xml'
    
    if f != cleanedfn and not 'head' in f and f.endswith('xml'):
        if os.path.isfile(dir + cleanedfn):
            print('clean-up will not work: ' + cleanedfn + ' exists')
        else:
            os.rename(dir + f, dir + cleanedfn)

def collect_file_info(inputdir):

    my_files = {}
    inputdir += '/'
  #  print(inputdir)
    for f in os.listdir(inputdir):
        parts = f.split('.')
        if len(parts) > 4:
            filename = parts[0]
            paragraph = int(parts[2])
            sentence_desc = parts[4]
            if '_' in sentence_desc:
                sentence = float(sentence_desc.replace('_','.'))
            elif len(parts) == 7:
                sentence = float(parts[4] + '.' + parts[5])
            else:
                sentence = int(parts[4])
            make_sure_input_file_exists(filename, paragraph, sentence, inputdir, f)
            if filename in my_files:
                file_info = my_files.get(filename)
            else:
                file_info = {}
            if parts[1] == 'head':
                if 'head' in file_info:
                    head_paragraph = file_info.get('head')
                else:
                    head_paragraph = {}
                if paragraph in head_paragraph:
                    head_paragraph[paragraph].insert(int(sentence)-1, sentence)
                else:
                    head_paragraph[paragraph] = [sentence]
                file_info['head'] = head_paragraph
            elif paragraph in file_info:
                file_info[paragraph].insert(int(sentence)-1, sentence)
            else:
                file_info[paragraph] = [sentence]
            my_files[filename] = file_info
    return my_files


def create_and_process_file(inputdir, file_info, raw, prefix, old_sentence, nafobj, word_count, offset):

    for para, sentences in sorted(file_info.items()):
    #add two newlines and an additional offset for new paragraphs
        if raw != '':
            raw += '\n\n'
            offset += 1
        for sentence in sorted(sentences):
            filename = prefix + str(para) + '.s.' + str(sentence) + '.xml'
            #print(filename)
            doc_sentence = old_sentence + sentence
            token_info = [str(para), str(doc_sentence), word_count]
            word_count, raw = convert2naf_file(inputdir + filename, nafobj, token_info, raw)
        old_sentence = doc_sentence
    return old_sentence, raw, word_count, offset

def convert2naf(inputdir, outputdir = None):

    global offset, pid, sid
    
    my_files = collect_file_info(inputdir)
    for k, v in my_files.items():
        print(k)
        raw = ''
        word_count = 1
        offset = 0
        pid = 0
        sid = 0
        nafobj = KafNafParser(type="NAF")
        set_metadata(nafobj, k)
        old_sentence = 0
        #if exists, create head first
        if 'head' in v:
            my_head_dict = v.get('head')
            prefix = k + '.head.'
            old_sentence, raw, word_count, offset = create_and_process_file(inputdir, my_head_dict, raw, prefix, old_sentence, nafobj, word_count, offset)
            del v['head']
        prefix = k + '.p.'
        old_sentence, raw, word_count, offset = create_and_process_file(inputdir, v, raw, prefix, old_sentence, nafobj, word_count, offset)

        
        print(k + ',' + str(pid) + ',' + str(sid))
        nafobj.set_raw(raw)
        nafobj.dump(outputdir + k + '.naf')

   

def main(argv=None):

    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        print('Usage: python sonar2naf.py sonardir (nafdir)')
    elif len(argv) < 3:
        convert2naf(argv[1])
    else:
        convert2naf(argv[1], argv[2])


if __name__ == '__main__':
    main()
