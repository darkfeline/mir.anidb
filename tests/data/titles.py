from mir.anidb.titles import Titles
from mir.anidb.anime import AnimeTitle

obj = [
    Titles(
        aid=22,
        titles=(
            AnimeTitle(title='Neon Genesis Evangelion',
                       type='official',
                       lang='en'),
            AnimeTitle(title='Shinseiki Evangelion',
                       type='main',
                       lang='x-jat'),
        ),
    ),
]
