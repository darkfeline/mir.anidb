# Copyright (C) 2016, 2017  Allen Li
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

"""Low level API for AniDB.

https://wiki.anidb.net/w/API
"""

import io
from typing import NamedTuple
import xml.etree.ElementTree as ET

import requests


def titles_request() -> 'Response':
    """Request titles.

    https://wiki.anidb.net/w/API#Anime_Titles
    """
    return requests.get('http://anidb.net/api/anime-titles.xml.gz')


class Client(NamedTuple):
    name: str
    version: int


def httpapi_request(client, **params) -> 'Response':
    """Send a request to AniDB HTTP API.

    https://wiki.anidb.net/w/HTTP_API_Definition
    """
    return requests.get(
        'http://api.anidb.net:9001/httpapi',
        params={
            'client': client.name,
            'clientver': client.version,
            'protover': 1,
            **params
        })


def unpack_xml_response(response) -> ET.ElementTree:
    """Unpack an XML response from AniDB API."""
    etree: ET.ElementTree = ET.parse(io.StringIO(response.text))
    _check_for_errors(etree)
    return etree


def _check_for_errors(etree: ET.ElementTree):
    """Check AniDB response XML tree for errors."""
    if etree.getroot().tag == 'error':
        raise APIError(etree.getroot().text)


class APIError(Exception):
    """AniDB API error."""
