#!/usr/bin/python
# -*- coding: UTF -*-

from distutils.core import setup

DESCRIPTION = 'Shellbox Backdoors'
LONG_DESCRIPTION = 'Framework to reverse tcp connection backdoors.'
VERSION = '1.0'
AUTHOR = 'Yan Marques'
AUTHOR_EMAIL = 'marques_yan@outlook.com'
URL = 'https://github.com/yanmarques/simple-backdoor'

setup(name='Shellbox',
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      packages=['simple_backdoor'],
      license='MIT'
     )