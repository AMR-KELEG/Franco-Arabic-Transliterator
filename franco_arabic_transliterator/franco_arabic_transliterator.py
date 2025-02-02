import re
import math
import hfst
import string
import logging
import pkg_resources
from functools import reduce, lru_cache
from collections import Counter


class FrancoArabicTransliterator:
    def __init__(self):
        """Construct a transliterator object."""
        rules_file_location = pkg_resources.resource_filename("data", "hfst.att")
        with open(rules_file_location, "r") as f:
            self.transducer = hfst.AttReader(f).read()
        self.logger = logging.getLogger("franco_arabic_transliterator")
        logging.basicConfig(level=logging.DEBUG)

        with open(pkg_resources.resource_filename("data", "lexicon"), "r") as f:
            self.wordlist = {
                l.split("\t")[0]: int(l.split("\t")[1]) for l in f.readlines()
            }

        def find_pairs(word, grams=10, max_len=20):
            pairs = []
            chars = ["_" for _ in range(grams)]
            word = "{}{}".format(word, "$" * (max_len - len(word)))
            for c in word:
                pairs.append((c, "".join(chars)))
                chars = chars[1:] + [c]
            return pairs

        pairs = [p for w in self.wordlist for p in find_pairs(w)]
        self.counts = Counter(pairs)
        self.sigma_counts = sum(self.counts.values())

    def transliterate(self, sentence, method):
        """Transliterate a sentence.

		Keyword arguments:
		sentence: A string of Franco Arabic words
		method: The method used to disambiguate the results ("lexicon" OR "language-model")
		"""

        sentence = sentence.lower()
        transliteration = []
        for word in sentence.split():
            word = word.lower()
            transliteration.append(
                sorted(self.__transliterate_word("^{}$".format(word), {}))
            )

        if method == "lexicon":
            self.logger.info(
                "Number of valid strings before lexicon search are: {}".format(
                    reduce((lambda x, y: x * y), [len(t) for t in transliteration])
                )
            )

            transliteration = [
                self.__lexicon_filter(r, w.lower())
                for r, w in zip(transliteration, sentence.split())
            ]

            self.logger.info(
                "Number of valid strings after lexicon search are: {}".format(
                    reduce((lambda x, y: x * y), [len(t) for t in transliteration])
                )
            )

            return " ".join(
                [self.__lexicon_disambiguate(results) for results in transliteration]
            )
        else:
            return " ".join(
                [
                    self.__language_model_disambiguate(results)
                    for results in transliteration
                ]
            )

    def __transliterate_word(self, word, temperorary_results_dictionary={}):
        """Find all the possible transliteration given the regex rules
		- Divide the word into all the valid prefixes, suffixes
		- Find the possible transliterations for the prefixes, suffixes
		- Join the prefix and suffix transliterations

		Keyword arguments:
		word: A Franco Arabic word
		temperorary_results_dictionary: A dictionary for storing intermediate results
		"""
        if not word:
            return set()
        if word in temperorary_results_dictionary:
            return temperorary_results_dictionary[word]
        results = self.__get_analyses(word)
        for index in range(1, len(word)):
            results = results.union(
                self.__join(
                    self.__transliterate_word(
                        word[:index], temperorary_results_dictionary
                    ),
                    self.__transliterate_word(
                        word[index:], temperorary_results_dictionary
                    ),
                )
            )

        # Store the temporary results in the dictionary
        temperorary_results_dictionary[word] = results
        return results

    @lru_cache(maxsize=1048576)
    def __get_analyses(self, word):
        """Find all the possible matches for a word string in the regex transducer.

		Keyword arguments:
		word: A Franco Arabic word
		temperorary_results_dictionary: A dictionary for storing intermediate results
		"""
        results = self.transducer.lookup(word, output="raw")
        if results:
            return set(
                [
                    "".join([r for r in result[1] if not "@_EPSILON_SYMBOL_@" in r])
                    for result in results
                ]
            )
        else:
            return set()

    def __join(self, prefixes_set, suffixes_set):
        """Join the results of prefix and suffix sets into a single merged results set.

		Keyword arguments:
		prefixes_set: A set of all the valid transliterations of the prefix
		suffixes_set: set of all the valid transliterations of the suffix
		"""
        if not prefixes_set and not suffixes_set:
            return set()

        if not prefixes_set:
            return suffixes_set

        if not suffixes_set:
            return prefixes_set

        prefixes_set = list(prefixes_set)
        suffixes_set = list(suffixes_set)
        return set(
            ["{}{}".format(i1, i2) for i1 in prefixes_set for i2 in suffixes_set]
        )

    def __lexicon_filter(self, word_results, word):
        """Use the lexicon to filter the results.

		Keyword arguments:
		word_results: The list of valid transliterations
		word: A Franco Arabic word
		"""
        self.logger.debug(
            "Results before disambiguation: {}".format(" ".join(word_results))
        )
        if sum([r in self.wordlist for r in word_results]) > 0:
            return {
                r: self.wordlist[r] - 50 * abs(len(r) - len(word))
                for r in word_results
                if r in self.wordlist
            }
        return {w: 1 / (1 + abs(len(w) - len(word))) for w in word_results}

    def __lexicon_disambiguate(self, word_results):
        """Select the most relevant result.

		Keyword arguments:
		word_results: The dictionary of valid transliterations
		"""
        self.logger.debug(
            "Results before disambiguation: {}".format(
                " ".join(["{}: {}".format(w, word_results[w]) for w in word_results])
            )
        )
        # TODO: Use a better sorting function
        return sorted(word_results, key=lambda t: word_results[t])[-1]

    def get_conditional_probability(self, word, context):
        prob = math.log(self.counts.get((word, context), 0) + 1) - math.log(
            self.sigma_counts
        )
        return prob

    def get_probability(self, word, grams=10):
        chars = ["_" for _ in range(grams)]
        prob = 0
        for c in word:
            prob += self.get_conditional_probability(c, "".join(chars))
            chars = chars[1:] + [c]
        return prob

    def __language_model_disambiguate(self, word_results, max_len=20):
        word_results = {
            word: self.get_probability("{}{}".format(word, "$" * (max_len - len(word))))
            for word in word_results
        }

        return sorted(word_results, key=lambda t: word_results[t])[-1]
