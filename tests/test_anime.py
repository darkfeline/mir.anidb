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

from unittest import mock

import pytest

from mir.anidb import api
from mir.anidb import anime

from . import testlib


def test_request_anime(test_xml):
    xml, obj = test_xml
    client = api.Client('foo', 1)
    with mock.patch('mir.anidb.api.httpapi_request') as request:
        request.return_value = testlib.FakeResponse(xml)
        got = anime.request_anime(client, 22)
    request.assert_called_once_with(client, request='anime', aid=22)
    assert got == obj


def test_get_episode_number():
    ep = _TEST_ANIME.episodes[1]
    got = anime.get_episode_number(ep)
    assert got == 1


def test_get_episode_title_ja():
    ep = _TEST_ANIME.episodes[0]
    got = anime.get_episode_title(ep)
    assert got == '\u4f7f\u5f92, \u8972\u6765'


def test_get_episode_title_fallback():
    ep = _TEST_ANIME.episodes[1]
    got = anime.get_episode_title(ep)
    assert got == 'Revival of Evangelion Extras Disc'


_TEST_ANIME = testlib.load_obj('anime.py')


@pytest.fixture(params=[
    ('anime.xml', 'anime.py'),
    ('anime_ongoing.xml', 'anime_ongoing.py'),
])
def test_xml(request):
    xml_path, obj_path = request.param
    xml = testlib.load_text(xml_path)
    obj = testlib.load_obj(obj_path)
    return xml, obj
