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

import functools
import logging
from pathlib import Path
import pickle
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from mir.anidb import api

logger = logging.getLogger(__name__)


def request_titles() -> 'Titles':
    """Request AniDB titles file."""
    response = urlopen('http://anidb.net/api/anime-titles.xml.gz')
    etree = api.unpack_response(response)
    return Titles(etree)


class Titles:

    """XMLTree representation of AniDB anime titles."""

    def __init__(self, root: ET.ElementTree):
        self._root = root

    @classmethod
    def load(cls, file):
        return cls(ET.parse(file))

    def dump(self, file):
        self._root.write(file)

    def search(self, query: 're.Pattern'):
        """Search titles using a compiled RE query."""
        return sorted(self._get_work(anime)
                      for anime in self._find(query))

    def _find(self, query: 're.Pattern'):
        """Yield anime that match the search query."""
        for anime in self._root:
            for title in anime:
                if query.search(title.text):
                    yield anime
                    break

    def _get_work(self, element: ET.Element):
        return Work(
            aid=int(element.attrib['aid']),
            main_title=self._get_main_title(element),
            titles=tuple(title.text for title in element),
        )

    def _get_main_title(self, anime: 'Element'):
        """Get main title of anime Element."""
        for title in anime:
            if title.attrib['type'] == 'main':
                return title.text


@functools.total_ordering
class Work:

    __slots__ = ('aid', 'main_title', 'titles')

    def __init__(self, aid, main_title, titles):
        self.aid = aid
        self.main_title = main_title
        self.titles = titles

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.aid == other.aid
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.aid < other.aid
        else:
            return NotImplemented


class TitlesFetcher:

    """Fetches titles, utilizing a local cache."""

    def __init__(self, cachedir: 'PathLike'):
        self._cachedir = Path(cachedir)
        self._caches = [
            _PickleCache(self._pickle_file),
            _FileCache(self._titles_file),
        ]

    def get_titles(self, force=False) -> Titles:
        titles: Titles
        missing: 'List[Cache]'
        if force:
            titles, missing = None, self._caches
        else:
            titles, missing = self._load_from_caches()
        if titles is None:
            titles = request_titles()
        self._make_missing_caches(titles, missing)
        return titles

    def _load_from_caches(self):
        titles = None
        missing = []
        for cache in self._caches:
            try:
                titles = cache.load()
            except Exception as e:
                logger.warning('Error loading cache %r: %s', cache, e)
                missing.append(cache)
            else:
                break
        return titles, missing

    def _make_missing_caches(self, titles, missing):
        for cache in reversed(missing):
            cache.dump(titles)

    @property
    def _titles_file(self):
        """Anime titles data file path."""
        return self._cachedir / 'anime-titles.xml'

    @property
    def _pickle_file(self):
        """Pickled anime titles data file path."""
        return self._cachedir / 'anime-titles.pickle'


class _PickleCache:

    _PROTOCOL = 4

    def __init__(self, file):
        self._file = file

    def __repr__(self):
        cls = type(self).__qualname__
        return f'{cls}({self._file!r})'

    def load(self):
        with self._file.open('rb') as file:
            return pickle.load(file, protocol=self._PROTOCOL)

    def dump(self, titles: Titles):
        with self._file.open('wb') as file:
            pickle.dump(titles, file, protocol=self._PROTOCOL)


class _FileCache:

    def __init__(self, file):
        self._file = file

    def __repr__(self):
        cls = type(self).__qualname__
        return f'{cls}({self._file!r})'

    def load(self):
        with self._file.open('r') as file:
            return Titles.load(file)

    def dump(self, titles: Titles):
        with self._file.open('w') as file:
            titles.dump(file)
