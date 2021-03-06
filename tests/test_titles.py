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

import collections
import io
import xml.etree.ElementTree as ET
from unittest import mock

import pytest

from mir.anidb import titles

from . import testlib


def test_CachedTitlesGetter_repr():
    getter = titles.CachedTitlesGetter(
        mock.sentinel.cache, mock.sentinel.requester)
    assert repr(getter) == \
        "CachedTitlesGetter(sentinel.cache, sentinel.requester)"


def test_CachedTitlesGetter_get_cache_force_should_skip_cache():
    cache = _FakeCache()
    cache.save(mock.sentinel.cached_titles)
    requester = _StubRequester([mock.sentinel.titles])
    getter = titles.CachedTitlesGetter(cache, requester)
    assert getter.get(force=True) == mock.sentinel.titles


def test_CachedTitlesGetter_get_cache_miss_should_call_requester():
    cache = _FakeCache()
    requester = _StubRequester([mock.sentinel.titles])
    getter = titles.CachedTitlesGetter(cache, requester)
    assert getter.get() == mock.sentinel.titles
    assert cache.load() == mock.sentinel.titles


def test_CachedTitlesGetter_get_cache_hit_should_skip_requester():
    cache = _FakeCache()
    cache.save(mock.sentinel.cached_titles)
    requester = _StubRequester([])
    getter = titles.CachedTitlesGetter(cache, requester)
    assert getter.get() == mock.sentinel.cached_titles


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


def test_api_requester(test_xml):
    xml, obj = test_xml
    with mock.patch('mir.anidb.api.titles_request') as request:
        request.return_value = testlib.FakeResponse(xml)
        got = titles.api_requester()
    assert got == obj


def test_request_titles(test_xml):
    xml, obj = test_xml
    with mock.patch('mir.anidb.api.titles_request') as request:
        request.return_value = testlib.FakeResponse(xml)
        got = titles.request_titles()
    assert got == obj


def test_CopyingRequester_repr():
    requester = titles.CopyingRequester('tmp')
    assert repr(requester) == "CopyingRequester('tmp')"


def test_CopyingRequester(test_xml, tmpdir):
    xml, obj = test_xml
    copypath = tmpdir / 'copy.xml'
    with mock.patch('mir.anidb.api.titles_request') as request:
        request.return_value = testlib.FakeResponse(xml)
        got = titles.CopyingRequester(copypath)()
    assert got == obj


def test_CopyingRequester_saves_xml_copy(test_xml, tmpdir):
    xml, obj = test_xml
    copypath = tmpdir / 'copy.xml'
    with mock.patch('mir.anidb.api.titles_request') as request:
        request.return_value = testlib.FakeResponse(xml)
        got = titles.CopyingRequester(copypath)()
    assert list(titles._unpack_titles(ET.parse(copypath))) == got


def test__unpack_titles(test_xml):
    xml, obj = test_xml
    etree = ET.parse(io.StringIO(xml))
    got = list(titles._unpack_titles(etree))
    assert got == obj


_TEST_TITLES = testlib.load_obj('titles.py')


@pytest.fixture(params=[
    ('titles.xml', 'titles.py'),
])
def test_xml(request):
    xml_path, obj_path = request.param
    xml = testlib.load_text(xml_path)
    obj = testlib.load_obj(obj_path)
    return xml, obj


class _FakeCache(titles.Cache):

    def __init__(self):
        self._titles = None

    def load(self):
        if self._titles is None:
            raise titles.CacheMissingError
        else:
            return self._titles

    def save(self, titles):
        self._titles = titles


class _StubRequester:

    def __init__(self, values):
        self._values = collections.deque(values)

    def __call__(self):
        if self._values:
            return self._values.popleft()
        else:  # pragma: no cover
            raise _UnexpectedCallError


class _UnexpectedCallError(Exception):
    pass
