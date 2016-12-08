#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

PACKAGE_PATH=os.path.dirname(os.path.realpath(__file__))
VERSION=open(os.path.join(PACKAGE_PATH, 'VERSION')).read().strip()

setup(name = 'jmflashcards',
      version = VERSION,
      description = 'A flashcard manager',
      author = 'Jorge Monforte González',
      author_email = 'jorge.monforte@gmail.com',
      scripts = ['bin/jmflashcards'],
      packages = ['jmflashcards'],
      package_dir = {'' : 'lib'},
      license = 'private',
      keywords = 'flashcards latex',
      classifiers = [
          'Environment :: Console',
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Education',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: Other/Proprietary License',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: Education :: Computer Aided Instruction (CAI)',
          'Topic :: Text Processing'
          ]
      )


