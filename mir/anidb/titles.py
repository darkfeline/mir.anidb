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

"""AniDB titles API.

https://wiki.anidb.net/w/API#Anime_Titles

In the AniDB documentation, this "API" is included with the other APIs,
but it's really just fetching a single XML file with all the titles
data.
"""

import abc
import logging
from pathlib import Path
import pickle
from typing import NamedTuple
import xml.etree.ElementTree as ET

from mir.anidb import api
from mir.anidb.anime import unpack_anime_title

logger = logging.getLogger(__name__)


class Titles(NamedTuple):
    aid: int
    titles: 'Tuple[AnimeTitle]'


class CachedTitlesGetter:

    """Cached getter for work titles.

    cache is a Cache subclass.  requester is a function that is
    responsible for returning a list of titles.
    """

    def __init__(self, cache, requester):
        self._cache = cache
        self._requester = requester

    def __repr__(self):
        cls = type(self).__qualname__
        return f'{cls}({self._cache!r}, {self._requester!r})'

    def get(self, force=False) -> 'List[Titles]':
        """Get list of Titles.

        Pass force=True to bypass the cache.
        """
        try:
            if force:
                raise CacheMissingError
            return self._cache.load()
        except CacheMissingError:
            titles = self._requester()
            self._cache.save(titles)
            return titles


class Cache(abc.ABC):

    """Abstract base class for Titles caches."""

    @abc.abstractmethod
    def load(self) -> 'List[Titles]':
        """Load work titles from the cache.

        Raises _CacheMissingError if cache could not be loaded.
        """
        raise CacheMissingError

    @abc.abstractmethod
    def save(self, titles):
        """Save work titles to the cache."""


class CacheMissingError(Exception):
    """Cache could not be loaded."""


class PickleCache(Cache):

    """Cache implemented with pickle."""

    _PROTOCOL = 4

    def __init__(self, path: 'PathLike'):
        self._path = Path(path)

    def __repr__(self):
        cls = type(self).__qualname__
        return f'{cls}({str(self._path)!r})'

    def load(self) -> 'List[Titles]':
        try:
            with self._path.open('rb') as file:
                return pickle.load(file)
        except IOError:
            raise CacheMissingError

    def save(self, titles):
        with self._path.open('wb') as file:
            pickle.dump(titles, file, protocol=self._PROTOCOL)


def api_requester() -> 'List[Titles]':
    """Request Titles from AniDB API."""
    etree = _request_titles_xml()
    return list(_unpack_titles(etree))


class CopyingRequester:

    """Request Titles from AniDB API, saving a copy of the XML."""

    def __init__(self, path: 'PathLike'):
        self._path = Path(path)

    def __repr__(self):
        cls = type(self).__qualname__
        return f'{cls}({str(self._path)!r})'

    def __call__(self) -> 'List[Titles]':
        """Request titles from AniDB API."""
        etree = _request_titles_xml()
        with self._path.open('wb') as file:
            etree.write(file)
        return list(_unpack_titles(etree))


def _request_titles_xml() -> ET.ElementTree:
    """Request AniDB titles file."""
    response = api.titles_request()
    return api.unpack_xml_response(response)


def _unpack_titles(etree: ET.ElementTree) -> 'Generator':
    """Unpack Titles from titles XML."""
    for anime in etree.getroot():
        yield Titles(
            aid=int(anime.get('aid')),
            titles=tuple(unpack_anime_title(title) for title in anime),
        )
