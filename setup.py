from setuptools import setup

setup(name='ibiparser',
      version='0.1',
      description='parsing the TEI files from berliner-intellektuelle.eu',
      url='http://github.com/millawell/ibiparser',
      author='David Lassner',
      author_email='davidlassner@gmail.com',
      license='MIT',
      packages=['ibiparser'],
      install_requires=[
          'lxml',
          'pandas'
      ],
      zip_safe=False)