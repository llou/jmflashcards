#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
VERSION=open(os.path.join(PACKAGE_PATH, 'VERSION')).read().strip()

with open("README.rst", "r") as f:
    long_description = f.read()

setup(name = 'jmflashcards',
      version = VERSION,
      description = 'A Flashcard deluxe flashcard processor',
      long_description = long_description,
      author = 'Jorge Monforte González',
      author_email = 'yo@llou.net',
      url = 'https://github.com/llou/jmflashcards',
      scripts = ['bin/jmflashcards'],
      packages = ['jmflashcards'],
      package_dir = {'' : 'lib'},
      license = 'MiT',
      keywords = 'flashcards latex',
      classifiers = [
          'Environment :: Console',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Education',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: Education :: Computer Aided Instruction (CAI)',
          'Topic :: Text Processing'
          ]
      )


