#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

setup(name = 'jmflashcards',
      version = '0.0.2',
      description = 'A flashcard manager',
      author = 'Jorge Monforte González',
      author_email = 'jorge.monforte@gmail.com',
      scripts = ['bin/jmflashcards'],
      packages = ['jmflashcards'],
      package_dir = {'' : 'lib'},
      license = 'private',
      keywords = 'flashcards latex',
      install_requires=['colouredlogs', 'pyYaml'],
      classifiers = [
          'Environment :: Console',
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Education',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: Other/Proprietary License',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Education :: Computer Aided Instruction (CAI)',
          'Topic :: Text Processing'
          ]
      )


