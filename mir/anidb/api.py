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

"""The module contains classes for working with AniDB's HTTP API."""

import gzip
import io
from urllib.parse import urlencode
from urllib.request import urlopen
import xml.etree.ElementTree as ET


class Client:

    def __init__(self, name: str, version: int, protocol=1):
        self._name = name
        self._version = version
        self._protocol = protocol

    def _request(self, request: str, **params) -> 'HttpResponse':
        """Make an AniDB HTTP API request.

        https://wiki.anidb.net/w/HTTP_API_Definition
        """
        urlparams = urlencode({
            'client': self._name,
            'clientver': self._version,
            'protover': self._protocol,
            'request': request,
            **params
        })
        return urlopen(f'http://api.anidb.net:9001/httpapi?{urlparams}')

    def call(self, request: str, **params) -> ET.ElementTree:
        """Call AniDB API."""
        response = self._request(request, **params)
        return unpack_response(response)


def unpack_response(response) -> ET.ElementTree:
    """Unpack AniDB API XML response."""
    etree: ET.ElementTree = ET.parse(_get_content(response))
    _check_for_errors(etree)
    return ET.ElementTree(etree)


def _get_content(response: 'HTTPResponse') -> str:
    """Get content from HTTP response.

    Handles gzipped content.
    """
    content = response
    if response.getheader('Content-encoding') == 'gzip':
        content = gzip.open(response)
    return io.TextIOWrapper(content)


def _check_for_errors(etree: ET.ElementTree):
    """Check AniDB response XML tree for errors."""
    if etree.getroot().tag == 'error':
        raise APIError(etree.getroot().text)


class APIError(Exception):
    """AniDB API error."""
