# Copyright (C) 2017 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from setuptools import setup


def find_version(path):
    with open(path) as f:
        text = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              text, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='mir.anidb',
    version=find_version('mir/anidb/__init__.py'),
    description='AniDB API',
    long_description='',
    keywords='',
    url='https://github.com/darkfeline/mir.anidb',
    author='Allen Li',
    author_email='darkfeline@felesatra.moe',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
    ],

    packages=['mir.anidb'],
    install_requires=[
        'requests~=2.23.0',
    ],
)
