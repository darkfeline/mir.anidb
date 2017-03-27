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

import datetime
import io
from pathlib import Path
from unittest import mock

import pytest

from mir.anidb import api
from mir.anidb import anime
from mir.anidb.anime import AnimeTitle
from mir.anidb.anime import Episode
from mir.anidb.anime import EpisodeTitle


def test_request_anime(testrequest):
    client = api.Client('foo', 1)
    got = anime.request_anime(client, 22)
    testrequest.assert_called_once_with(client, request='anime', aid=22)
    assert got == _TEST_ANIME


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


_TEST_ANIME = anime.Anime(
    aid=22,
    type='TV Series',
    episodecount=26,
    startdate=datetime.date(1995, 10, 4),
    enddate=datetime.date(1996, 3, 27),
    titles=(
        AnimeTitle(title='Shinseiki Evangelion',
                         type='main',
                         lang='x-jat'),
        AnimeTitle(title='Neon Genesis Evangelion',
                         type='official',
                         lang='en'),
    ),
    episodes=(
        Episode(
            epno='1',
            type=1,
            length=25,
            titles=(
                EpisodeTitle(title='\u4f7f\u5f92, \u8972\u6765', lang='ja'),
                EpisodeTitle(title='Angel Attack!', lang='en'),
                EpisodeTitle(title='Shito, Shuurai', lang='x-jat'),
            )),
        Episode(
            epno='S1',
            type=2,
            length=75,
            titles=(
                EpisodeTitle(title='Revival of Evangelion Extras Disc',
                             lang='en'),
            )),
    ),
)
_TESTXML = Path(__file__).parent / 'data' / 'anime.xml'


@pytest.fixture
def testxml():
    with open(_TESTXML) as file:
        return io.StringIO(file.read())


@pytest.fixture
def testrequest(testxml):
    with mock.patch('mir.anidb.api.httpapi_request') as request:
        request.return_value = FakeResponse(testxml.getvalue())
        yield request


class FakeResponse:

    def __init__(self, text):
        self.text = text
