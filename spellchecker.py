import re
from collections import Counter

"""
Analyzing Norvig's spelling corrector from first principles.
Examples written to optimize for explanatory and pedagogical useful over brevity.
"""

letters = 'abcdefghijklmnopqrstuvwxyz'


def words(text):
    """
    Find all words in a given text and return them as a list
    >>> words('It was a dark and stormy night')
    ['it', 'was', 'a', 'dark', 'and', 'stormy', 'night']
    """
    return re.findall(r'\w+', text.lower())


def build_word_dict():
    """
    Extract words from 'big.txt' into a Python Counter object.
    >>> WORDS = Counter(words(open('big.txt').read()))
    >>> list(WORDS.keys())[:5]
    ['the', 'project', 'gutenberg', 'ebook', 'of']
    >>> WORDS['project']
    288
    """
    return Counter(words(open('big.txt').read()))


WORDS = build_word_dict()


def get_longest(words):
    """
    Get the longest word in a list.
    >>> words = ['beta', 'tau', 'pi', 'omega']
    >>> get_longest(words)
    'omega'
    """
    return max(words, key=len)


def P(word, N=sum(WORDS.values())):
    """
    Return the probability of the selected word in the text.
    >>> P('the')
    0.07154004401278254
    >>> P('project')
    0.00025816051667958964
    """
    return WORDS[word] / float(N)


def get_splits(word):
    """
    Get all splits of a word.
    >>> get_splits('take')
    [('', 'take'), ('t', 'ake'), ('ta', 'ke'), ('tak', 'e'), ('take', '')]
    """
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    return splits


def get_deletes(splits):
    """
    Return the variations of a word involving one character deletion at a time.
    >>> get_deletes(get_splits('take'))
    ['ake', 'tke', 'tae', 'tak', 'take']
    """
    return [L + R[1:] for L, R in splits]


def get_transposes(splits):
    """
    Get the variations of a word with 2 adjacent letters swapped.
    >>> get_transposes(get_splits('take'))
    ['atke', 'tkae', 'taek']
    """
    return [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]


def get_replaces(splits):
    """
    Get all variations of a word with a single letter replaced.
    >>> get_replaces(get_splits('take'))
    ['aake', 'bake', 'cake', 'dake', 'eake', ..., 'taky', 'takz']
    """
    return [L + c + R[1:] for L, R in splits if R for c in letters]


def get_inserts(splits):
    """
    Get all variations of a word with a single letter addition.
    >>> get_inserts(get_splits('take'))
    ['atake', 'btake', 'ctake', 'dtake',..., 'takex', 'takey', 'takez']
    """
    return [L + c + R for L, R in splits for c in letters]


def edits1(word):
    """
    Generate all edits that are one edit away from a word as a set.
    >>> e1 = edits1('take')
    >>> list(e1)[:5]
    ['toake', 'txake', 'takfe', 'teake', 'takel']
    >>> len(el)
    234
    """
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = get_deletes(splits)
    transposes = get_transposes(splits)
    replaces = get_replaces(splits)
    inserts = get_inserts(splits)
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """
    Generate all edits that are two edits away from `word`.
    >>> len(set(edits2('take')))
    24254
    """
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def correction(word):
    """
    Return the most probable correction for the input word.
    >>> correction('speling')
    'spelling'
    >>> correction('tpke')
    'take'
    >>> correction('trike')
    'strike'
    """
    return max(candidate(word), key=P)

def candidate_probs(candidates):
    """
    Return a list of the probabilities for a candidate list of corrections.
    >>> candidates = set(['strike', 'tribe', 'trite'])
    >>> candidate_probs(candidates)
    >>> [3.495923663369443e-05, 3.585562731660967e-06, 8.963906829152417e-07]
    """
    return list(map(P, candidates))


def candidate(word):
    """
    Given an input word:
    1. Find if the word is in the text. If so, return it. If not, proceed to...
    2. Find the collection of 1-edits in the text. If not, proceed to...
    3. Find the collection of 2-edits in the text. If not, proceed to...
    4. Return the original input in its unmodified form.
    >>> candidate('trike')
    set(['strike', 'tribe', 'trite'])
    """
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])


def known(words):
    """
    Return the list of words from the input that appear in the text.
    >>> known(['bake', 'madeupword', 'taken'])
    set(['taken', 'bake'])
    """
    return set(w for w in words if w in WORDS)


def unit_tests():
    """
    Unit tests.
    """
    assert correction('speling') == 'spelling'              # insert
    assert correction('korrectud') == 'corrected'           # replace 2
    assert correction('bycycle') == 'bicycle'               # replace
    assert correction('inconvient') == 'inconvenient'       # insert 2
    assert correction('arrainged') == 'arranged'            # delete
    assert correction('peotry') =='poetry'                  # transpose
    assert correction('peotryy') =='poetry'                 # transpose + delete
    assert correction('word') == 'word'                     # known
    assert correction('quintessential') == 'quintessential' # unknown
    assert words('This is a TEST.') == ['this', 'is', 'a', 'test']
    assert Counter(words('This is a test. 123; A TEST this is.')) == (
           Counter({'123': 1, 'a': 2, 'is': 2, 'test': 2, 'this': 2}))
    assert len(WORDS) == 32198
    assert sum(WORDS.values()) == 1115585
    assert WORDS.most_common(10) == [
      ('the', 79809),
      ('of', 40024),
      ('and', 38312),
      ('to', 28765),
      ('in', 22023),
      ('a', 21124),
      ('that', 12512),
      ('he', 12401),
      ('was', 11410),
      ('it', 10681)]
    assert WORDS['the'] == 79809
    assert P('quintessential') == 0
    assert 0.07 < P('the') < 0.08
    return 'unit_tests pass'


print(unit_tests())