import datetime

from mir.anidb.anime import Anime
from mir.anidb.anime import AnimeTitle
from mir.anidb.anime import Episode
from mir.anidb.anime import EpisodeTitle

obj = Anime(
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
