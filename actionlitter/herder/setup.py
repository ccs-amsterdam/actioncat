#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    "amcat4py",
    "fastapi",
    "typing",
    "requests",
    "pydantic",
    "uvicorn",
 ]

test_requirements = ['pytest>=3', ]

setup(
    author="Johannes B. Gruber",
    author_email='JohannesB.Gruber@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Run automated tasks on documents of an AmCAT instance",
    entry_points={
        'console_scripts': [
            'actioncat=actioncat.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='actioncat',
    name='actioncat',
    packages=find_packages(include=['actioncat', 'actioncat.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/JBGruber/actioncat',
    version='0.1.0',
    zip_safe=False,
)
