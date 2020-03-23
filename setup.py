"""A command to burn many sd cards for PI clusters.

    # $ pip install cloudmesh/cm-burn.py
    
    we may cahnge this to 
        # And where it will live on PyPI: https://pypi.org/cloudmesh/cm-burn.py/


"""

from setuptools import find_packages, setup
import io

def readfile(filename):
    with io.open(filename, encoding="utf-8") as stream:
        return stream.read().split()

with open('README.md') as f:
    long_description = f.read()

setup(
#    name='cloudmesh-pi-burn',
    name='cmburn',
    version='0.3.2',
    description='A command to burn many SD cards for building PI clusters',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cloudmesh/cloudmesh_cm_burn',
    author='Cloudmesh Team',
    author_email='laszewski@gmail.comm',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: System",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    keywords='Raspberry PI SD Card Cloudmesh',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=[
        "python-hostlist",
        "docopt",
        "prompter",
        "requests",
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
        'Bug Reports': 'https://github.com/cloudmesh/cloudmesh_pi_burn/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/cloudmesh/cloudmesh_pi_burn',
    },
)
