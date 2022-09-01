import fnmatch
import json
import os

import youtube_dl
from youtubesearchpython import VideosSearch


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def main():
    f = open('lista.json')
    data = json.load(f)

    for music in data:
        name = f'{music[0]} - {music[1]}'
        videos_search = VideosSearch(name, limit=1)
        link = videos_search.result()['result'][0]['link']
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        code = link.split('=')[-1]
        foud_files = find(f'*{code}.mp3', '.')
        if len(foud_files) < 1:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        else:
            print('descargado')

    f.close()


if __name__ == "__main__":
    main()
