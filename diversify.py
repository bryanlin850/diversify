"""
Bryan Lin
November 2017
ENGM 3700 Project
https://github.com/bryanlin850/diversify
"""
from musixmatch import Musixmatch
import re
import json
# API key
musixmatch = Musixmatch('51407cabf3a6af689162aa66cf2be0d8')

def get_lyrics(trackName, artistName):
    tr = musixmatch.matcher_track_get(q_track=trackName, q_artist=artistName)
    return tr
tr = get_lyrics('Attention', 'Charlie Puth')
tr_id = tr['message']['body']['track']['track_id']
print(musixmatch.track_subtitle_get(tr_id))
