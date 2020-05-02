import pytest
from franco_arabic_transliterator.franco_arabic_transliterator import FrancoArabicTransliterator


def test_generate_output():
	transliterator = FrancoArabicTransliterator()
	word = 'Ahlan'
	transliterated_word = transliterator.transliterate(word, None)
	assert(transliterated_word)
