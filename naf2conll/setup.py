from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='naf2conll',
    version='1.0.0',
    description='Script to convert files in NAF format to CoNLL format',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Martin van Harmelen',
    author_email='Martin@vanharmelen.com',
    url='https://github.com/cltl/FormatConversions/tree/master/naf2conll',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "KafNafParserPy>=1.88",
        "pyaml>=17.12.1",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
    ],
)
