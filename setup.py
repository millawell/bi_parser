from setuptools import setup

setup(name='bi_parser',
      version='0.1',
      description='parsing the TEI files from berliner-intellektuelle.eu',
      url='http://github.com/millawell/bi_parser',
      author='David Lassner',
      author_email='davidlassner@gmail.com',
      license='MIT',
      packages=['bi_parser'],
      install_requires=[
          'lxml',
          'pandas'
      ],
      zip_safe=False)
