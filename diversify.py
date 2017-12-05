"""
Bryan Lin
November 2017
ENGM 3700 Project
https://github.com/bryanlin850/diversify
"""
import requests
from bs4 import BeautifulSoup
import pygame
import time as tlib

base_url = "http://api.genius.com"
headers = {
    'Authorization': 'Bearer d2FBpnZfxtalLk0GwBF6noxKVwl-8FiH3tifBroK6LfyPG90EeAc-mSCkyoBlviT'}


def lyrics_from_song_api_path(song_api_path):
    """
    Find lyrics given an API path
    @params:
        song_api_path, endpoint to the desired song
    @return:
        lyrics, a string of all the lyrics
    """
    song_url = base_url + song_api_path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json['response']['song']['path']
    # gotta go regular html scraping... come on Genius
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    # remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    # at least Genius is nice and has a tag called 'lyrics'!
    # updated css where the lyrics are based in HTML
    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics


if __name__ == "__main__":
    # search URL is http://api.genius.com/search
    search_url = base_url + "/search"
    song_title = input('Enter the song title: ')
    if song_title == "Attention":
        song_title = "Attention"
    elif song_title == "Praying":
        song_title = "Praying"
    else:
        song_title = "Feel It Still"
    artist_name = input('Enter the artist name: ')
    if artist_name == "Charlie Puth":
        artist_name = "Charlie Puth"
    elif artist_name == "Kesha":
        artist_name = "Kesha"
    else:
        artist_name = "Portugal. The Man"
    data = {'q': song_title}
    # putting together the request for the requests library
    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    song_info = None
    for hit in json['response']['hits']:
        if hit["result"]["primary_artist"]["name"] == artist_name:
            song_info = hit
            break
    lyrics = ''
    if song_info:
        song_api_path = song_info["result"]["api_path"]
        lyrics = lyrics_from_song_api_path(song_api_path)
        lyrics += '[]'

    # q is the query
    # After Alexa integration, the query will be input by the user with voice input.
    # For now, the query is specified in the code or through the command line.
    q = input('Enter the desired section: ')
    # split the lyrics by the '[' character
    lyrics = lyrics.split('[')
    # take everything but the last character (which will always be ']')
    lyrics = lyrics[: -1]
    base_lyr = ''
    for sect in lyrics:
        # search the Genius lyrics for the desired section
        if sect.startswith(q):
            base_lyr = sect
            break
    
    """
    The lyrics in their current form look something like this:
        Verse 1]\n
        You've been runnin' 'round, runnin' 'round, runnin' 'round\n
        Throwin' that dirt all on my name\n
        ...
    So we need to strip the extra ']' while keeping the timestamp somehow separate
    from the text. The ']' provides a convenient character to split each string on.
    The end result is a 2-element list of strings where the first element is the 
    timestamp and the second element is the lyrics for that section.
    We throw away the first element and split the second section on the '\n'
    character, and creating a list of strings where each element is a different
    line of the lyrics.
    """
    base_lyr = base_lyr.split(']')
    base_lyr = base_lyr[1]
    base_lyr = base_lyr.split('\n')
    # clean up the lyrics by removing empty elements
    base_lyr[:] = [item for item in base_lyr if item]
    time_name = ''
    mp3_name = ''
    if song_title is 'Attention':
        time_name = 'lyrics/attention.txt'
        mp3_name = 'songs/attention.ogg'
    elif song_title is 'Praying':
        time_name = 'lyrics/praying.txt'
        mp3_name = 'songs/praying.ogg'
    else:
        time_name = 'lyrics/feel_it_still.txt'
        mp3_name = 'songs/feel_it_still.ogg'
    time_lyr = ''
    time = ''
    with open(time_name, 'r') as f:
        time_lyr = f.read()
        """
        The timed lyrics in their current form look something like this:
            [00:04.32]Woah-oah, hm-hmm
            \n\n
            [00:09.58]You've been runnin' 'round, runnin' 'round, runnin' 'round\n
            [00:11.69]Throwin' that dirt all on my name\n
            ...
        Note that there are two '\n' characters between sections. We take 
        advantage of this and split the string on occurences of '\n\n' to get
        a list of strings where each element is a different section of the song.
        """
        time_lyr = time_lyr.split('\n\n')
        """
        The timed lyrics now look something like this:
            [
                "[00:04.32]Woah-oah, hm-hmm",
                "[00:09.58]You've been runnin' 'round, runnin' 'round, runnin' 'round"
                "[00:11.69]Throwin' that dirt all on my name"
                ...
            ]
        Each element is a different section of the song as previous.
        This list comprehension replaces every '\n' with '' and also splits
        each section on the '[' character, turning the Verse 1 section, for
        example, into:
            [
                "00:09.58]You've been runnin' 'round, runnin' 'round, runnin' 'round",
                "00:11.69]Throwin' that dirt all on my name",
                ...
            ]
        Once again, splitting on the ']' character gives a conveniently separated 
        list that looks like [[timestamp1, line1], [timestamp2, line2], ...]
        The lines will be searched line by line to see if it matches with the lyrics
        query and the timestamp will be returned if it does match.
        """
        time_lyr[:] = [item.replace('\n', '').split('[') for item in time_lyr]
        time_lyr[:] = [[item.split(']') for item in sect[1:]]
                       for sect in time_lyr]
        found_bool = False
        for sect in time_lyr:
            if found_bool:
                break
            i = 0
            for line in sect:
                if line[1] == base_lyr[i]:
                    time = sect[0][0]
                    i += 1
                    if i == len(base_lyr):
                        found_bool = True
                        break
                else:
                    break
    time_float = 60.0 * float(time[0:2]) + float(time[3:])
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_name)
    if time_float > 2.0:
        time_float -= 2.0
    pygame.mixer.music.play(0, time_float)
    stop_cmd = ''
    while stop_cmd != 'stop':
        stop_cmd = input('Enter stop to stop the music: ')
        if stop_cmd == 'stop':
            pygame.mixer.music.stop()
