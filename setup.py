#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

from opps import videos



install_requires = ["opps", "FFVideo"]

classifiers = ["Development Status :: 4 - Beta",
               "Intended Audience :: Developers",
               "Operating System :: OS Independent",
               "Framework :: Django",
               'Programming Language :: Python',
               "Programming Language :: Python :: 2.7",
               "Operating System :: OS Independent",
               "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
               'Topic :: Software Development :: Libraries :: Python Modules']

try:
    long_description = open('README.md').read()
except:
    long_description = videos.__description__

setup(name='opps-videos',
        namespace_packages=['opps'],
        version=videos.__version__,
        description=videos.__description__,
        long_description=long_description,
        classifiers=classifiers,
        keywords='Video upload app for opps cms',
        author=videos.__author__,
        author_email=videos.__email__,
        packages=find_packages(exclude=('doc', 'docs',)),
        install_requires=install_requires,
        include_package_data=True,)
