import re
import hfst
import string
import pandas as pd
import pkg_resources

class FrancoArabicTransliterator:
	def __init__(self):
		rules_file_location = pkg_resources.resource_filename('data', 'hfst.att')
		with open(rules_file_location, 'r') as f:
			self.transducer = hfst.AttReader(f).read()

	def transliterate(self, sentence):
		transliteration = []
		for word in sentence.split():
			self.dp_dict = {}
			transliteration.append(
				sorted(self.__transliterate_word('^{}$'.format(word))))
		return transliteration

	def __transliterate_word(self, word):
		if not word:
			return set()
		if word in self.dp_dict:
			return self.dp_dict[word]
		results = self.__get_analyses(word)
		for index in range(1, len(word)):
			results = results.union(self.__join(
				self.__transliterate_word(word[:index]),
				self.__transliterate_word(word[index:])))
		self.dp_dict[word] = results
		return results

	def __get_analyses(self, word):
		results = self.transducer.lookup(word, output='raw')
		if results:
			return set([''.join([r for r in result[1] if not '@_EPSILON_SYMBOL_@' in r]) for result in results])
		else:
			return set()

	def __join(self, prefixes_set, suffixes_set):
		if not prefixes_set and not suffixes_set:
			return set()

		if not prefixes_set:
			return suffixes_set

		if not suffixes_set:
			return prefixes_set

		prefixes_set = list(prefixes_set)
		suffixes_set = list(suffixes_set)
		return set(['{}{}'.format(i1, i2) for i1 in prefixes_set for i2 in suffixes_set])

if __name__=='__main__':
	word = input()
	transliterator = FrancoArabicTransliterator()
	print(transliterator.transliterate(word))
