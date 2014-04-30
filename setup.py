#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

from opps import multimedias


install_requires = [
    "opps>=0.2",
    "django-celery",
    "gdata",
    # "uolmais-api"
]

# dependency_links = ['https://yacows.codebasehq.com/yacows-libs/'
#                    'multimediauolmais.git#egg=uolmais-api']

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
    long_description = multimedias.__description__

setup(name='opps-multimedias',
      namespace_packages=['opps'],
      version=multimedias.__version__,
      description=multimedias.__description__,
      long_description=long_description,
      classifiers=classifiers,
      keywords='Multimedia upload app for opps cms',
      author=multimedias.__author__,
      author_email=multimedias.__email__,
      packages=find_packages(exclude=('doc', 'docs',)),
      install_requires=install_requires,
      # dependency_links=dependency_links,
      include_package_data=True,)
