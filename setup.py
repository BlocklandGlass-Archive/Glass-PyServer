#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='glass',
      version='1.0',
      packages=find_packages(),

      install_requires=[
        'twisted>=12.1.0',
        'txamqp>=0.6.1',
        'txamqp-helpers>=0.5',
        'pyOpenSSL>=0.13',
        'Flask>=0.9',
        'hamlish-jinja>=0.2',
        'Flask-WTF>=0.8'
      ]
     )
