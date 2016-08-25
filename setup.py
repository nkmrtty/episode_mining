#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__author__ = 'Tatsuya Nakamura'

setup(
    name='episode_mining',
    version='0.2.3',
    description='An inplementation of sequential patterm mining method',
    author='Tatsuya Nakamura',
    author_email='nkmrtty.com@gmail.com',
    url='https://github.com/nkmrtty/episode_mining',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords=['episode mining', 'pattern mining'],
    license='MIT License',
    install_requires=[],
)
