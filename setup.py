"""A command to burn many sd cards for PI clusters.

    # $ pip install cloudmesh/cm-burn.py
    
    we may cahnge this to 
        # And where it will live on PyPI: https://pypi.org/cloudmesh/cm-burn.py/


"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cm-burn',
    version='0.0.2',
    description='A command to burn many SD cards for building PI clusters',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cloudmesh/cm-burn.py',
    author='Cloudmesh Team',
    author_email='laszewski@gmail.comm',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: Apache 2.0',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='Raspberry PI SDcard cloudmesh',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=[
        "python-hostlist",
        "docopt",
        "prompter",
        "requests",
        "wget",
        "pyyaml",
        "oyaml",
        "cloudmesh-common"
    ],
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'cm-burn=cmburn.general.cmburn:main',
            'cm-pi-burn=cmburn.pi.cmpiburn:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/cloudmesh/cm-burn.py/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/cloudmesh/cm-burn.py/',
    },
)
