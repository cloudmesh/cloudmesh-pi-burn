#!/usr/bin/env python
# ----------------------------------------------------------------------- #
# Copyright 2017, Gregor von Laszewski, Indiana University                #
#                                                                         #
# Licensed under the Apache License, Version 2.0 (the "License"); you may #
# not use this file except in compliance with the License. You may obtain #
# a copy of the License at                                                #
#                                                                         #
# http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                         #
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
# See the License for the specific language governing permissions and     #
# limitations under the License.                                          #
# ------------------------------------------------------------------------#

import io

from setuptools import find_packages, setup


def readfile(filename):
    with io.open(filename, encoding="utf-8") as stream:
        return stream.read().split()


# requiers = readfile ('requirements.txt')
#
# add minimum requirements here
#
requiers = """
cloudmesh-common
cloudmesh-cmd5
cloudmesh-inventory
cloudmesh-configuration
wget
python-hostlist
docopt
prompter
pyyaml
oyaml
requests
pyusb
""".split("\n")

# dependency_links = ['http://github.com/nicolaiarocci/eve.git@develop']

version = readfile("VERSION")[0].strip()

with open('README.md') as f:
    long_description = f.read()

NAME = "cloudmesh-pi-burn"
DESCRIPTION = "A command `cms burn` to burn many Raspberry PI "\
              "SD Cards for buildiing PI Clusters with sshkeys "\
              "and networking" \

AUTHOR = "Gregor von Laszewski"
AUTHOR_EMAIL = "laszewski@gmail.com"
URL = "https://github.com/cloudmesh/cloudmesh-burn"

setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    license="Apache 2.0",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=requiers,
    tests_require=[
        "flake8",
        "coverage",
    ],
    zip_safe=False,
    namespace_packages=['cloudmesh'],
)
