from naf2conll.naf_readers import NAFReader


def test_extract_coref_sets(nafobj):
    coref_sets = NAFReader.extract_coref_sets(nafobj)
    coref_sets = list(coref_sets)
    assert len(coref_sets) == 101
    for refset in coref_sets:
        assert len(refset) >= 1

    for refset in coref_sets:
        assert isinstance(refset, list)

    for refset in coref_sets:
        for refspan in refset:
            assert isinstance(refspan, list)

    for refset in coref_sets:
        for refspan in refset:
            for token_id in refspan:
                assert isinstance(token_id, str)

    for refset in coref_sets:
        for refspan in refset:
            for token_id in refspan:
                assert isinstance(token_id, str)

    for refset in coref_sets:
        for refspan in refset:
            for token_id in refspan:
                assert nafobj.get_token(token_id) is not None


def test_token_ids_from_term_ids(nafobj):
    from KafNafParserPy import Cterm, Cwf
    calculated_ids = list(NAFReader.token_ids_from_term_ids(
        map(
            Cterm.get_id,
            nafobj.get_terms()
        ),
        nafobj
    ))
    expected_ids = list(map(Cwf.get_id, nafobj.get_tokens()))
    assert calculated_ids == expected_ids
