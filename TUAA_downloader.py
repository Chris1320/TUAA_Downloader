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
        self.endpoint = "https://unusannusarchive.tk/api"  # This is the API that provides metadata.
        self.cdn = "https://cdn.unusannusarchive.tk"  # This where the video files are stored.

        self.extensions = {
            "video": "mp4",
            "subtitles": "vtt",
            "thumbnail": "jpg",
            "nfo": "nfo"
        }

    def _download(self, url: str, fname: str):
        resp = requests.get(url, stream=True)
        total = int(resp.headers.get('content-length', 0))
        with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024
        ) as bar:
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)

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

        if quality not in (2160, 1440, 1080, 720, 480, 360, 240):
            raise ValueError("Invalid quality parameter!")

        # return requests.get(f"{self.cdn}/{season}/{episode}/{quality}.{self.extensions['video']}").content
        return self._download(f"{self.cdn}/{season}/{episode}/{quality}.{self.extensions['video']}", filepath)

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
        runtime = meta.get("duration", 0)
        if runtime > 0:
            runtime = round((runtime / 60) / 60)  # Convert to hours

        return f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<episodedetails>
  <plot>{plot}</plot>
  <outline />
  <lockdata>true</lockdata>
  <title>{title}</title>
  <imdbid>tt11289784</imdbid>
  <runtime>{runtime}</runtime>
  <art>
    <poster>{show_path}\\Season {sf}\\Unus Annus S{s}E{e}\\metadata\\Unus Annus S{s}E{e}.jpg</poster>
  </art>
  <actor>
    <name>Ethan Nestor</name>
    <role>CrankGameplays</role>
    <type>Actor</type>
    <thumb>E:\\HomeTheater\\Server\\Jellyfin\\Server\\metadata\\People\\E\\Ethan Nestor\\folder.jpg</thumb>
  </actor>
  <actor>
    <name>Mark Fishbach</name>
    <role>Markiplier</role>
    <type>Actor</type>
    <thumb>E:\\HomeTheater\\Server\\Jellyfin\\Server\\metadata\\People\\M\\Mark Fishbach\\folder.jpg</thumb>
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

    def main(self):
        s = self.api._check(self.s, 's')
        e = self.api._check(self.e, 'e')
        filename = f"Unus Annus S{self.s}E{self.e}"
        sf = f"Season {s}"  # Season folder
        ef = os.path.join(f"{sf}", f"Unus Annus S{self.s}E{self.e}")  # Episode folder
        mf = os.path.join(f"{ef}", "metadata")  # Metadata folder

        print("Creating folder...")
        os.makedirs(mf, exist_ok=True)

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
        with open(os.path.join(mf, f"{filename}.{self.api.extensions['thumbnail']}"), 'wb') as f:
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
            self.api.get_video_data(
                season=self.s,
                episode=self.e,
                filepath=os.path.join(ef, f"{filename}.{self.api.extensions['video']}"),
                quality=self.quality
            )

        print("Done!")
        return 0


if __name__ == "__main__":
    s = int(sys.argv[1])
    e = int(sys.argv[2])
    try:
        q = int(sys.argv[3])

    except IndexError:
        q = 1080

    sys.exit(Main(
        season=s,
        episode=e,
        quality=q
    ).main())
