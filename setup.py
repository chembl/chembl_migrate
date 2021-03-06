#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mnowotka'

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='chembl-migrate',
    version='0.9.6',
    author='Michal Nowotka',
    author_email='mnowotka@ebi.ac.uk',
    description='Django custom management tool intended to perform data exports and migration of CheMBL database.',
    url='https://www.ebi.ac.uk/chembl/',
    license='Apache Software License',
    packages=['chembl_migrate',
              'chembl_migrate.management',
              'chembl_migrate.management.commands'],
    long_description=open('README.rst').read(),
    install_requires=[
        'Django==1.10.6',
    ],
    include_package_data=False,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering :: Chemistry'],
    zip_safe=False,
)
