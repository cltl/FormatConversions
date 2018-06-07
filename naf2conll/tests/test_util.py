import itertools as it

from hypothesis import given
from hypothesis.strategies import integers, lists

from naf2conll.util import split_on_numbering


@given(lists(integers(min_value=1, max_value=1000)))
def test_split_on_numbering(lengths):
    lists = [[i] * l for i, l in enumerate(lengths)]
    assert split_on_numbering(it.chain(*lists), lambda x: x) == lists
