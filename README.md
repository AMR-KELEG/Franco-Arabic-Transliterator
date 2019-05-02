# Franco Arabic Transliterator
A rule-based python script to convert romanised/franco arabic into Arabic.

## Depenedencies
- pandas: `pip install pandas`

## Usage
```
from franco_arabic_transliterator import franco_arabic_transliterate

str = '2zayak ya 7abeby'
print(franco_arabic_transliterate(str)) # أزيك يه حبيبي

```

### TODO:
- [ ] Compare the tool to https://github.com/athreef/Encode-Arabic-Franco https://metacpan.org/release/Encode-Arabic-Franco/source/lib/Encode/Arabic/Franco.pm
- [ ] Consider using a FST for generating multiple outputs
