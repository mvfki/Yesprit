#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

# Recursively included needed data files
import glob
data_files = []
directories = glob.glob('Yesprit/data/?/')
for directory in directories:
    files = glob.glob(directory+'*')
    data_files.append(('/'.join(directory.split('/')[1:]), files))

directories = glob.glob('Yesprit/resources/')
for directory in directories:
    files = glob.glob(directory+'*')
    data_files.append(('/'.join(directory.split('/')[1:-1]), files))

setup(
    name="Yesprit",
    version="1.0.1",
    description="This is a tool that design primers for four fission yeast species.",
    author="Xindi Wang",
    author_email="wangxd1@shanghaitech.edu.cn",
    python_requires=">=3.6.0",
    url="https://github.com/Sugiyama-Lab/Yesprit",
    py_modules=['Yesprit'],
    packages=["Yesprit"],
    entry_points={
        'console_scripts': [
        'Yesprit = Yesprit.__main__:main',
    ],
    },
    install_requires=["tk", "Bio"],
    include_package_data=True,
    data_files=data_files,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ]
)