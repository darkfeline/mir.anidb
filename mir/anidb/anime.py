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

"""AniDB HTTP anime API."""

import datetime
from functools import partial
import re
from typing import NamedTuple
import xml.etree.ElementTree as ET

from mir.anidb import api
from mir.anidb._xmlns import XML


def request_anime(client, aid: int) -> 'Anime':
    """Make an anime API request."""
    response = api.httpapi_request(client, request='anime', aid=aid)
    etree = api.unpack_xml_response(response)
    return _unpack_anime(etree.getroot())


class Anime(NamedTuple):
    aid: int
    type: str
    episodecount: int
    startdate: 'Optional[date]'
    enddate: 'Optional[date]'
    titles: 'Tuple[AnimeTitle]'
    episodes: 'Tuple[Episode]'


class AnimeTitle(NamedTuple):
    title: str
    type: str
    lang: str


class Episode(NamedTuple):
    """Episode record.

    epno is a concatenation of type string and episode number.  It should be
    unique among the episodes for an anime, so it can serve as a unique
    identifier.

    type is the episode type code, which is an int.

    length is the length of the episode in minutes.

    title is the episode title.
    """
    epno: str
    type: int
    length: int
    titles: 'Tuple[EpisodeTitle]'


class EpisodeTitle(NamedTuple):
    title: str
    lang: str


def _unpack_anime(element: ET.Element) -> Anime:
    t = partial(_find_element_text, element)
    return Anime(
        aid=int(element.get('id')),
        type=t('type'),
        episodecount=int(t('episodecount')),
        startdate=_parse_date(t('startdate', default='')),
        enddate=_parse_date(t('enddate', default='')),
        titles=tuple(unpack_anime_title(title) for title in element.find('titles')),
        episodes=tuple(_unpack_episode(ep) for ep in element.find('episodes')),
    )


def _find_element_text(element, match, default=None):
    """Find a matching subelement and return its text.

    If default is given, return it if a matching subelement is not
    found.  Otherwise, ValueError is raised.
    """
    child = element.find(match)
    try:
        return child.text
    except AttributeError:
        if default is not None:
            return default
        else:
            raise ValueError


def _parse_date(string: str) -> 'Optional[date]':
    """Parse an ISO 8601 date (YYYY-mm-dd).

    Returns None if parsing fails.

    >>> _parse_date('1990-01-02')
    datetime.date(1990, 1, 2)
    >>> _parse_date('foo') is None
    True
    """
    try:
        return datetime.datetime.strptime(string, '%Y-%m-%d').date()
    except ValueError:
        return None


def unpack_anime_title(element: ET.Element) -> 'Title':
    return AnimeTitle(
        title=element.text,
        type=element.get('type'),
        lang=element.get(f'{XML}lang'),
    )


def _unpack_episode(element: ET.Element):
    """Unpack Episode from episode XML element."""
    return Episode(
        epno=element.find('epno').text,
        type=int(element.find('epno').get('type')),
        length=int(element.find('length').text),
        titles=tuple(_unpack_episode_title(title)
                     for title in element.iterfind('title')),
    )


def _unpack_episode_title(element: ET.Element):
    """Unpack EpisodeTitle from title XML element."""
    return EpisodeTitle(title=element.text,
                        lang=element.get(f'{XML}lang'))


_NUMBER_SUFFIX = re.compile(r'(\d+)$')


def get_episode_number(episode: Episode) -> int:
    """Get the episode number.

    The episode number is unique for an anime and episode type, but not
    across episode types for the same anime.
    """
    match = _NUMBER_SUFFIX.search(episode.epno)
    return int(match.group(1))


def get_episode_title(episode: Episode) -> int:
    """Get the episode title.

    Japanese title is prioritized.
    """
    for title in episode.titles:
        if title.lang == 'ja':
            return title.title
    else:
        return episode.titles[0].title
