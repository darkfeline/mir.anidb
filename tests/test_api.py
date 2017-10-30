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

import asyncio
from unittest import mock
import xml.etree.ElementTree as ET

import aiohttp
import pytest
import requests_mock

from mir.anidb import api


def test_titles_request():
    with requests_mock.Mocker() as m:
        m.get('http://anidb.net/api/anime-titles.xml.gz', text='ok')
        got = api.titles_request()
    assert got.text == 'ok'


def test_async_titles_request(loop):
    async def test():
        session = mock.create_autospec(aiohttp.ClientSession, instance=True)
        session.get.return_value = StubClientResponse('ok')
        response = api.async_titles_request(session)
        return await response.text()
    got = loop.run_until_complete(test())
    assert got == 'ok'


def test_client_eq():
    assert api.Client('foo', 1) == api.Client('foo', 1)


def test_client_not_eq():
    assert api.Client('foo', 2) != api.Client('foo', 1)


def test_httpapi_request():
    client = api.Client('foo', 2)
    with requests_mock.Mocker() as m:
        m.get('http://api.anidb.net:9001/httpapi', text='ok')
        got = api.httpapi_request(client, request='anime')
    assert got.text == 'ok'


def test_async_httpapi_request(loop):
    client = api.Client('foo', 2)

    async def test():
        session = mock.create_autospec(aiohttp.ClientSession, instance=True)
        session.get.return_value = StubClientResponse('ok')
        response = api.async_httpapi_request(session, client, request='anime')
        return await response.text()
    got = loop.run_until_complete(test())
    assert got == 'ok'


def test__check_for_errors():
    etree = ET.ElementTree(ET.fromstring('<error>Banned</error>'))
    with pytest.raises(api.APIError) as excinfo:
        api._check_for_errors(etree)
    assert excinfo.value.args == ('Banned',)


def test_unpack_xml_response():
    response = FakeResponse('<test></test>')
    got = api.unpack_xml_response(response)
    assert isinstance(got, ET.ElementTree)


class FakeResponse:

    def __init__(self, text):
        self.text = text


class StubClientResponse:

    def __init__(self, text):
        self._text = text

    async def text(self):
        return self._text
