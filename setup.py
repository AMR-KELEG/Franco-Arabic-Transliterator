import setuptools

setuptools.setup(
	name='franco_arabic_transliterator',
	version='0.0.1.3',
	description='Convert franco-arabic text into arabic',
	url='https://github.com/AMR-KELEG/Franco-Arabic-Transliterator',
	author='Amr Keleg',
	author_email='amr_mohamed@live.com',
	license='GPLv3',
	packages=setuptools.find_packages(),
	install_requires=['hfst'],
	include_package_data=True,
	zip_safe=False)

