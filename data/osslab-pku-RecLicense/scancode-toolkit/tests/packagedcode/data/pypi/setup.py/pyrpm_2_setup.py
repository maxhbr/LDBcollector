from setuptools import setup, find_packages

setup(name='pyrpm-02strich',
      version='0.5.3',
      description="A pure python rpm reader and YUM metadata generator",
      author="Stefan Richter",
      author_email="stefan@02strich.de",
      url="https://github.com/02strich/pyrpm",
      license="BSD",

      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.1',
          'Topic :: Software Development :: Libraries',
      ],

      packages=find_packages(where='.'),
      use_2to3=True,
      test_suite="tests",
      )
