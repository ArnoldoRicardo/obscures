import fnmatch
import json
import os
import time

import typer
import youtube_dl
from selenium import webdriver
from selenium.common.exceptions import (ElementNotSelectableException,
                                        ElementNotVisibleException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from youtubesearchpython import VideosSearch

app = typer.Typer()


@app.command()
def get_traks():
    driver = webdriver.Firefox()

    driver.get("https://open.spotify.com/playlist/37i9dQZF1DWXLeA8Omikj7?si=fbdaa76c019a40f8")
    wait = WebDriverWait(driver, timeout=10, poll_frequency=1, ignored_exceptions=[
                         ElementNotVisibleException, ElementNotSelectableException])
    raw_total = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'span.cPwEdQ:nth-child(3)')))
    total = raw_total.text.split(' ')[0]

    traks = set()
    while len(traks) < int(total):
        songs = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tracklist-row"] > div:first-child + div > div')
        last_song = songs[-1]
        songs_text = [s.text for s in songs]
        traks.update(songs_text)
        driver.execute_script("return arguments[0].scrollIntoView(true);", last_song)
        time.sleep(5)

    filter_to_save = [t.split('\n') for t in traks]
    with open('data.json', 'w') as f:
        json.dump(filter_to_save, f)


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


@app.command()
def main():
    f = open('data.json')
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
    app()
