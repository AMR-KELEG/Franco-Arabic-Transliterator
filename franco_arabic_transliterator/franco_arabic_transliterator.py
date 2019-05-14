import re
import string
import pandas as pd
import pkg_resources

def franco_arabic_transliterate(str):
	rules_file_location = pkg_resources.resource_filename('data', 'rules.tsv')
	rules_df = pd.read_csv(rules_file_location, sep='\t', header=None)
	str = str.lower()
	tokens = str.split()

	# Apply the regex rules in the order of occurence in the dataframe
	for _, rule in rules_df.iterrows():
		reg = rule.iloc[0]
		sub = rule.iloc[1]
		tokens = [re.sub(reg, sub, str) for str in tokens]

	# Remove remaining arabic characters
	for c in string.ascii_letters:
		tokens = [re.sub(r'{}+'.format(c), '', str) for str in tokens]

	return ' '.join(tokens)

if __name__=='__main__':
	str = input().lower()
	print(franco_arabic_transliterate(str))
