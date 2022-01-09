![https://github.com/AMR-KELEG/Franco-Arabic-Transliterator/actions?query=workflow%3ABuild](https://github.com/AMR-KELEG/Franco-Arabic-Transliterator/workflows/Build/badge.svg)
# Franco Arabic Transliterator
A rule-based python script to convert romanised/franco arabic into Arabic.

## Installation
`pip install franco_arabic_transliterator`

## Usage
```
from franco_arabic_transliterator.franco_arabic_transliterator import *

str = '2zayak ya 7abeby'
transliterator = FrancoArabicTransliterator()

# Pick up one of the disambiguation methods
print(transliterator.transliterate(str, method="lexicon")) # ازيك يا حبيبي
print(transliterator.transliterate(str, method="language-model")) # ازيك يا حبيبي

```
## Live demo
https://ak-blog.herokuapp.com/franco/
