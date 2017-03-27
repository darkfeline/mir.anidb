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
import re
from typing import NamedTuple
import xml.etree.ElementTree as ET

from mir.anidb import api

#from animanager.date import parse_date
#from animanager.xml import XMLTree


def request_anime(client, aid: int):
    """Make an anime API request."""
    response = api.httpapi_request(client, request='anime', aid=aid)
    etree = api.unpack_xml_response(response)
    ...


class AnimeTree:

    """XMLTree repesentation of an anime."""

    @property
    def aid(self) -> int:
        """AniDB ID (AID)."""
        return int(self.root.get('id'))

    @property
    def type(self) -> str:
        """Anime type."""
        return self.root.find('type').text

    @property
    def episodecount(self) -> int:
        """Number of episodes."""
        return int(self.root.find('episodecount').text)

    @property
    def startdate(self) -> 'Optional[datetime.date]':
        """Start date of anime."""
        text = self.root.find('startdate').text
        try:
            return parse_date(text)
        except ValueError:
            return None

    @property
    def enddate(self) -> 'Optional[datetime.date]':
        """End date of anime."""
        text = self.root.find('enddate').text
        try:
            return parse_date(text)
        except ValueError:
            return None

    @property
    def title(self) -> str:
        """Main title."""
        for element in self.root.find('titles'):
            if element.get('type') == 'main':
                return element.text

    @property
    def episodes(self) -> 'Iterable[Episode]':
        """The anime's episodes."""
        for element in self.root.find('episodes'):
            yield Episode(element)


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


def _unpack_episode(element: ET.Element):
    return Episode(
        epno=element.find('epno').text,
        type=int(element.find('epno').get('type')),
        length=int(element.find('length').text)
    )


def _unpack_title(element: ET.Element):
    for title in element.iterfind('title'):
        if title.get('xml:lang') == 'ja':
            return title.text
    else:
        # In case there's no Japanese title.
        return element.find('title').text


_NUMBER_SUFFIX = re.compile(r'(\d+)$')


def _get_episode_number(episode: Episode) -> int:
    """Get the episode number.

    The episode number is unique for an anime and episode type, but not
    across episode types for the same anime.
    """
    match = _NUMBER_SUFFIX.search(episode.epno)
    return int(match.group(1))
