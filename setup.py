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
    version='0.0.1',  
    description='A command to burn many SD cards for building PI clusters',
    long_description=long_description,  
    long_description_content_type='text/markdown',
    url='https://github.com/cloudmesh/cm-burn.py',
    author='Cloudmesh Team', 
    author_email='laszewski@gmail.comm', 
    scripts=['cmburn.py'],

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
    ],

    keywords='Raspberry PI SDcard cloudmesh',  

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=[
        "python-hostlist",
        "docopt",
        "prompter",
        "requests",
        "wget",
        "pyyaml",
        ],

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    
    # package_data={  # Optional
    #    'sample': ['package_data.dat'],
    # },
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    entry_points={
        'console_scripts': [
            'cm-burn=cmburn:main',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/cloudmesh/cm-burn.py/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/cloudmesh/cm-burn.py/',
    },
)
