# MMAX Format
Modified from [Multi-Level Annotation in MMAX (2003)][MMAX].

## Files
A `.MMAX` project file contains references to all files comprising a MMAX document:

### Files with language data
All elements comprising a MMAX document are stored in a _sentences_ or _turns_ file and a _words_ file (and an additional _gestures_ file for multimodal dialogue).
These files define the annotation base data and are not supposed to be modifiable through the annotation tool.

 - one _sentences_ or _turns_ XML file
 - a _words_ XML file (and/or a _gestures_ file)
 - a list of _markables_ XML files

### Files with style data

 - an XSL style sheet file for rendering the _layout_ of the MMAX display
 - an XML file specifying colour attributes for rendering the appearance of markables depending on their _content_


## Sentences, turns and words files

As for the XML implementation of the annotation base data, we simply model **sentence** and turn elements as XML elements with the respective name and with two obligatory attributes: The `ID` attribute assigns a unique label to each element, and the `span` attribute contains a (condensed) list of `ID`s of those base data elements that the sentence or turn contains.
```xml
<sentence id="sentence_1" span="word_1..word_8"/>
```

The **turn** element may have an additional `speaker` and `number` attribute.
```xml
<turn id="turn_1" span="word_1..word_7" speaker="A" number="1"/>
```

Each **word** element in the base data is modelled as a `<word>` XML element with an ID attribute as the only obligatory one.
The word itself is represented as a text child of the `<word>` element.
If the original language data was spoken language, this is the transcription of the originally spoken word.
In this case, the `<word>` element may also have an additional `starttime` and `endtime` attribute relating the word to a time line.

```xml
<word id="word_1" starttime="0.000" endtime="0.7567">
    This
</word>
```

The COREA dataset also contains an `alpsent` and `alppos` attribute, which relate a word to a sentence identifier and the (zero-based) position of that word in the sentence.

## Markables files
Markables pertaining to the same linguistic level are stored together in a _markables_ XML file.
In its header, this file contains a reference to an annotation scheme XML file.

A **markable** is simply an abstract entity which aggregates an arbitrary set of elements from the base data.
It does so by means of a list of IDs of word elements (and/or gesture elements), which are interpreted as pointers to the respective elements.


Markables are modelled as `<markable>` XML elements which are similar to `<sentence>` and `<turn>` elements in that they consist (in their most basic form) mainly of an `ID` and a `span` attribute.
The latter attribute, however, can be more complex since it can reference discontinuous (or fragmented) sequences of base data elements.

```xml
<markable id="markable_1" span="word_1..word_5,word_7" ... />
```


### Attributes
At this time, two types of attributes are supported:

 - _nominal_ attributes can take one of a closed set of values,
 - _freetext_ attributes can take any string (or numerical) value.

On the XML level, attributes are expressed in the standard `name="value"` format on markable elements in the _markables_ file. Note, however, that both the type of the attributes and their possible values (for nominal attributes) cannot be determined from the _markables_ file alone, but only with reference to the annotation scheme linked to it.


### Relations
The following relations are currently supported:

 - _member-relation_ express undirected relations between arbitrary many markables (≈ set-membership), i.e. markables having the same value in an attribute of type _member-relation_ constitute an unordered set.
 - _pointer-relation_ express directed relations between single source markables and arbitrarily many target markables. As the name suggests, this relation can be interpreted as the source markable pointing to its target markable(s).

**N.B.**: _member-relation_ and _pointer-relation_ are not attributes themselves. Rather, they are _types_ of attributes (like _nominal_ and _freetext_) which can be realized by attributes of arbitrary names. That means that for one markable, several different attributes of type _member-_ and _pointer-relation_ can be defined within the same annotation scheme. The attribute type simply defines how these attributes are interpreted.

On the XML level, relations are expressed like normal attributes, with the only difference that their values are (lists of) markable element IDs (_pointer-relation_) or strings of the form `set_x` (_member-relation_).

```xml
<markable id="markable_2" span="word_14..16"
    coref_class="set_4" antecedent="markable_1" ... />
```


## Scheme files
(Written by @mpvharmelen, using only an example scheme file.)

A scheme file contains a `<annotationscheme>` tag, which contains `<attribute>` tags that describe legal attributes.

`<attribute>` tags have the following attributes:

 - `id` identifier used to refer to this attribute. This identifier is only used in scheme files.
 - `name` name of the attribute (of a markable) as used in markables file, e.g. if `name="comment"` then one could find with `<markable ... comment="some value"/>` in a markables file.
 - `type` type of the attribute. Possible values (not exhaustive):
     + `nominal_button` see _nominal_ attributes in [Attributes][]
     + `freetext` see _freetext_ attributes in [Attributes][]
     + `markable_pointer` see _pointer-relation_ in [Relations][]
     + I expect some type to facilitate a _member-relation_ (see [Relations][]), maybe `markable_member`.
     + I do **not** expect pointers to other types of objects to be legal (e.g. `word_pointer` or `sentence_pointer`), as [Relations][] explicitly names markables as the subject of relations.
 - `text` description of the attribute

`<attribute>` tags contain `<value>` tags that describe legal values of an attribute.

`<value>` tags have the following attributes:

 - `id` identifier used to refer to this value. I have not seen this identifier been used.
 - `name` the function of the `name` attribute differs per `<attribute>` type:
     + `nominal_button`: `name` contains a legal value
     + `markable_pointer`: `name` contains either `set` or `not set`
     + `freetext`: `name` has the same function as `text`
 - `text` description of the value
 - `next` only for a `markable_pointer` `<attribute>`. Contains a comma-separated list of identifiers of `<attribute>`s that are expected if this pointer is (not) set.

### Example
This example is taken from the COREA corpus: _COREA: Coreference Resolution for Extracting
Answers for Dutch_ in [Essential Speech and Language Technology for Dutch][COREABook] Ch. 7 p. 115 -- 128.

Given the following scheme file

```xml
<annotationscheme>
  <attribute id="att_head" name="head" text="Which word is the semantic head of the NP?" type="freetext">
    <value id="val_head" name="the word which is the semantic head of the NP"/>
  </attribute>

  <attribute id="att_ref" name="ref" type="markable_pointer">
    <value id="val_ref_set"     name="set" next="att_type,att_mod"/>
    <value id="val_ref_not_set" name="not_set"/>
  </attribute>

  <attribute id="att_type" name="type" type="nominal_button" text="What type of coreference is expressed?">
    <value id="val_type_ident"  name="ident"  text="Ana is identical to Ante"/>
    <value id="val_type_pred"   name="pred"   text="Ana is predicated of Ante"/>
  </attribute>

  <attribute id="att_mod" name="mod" type="nominal_button" text="Does context contain a modal operator?">
    <value id="val_mod_0" name="no"/>
    <value id="val_mod_1" name="yes"/>
  </attribute>
</annotationscheme>
```

The following markables could be expected (somewhere in a markables file).
```xml
...
<markable id="markable_005" span="word_17..word_18" head="grain" />
...
<markable id="markable_014" span="word_42..word_43" head="grain"  ref="markable_5"  type="ident" mod="no" />
...
```

[MMAX]: http://www.speech.cs.cmu.edu/sigdial2003/proceedings/07_LONG_strube_paper.pdf
[Attributes]: #attributes
[Relations]: #relations
[COREABook]: https://link.springer.com/book/10.1007/978-3-642-30910-6
