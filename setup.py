from setuptools import setup

setup(name='bi_parser',
      version='0.1',
      description='parsing the TEI files from berliner-intellektuelle.eu',
      url='http://github.com/millawell/bi_parser',
      author='David Lassner',
      author_email='davidlassner@gmail.com',
      license='MIT',
      packages=['berliner_intellektuelle_preprocessing'],
      install_requires=[
          'lxml',
          'spacy',
          'tqdm',
          'cPickle'
      ],
      zip_safe=False)
