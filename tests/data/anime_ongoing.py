import datetime

from mir.anidb.anime import Anime
from mir.anidb.anime import AnimeTitle
from mir.anidb.anime import Episode
from mir.anidb.anime import EpisodeTitle

obj = Anime(
    aid=11223,
    type='TV Series',
    episodecount=24,
    startdate=datetime.date(2017, 4, 8),
    enddate=None,
    titles=(
        AnimeTitle(title='Shingeki no Bahamut: Virgin Soul',
                   type='main',
                   lang='x-jat'),
    ),
    episodes=(
        Episode(
            epno='4',
            type=1,
            length=25,
            titles=(
                EpisodeTitle(title='Firestarter', lang='ja'),
                EpisodeTitle(title='Firestarter', lang='en'),
                EpisodeTitle(title='Firestarter', lang='x-jat'),
            )),
    ),
)
