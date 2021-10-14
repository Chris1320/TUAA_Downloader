"""
TUAA_downloader.py

The (maybe) stable version of TUAA downloader.

Their [Downloader application](https://github.com/TheUnusAnnusArchive/TUAA-Downloader/) doesn't work most of the times (at least for me) and I'm too lazy to try to fix it so I decided to do it in Python.

This python script can be imported to another script so you can use the API.

Example Usage:

```python

import json
from TUAA_downloader import API

tuaa_api = API()

season = 1
episode = 4
quality = 1080  # Download in 1080p

metadata = tuaa_api.get_metadata(season, episode)  # Get the metadata of season 1's 4th episode.

metadata = json.loads(metadata.content)  # Convert JSON to Python dictionary.

# Do something with the metadata
print(f"Downloading {metadata['title']}...")
tuaa_api.get_video_data(season, episode, "video.mp4", quality)  # Save file to `video.mp4`
```

The API can download the videos, metadata, thumbnails/posters, and subtitles.

If you just want to automate the download of multiple episodes,
import the Main class instead.

```python

from TUAA_downloader import Main

episodes_to_download = {
    0: (2, 4, 6, 8),  # Download episodes 2, 4, 6, and 8 of season 0. (Specials)
    1: (10, 12, 14, 17)  # Download episodes 10, 12, 14, and 17 of season 1.
}

quality = 1080  # Download videos in 1080p quality.

for season in episodes_to_download:
    for episode in episodes_to_download[season]:
        Main(season, episode).main()
```
"""

import os
import sys
import json

import requests
from tqdm import tqdm


class API():
    def __init__(self):
        """
        The initialization method of API() class.
        """

        self.endpoint = "https://unusannusarchive.tk/api"  # This is the API that provides metadata.
        self.cdn = "https://cdn.unusannusarchive.tk"  # This where the video files are stored.

        self.extensions = {
            "video": "mp4",
            "subtitles": "vtt",
            "thumbnail": "jpg",
            "nfo": "nfo"
        }
        self.video_qualities = (2160, 1440, 1080, 720, 480, 360, 240)

    def _download(self, url: str, fname: str, s: int = None, e: int = None):
        """
        Download <url> with tqdm progress bar.

        :param str url: The URL of the file to be downloaded.
        :param str fname: The filename of the output; Where to write the data to
        :param int s: Season number
        :param int e: Episode number

        :returns int: `0` if download is successful. `1` if the download is not completed. `2` if the downloaded file is larger than the expected size.
        """

        resp = requests.get(url, stream=True)
        total = int(resp.headers.get('content-length', 0))
        if s is None or e is None:
            desc = f"Downloading to {fname}..."

        else:
            desc = f"Downloading S{s}E{e}..."

        with open(fname, 'wb') as file, tqdm(
            desc=desc,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024
        ) as bar:
            downloaded_size = 0
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
                downloaded_size += size

            # * These are just for debugging. (DEV0005)
            # print("DLS   :", downloaded_size)
            # print("total:", total)

            if downloaded_size < total:
                return 1  # Success is False; Not successful

            elif downloaded_size > total:
                return 2  # This is suspicious if this happens.

            elif downloaded_size == total:
                return 0  # Success is True; Successful

    def _check(self, value: str, vtype: str):
        """
        Check if the value is right, depending on type.

        :param str value: The value to check.
        :param str vtype: `s` for season numbers or `e` for episode numbers.

        :returns str: Processed version of the value.
        """

        if vtype == 's':
            if len(str(value)) < 2:
                value = f"0{value}"

            return value

        elif vtype == 'e':
            while len(str(value)) < 3:
                value = "0" + str(value)

            return value

    def get_metadata(self, s: int = None, e: int = None, dl_all: bool = False):
        """
        Get episode <e> of season <s> metadata from <self.endpoint>.

        :param int s: Season number (Not needed if dl_all is True)
        :param int e: Episode number (Not needed if dl_all is True)
        :param bool dl_all: Download all season and episode metadata

        :returns obj: requests response object.
        """

        if dl_all:
            r = requests.get(f"{self.endpoint}/v2/metadata/video/all")

        else:
            s = self._check(s, 's')
            e = self._check(e, 'e')
            r = requests.get(f"{self.endpoint}/v2/metadata/video/episode/s{s}.e{e}")

        return r

    def get_thumbnail(self, s: int, e: int):
        """
        Get thumbnail of season <s> episode <e>.

        :param int s: Season number.
        :param int e: Episode number.

        :returns bytes: thumbnail data in jpg format.
        """

        s = self._check(s, 's')
        e = self._check(e, 'e')

        return requests.get(f"{self.cdn}/thumbnails/{s}/{e}.{self.extensions['thumbnail']}").content

    def get_video_data(self, season: int, episode: int, filepath: str, quality: int = 1080):
        """
        Get the actual video data from the CDN.

        :param int season: Season number
        :param int episode: Episode number
        :param str filepath: Where to store the downloaded video.
        :param int quality: `1080` for 1080p, (Other options: `2160`, `1440`, `720`, `480`, `360`, `240`)

        :returns void:
        """

        season = self._check(season, 's')
        episode = self._check(episode, 'e')

        if quality not in self.video_qualities:
            raise ValueError("Invalid quality parameter!")

        # return requests.get(f"{self.cdn}/{season}/{episode}/{quality}.{self.extensions['video']}").content
        return self._download(f"{self.cdn}/{season}/{episode}/{quality}.{self.extensions['video']}", filepath, season, episode)

    def get_subtitle(self, s: int, e: int, language: str = None, dl_all: bool = False):
        """
        Get subtitles of season <s> episode <e>.

        :param int s: Season number.
        :param int e: Episode number.
        :param str language: The language to download. (Country code like `en` for English)
        :param bool dl_all: Download all available subtitles.

        :returns dict: A dictionary containing the subtitles in <bytes>. Returns an empty dictionary if no subtitles are found.
        """

        s = self._check(s, 's')
        e = self._check(e, 'e')

        if not dl_all:
            if language is None:
                raise ValueError("You need to set `language` if dl_all is False.")

            r = requests.get(f"{self.cdn}/subs/{s}/{e}.{language}.{self.extensions['subtitles']}")
            if r.status_code == 200:
                return {language: r.content}

            else:
                return {}

        else:
            md = self.get_metadata(int(s), int(e))
            result = {}
            for tracks in json.loads(md.content)["tracks"]:
                result[tracks["srclang"]] = requests.get(f"{self.cdn}/subs/{s}/{e}.{tracks['srclang']}.{self.extensions['subtitles']}").content

            return result

    def gen_nfo(self, s: int, e: int, show_path=os.path.join("E:\\HomeTheater", "YouTube Series", "Unus Annus (2019)")):
        """
        Generate NFO using self.get_metadata().
        NOTE: This method have hardcoded variables.

        :param int s: Season number.
        :param int e: Episode number.

        :returns str: NFO output.
        """

        sf = self._check(s, 's')
        meta = json.loads(self.get_metadata(s, e).content)
        title = meta.get("title", "Unus Annus")
        plot = meta.get("description", "")

        return f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<episodedetails>
  <plot>{plot}</plot>
  <outline />
  <lockdata>true</lockdata>
  <title>{title}</title>
  <imdbid>tt11289784</imdbid>
  <actor>
    <name>Mark Fishbach</name>
    <role>Markiplier</role>
    <type>Actor</type>
    <sortorder>0</sortorder>
  </actor>
  <actor>
    <name>Ethan Nestor</name>
    <role>CrankGameplays</role>
    <type>Actor</type>
    <sortorder>1</sortorder>
  </actor>
  <episode>{e}</episode>
  <season>{s}</season>
</episodedetails>"""


class Main():
    def __init__(self, season: int, episode: int, quality: int = 1080):
        self.s = season
        self.e = episode
        self.quality = quality
        self.api = API()
        self.retries = 3  # Maximum retries

    def main(self):
        s = self.api._check(self.s, 's')
        e = self.api._check(self.e, 'e')
        filename = f"Unus Annus S{self.s}E{self.e}"
        sf = f"Season {s}"  # Season folder
        ef = os.path.join(f"{sf}", f"Unus Annus S{self.s}E{self.e}")  # Episode folder

        print("Creating folder...")
        os.makedirs(ef, exist_ok=True)

        print("Downloading subtitles...")
        subs = self.api.get_subtitle(
            s=self.s,
            e=self.e,
            language=None,
            dl_all=True
        )
        print("Downloading thumbnail...")
        poster = self.api.get_thumbnail(
            s=self.s,
            e=self.e
        )

        print("Writing thumbnail to file...")
        with open(os.path.join(ef, f"thumb.{self.api.extensions['thumbnail']}"), 'wb') as f:
            f.write(poster)

        for lang in subs:
            print(f"Writing `{lang}` subtitles to file...")
            with open(os.path.join(ef, f"{filename}.{lang}.{self.api.extensions['subtitles']}"), 'wb') as f:
                f.write(subs[lang])

        print("Generating NFO...")
        with open(os.path.join(ef, f"{filename}.{self.api.extensions['nfo']}"), 'wb') as f:
            f.write(self.api.gen_nfo(self.s, self.e).encode("utf-8"))

        if os.path.isfile(os.path.join(ef, f"{filename}.{self.api.extensions['video']}")):
            print("Skipping video because it already exists.")

        else:
            print("Downloading video... (Might take a long time)")
            video_dl_retries = 0
            while self.api.get_video_data(
                season=self.s,
                episode=self.e,
                filepath=os.path.join(ef, f"{filename}.{self.api.extensions['video']}"),
                quality=self.quality
            ) != 0:
                if video_dl_retries == self.retries:
                    print("Failed to download video and maximum retries reached.")
                    break

                os.remove(os.path.join(ef, f"{filename}.{self.api.extensions['video']}"))
                video_dl_retries += 1
                print(f"Video download of S{s}E{e} failed. Retrying... ({video_dl_retries}/{self.retries})")

        print("Done!")
        return 0


def __dl(s, e):
    """
    A private function to be used below.
    """

    print(f"Downloading S{s}E{e}...")
    return Main(
        season=s,
        episode=e,
        quality=q
    ).main()


if __name__ == "__main__":
    try:
        s = int(sys.argv[1])
        if '-' not in sys.argv[2]:
            e = int(sys.argv[2])

        else:
            e = (int(sys.argv[2].partition('-')[0]), int(sys.argv[2].partition('-')[2]))
            if e[0] == e[1]:
                e = e[0]

            elif e[0] > e[1]:
                i = -1  # Generate a range object with step of -1; Decrement.

            else:
                i = 1

    except(IndexError, ValueError):
        print(f"USAGE: {sys.argv[0]} <season number> <episode number> <optional quality>")
        print(f"USAGE: {sys.argv[0]} <season number> <episode number range> <optional quality>")
        print()
        print("EXAMPLES:")
        print(f"    {sys.argv[0]} 1 3        # Downloads Season 1 Episode 3")
        print(f"    {sys.argv[0]} 0 6 720    # Downloads Season 0 Episode 6 in 720p")
        print(f"    {sys.argv[0]} 1 2-5      # Downloads Season 1 Episodes 2, 3, 4, and 5.")
        print()
        print("AVAILABLE QUALITIES:")
        available_qualities = ""
        print('p, '.join(map(lambda x: available_qualities + str(x), API().video_qualities)) + 'p')
        sys.exit(1)

    try:
        q = int(sys.argv[3])

    except IndexError:
        q = 1080  # Default quality

    if type(e) is int:
        sys.exit(__dl(s, e))

    else:
        ec = 0  # Error code
        if i == -1:
            e_range = range(e[0], (e[1] - 1), i)

        else:
            e_range = range(e[0], (e[1] + 1), i)

        print(f"Downloading S{s}E{e[0]}-{e[1]}... ({len(e_range)} episodes)")

        for current_episode in e_range:
            print()
            ec += __dl(s, current_episode)
            pass

        sys.exit(ec)
