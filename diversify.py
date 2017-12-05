"""
Bryan Lin
November 2017
ENGM 3700 Project
https://github.com/bryanlin850/diversify
"""
import requests
from bs4 import BeautifulSoup

base_url = "http://api.genius.com"
headers = {
    'Authorization': 'Bearer d2FBpnZfxtalLk0GwBF6noxKVwl-8FiH3tifBroK6LfyPG90EeAc-mSCkyoBlviT'}

song_title = "Attention"
artist_name = "Charlie Puth"


def lyrics_from_song_api_path(song_api_path):
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
    search_url = base_url + "/search"
    data = {'q': song_title}
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
    q = 'Verse 1'
    lyrics = lyrics.split('[')
    lyrics = lyrics[:-1]
    base_lyr = ''
    for sect in lyrics:
        if sect.startswith(q):
            base_lyr = sect
            break
    base_lyr = base_lyr.split(']')
    base_lyr = base_lyr[1]
    base_lyr = base_lyr.split('\n')
    base_lyr[:] = [item for item in base_lyr if item]
    time_name = ''
    if song_title is 'Attention':
        time_name = 'lyrics/attention.txt'
    elif song_title is 'Praying':
        time_name = 'lyrics/praying.txt'
    else:
        time_name = 'lyrics/feel_it_still.txt'
    time_lyr = ''
    time = ''
    with open(time_name, 'r') as f:
        time_lyr = f.read()
        time_lyr = time_lyr.split('\n\n')
        time_lyr[:] = [item.replace('\n', '').split('[') for item in time_lyr]
        time_lyr[:] = [[item.split(']') for item in para[1:]]
                       for para in time_lyr]
        found_bool = False
        for para in time_lyr:
            if found_bool:
                break
            i = 0
            for line in para:
                if line[1] == base_lyr[i]:
                    time = para[0][0]
                    i += 1
                    if i == len(base_lyr):
                        found_bool = True
                        break
                else:
                    break
    print(time)
