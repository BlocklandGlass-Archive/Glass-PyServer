#!/usr/bin/env python

from distutils.core import setup
from distutils.cmd import Command


setup(name='glass',
      version='1.0',
      packages=['glass', 'glass.server'],
      cmdclass={
        "keygen": keygen,
      },
     )
