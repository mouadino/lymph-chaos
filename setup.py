# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as f:
    description = f.read()


setup(
    name='lymph-chaos',
    version='0.1.0',
    url='http://github.com/mouadino/lymph-chaos/',
    packages=find_packages(),
    namespace_packages=['lymph'],
    license=u'Apache License (2.0)',
    long_description=description,
    include_package_data=True,
    install_requires=[
        'lymph>=0.1.0',
    ],
)
