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

import io
from pathlib import Path
import xml.etree.ElementTree as ET
from unittest import mock

import pytest

from mir.anidb import titles


def test_CachedTitlesGetter_repr():
    getter = titles.CachedTitlesGetter(
        mock.sentinel.cache, mock.sentinel.requester)
    assert repr(getter) == \
        "CachedTitlesGetter(sentinel.cache, sentinel.requester)"


def test_CachedTitlesGetter_get_cache_force():
    cache = mock.create_autospec(titles.Cache, instance=True)
    requester = mock.create_autospec(titles.api_requester)
    requester.return_value = mock.sentinel.titles
    cache.load.return_value = mock.sentinel.bad_titles
    getter = titles.CachedTitlesGetter(cache, requester)
    assert getter.get(force=True) == mock.sentinel.titles
    requester.assert_called_once_with()
    cache.load.assert_not_called()


def test_CachedTitlesGetter_get_cache_miss():
    cache = mock.create_autospec(titles.Cache, instance=True)
    requester = mock.create_autospec(titles.api_requester)
    requester.return_value = mock.sentinel.titles
    cache.load.side_effect = titles.CacheMissingError
    getter = titles.CachedTitlesGetter(cache, requester)
    assert getter.get() == mock.sentinel.titles
    requester.assert_called_once_with()
    cache.save.assert_called_once_with(mock.sentinel.titles)


def test_CachedTitlesGetter_get_cache_hit():
    cache = mock.create_autospec(titles.Cache, instance=True)
    requester = mock.create_autospec(titles.api_requester)
    cache.load.return_value = mock.sentinel.titles
    getter = titles.CachedTitlesGetter(cache, requester)
    assert getter.get() == mock.sentinel.titles
    requester.assert_not_called()
    cache.load.assert_called_once_with()


def test_Cache_load():
    with pytest.raises(titles.CacheMissingError):
        titles.Cache.load(mock.sentinel.dummy)


def test_PickleCache_repr():
    cache = titles.PickleCache('foo')
    assert repr(cache) == "PickleCache('foo')"


def test_PickleCache_load_cache_missing(tmpdir):
    cache = titles.PickleCache(tmpdir / 'foo')
    with pytest.raises(titles.CacheMissingError):
        cache.load()


def test_PickleCache_save_load(tmpdir):
    cache = titles.PickleCache(tmpdir / 'foo')
    titles_list = _TEST_TITLES
    cache.save(titles_list)
    assert cache.load() == titles_list


def test_api_requester(testrequest, tmpdir):
    got = titles.api_requester()
    assert got == _TEST_TITLES


def test_CopyingRequester_repr(tmpdir):
    requester = titles.CopyingRequester('tmp')
    assert repr(requester) == "CopyingRequester('tmp')"


def test_CopyingRequester(testrequest, tmpdir):
    got = titles.CopyingRequester(tmpdir / 'copy.xml')()
    assert got == _TEST_TITLES


def test_CopyingRequester_saves_xml_copy(testrequest, tmpdir):
    copy = tmpdir / 'copy.xml'
    got = titles.CopyingRequester(copy)()
    assert list(titles._unpack_titles(ET.parse(copy))) == got


def test__unpack_titles(testxml):
    etree = ET.parse(testxml)
    got = list(titles._unpack_titles(etree))
    assert got == _TEST_TITLES


_TEST_TITLES = [titles.Titles(
    aid=22,
    titles=(
        titles.Title(title='Neon Genesis Evangelion',
                     type='official',
                     lang='en'),
        titles.Title(title='Shinseiki Evangelion',
                     type='main',
                     lang='x-jat'),
    ))]
_TESTXML = Path(__file__).parent / 'data' / 'titles.xml'


@pytest.fixture
def testxml():
    with open(_TESTXML) as file:
        return io.StringIO(file.read())


@pytest.fixture
def testrequest(testxml):
    with mock.patch('mir.anidb.api.titles_request') as request:
        request.return_value = FakeResponse(testxml.getvalue())
        yield request


class FakeResponse:

    def __init__(self, text):
        self.text = text
