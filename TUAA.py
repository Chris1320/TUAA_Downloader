"""
The Unus Annus Archive Downloader (TUAA Downloader)

A python script I made for downloading videos from the Unus Annus Archive (https://unusann.us/).
This script is tested on *Windows 10/11*, Termux (Android), and *Kali Linux*.

Their Downloader application (https://github.com/TheUnusAnnusArchive/TUAA-Downloader/) doesn't
work most of the times (at least for me) and I'm too lazy to try to fix it so I decided to do
my own version of the downloader in Python 3.

Usage: `$ python tuaa.py <season> <episode|episode range> <quality>`

- `<season>`: Season number. (e.g., `0` or `1`)
- `<episode|episode range>`: Episode number or a range of episode numbers. (e.g., `26` or `50-60`)
- `<quality>`: [Optional argument] Set the quality to download (`2160`, `1440`, `1080`, `720`, `480`, `360`, or `240`) [Default: `1080`]

This python script can be imported to another script so you can use the API.
"""

import os
import sys
import json
import datetime

from typing import Any
from html.parser import HTMLParser

try:
    import requests

except ImportError:  # requests module is required.
    print("[E] You need to install the `requests` library.")
    sys.exit(1)

try:
    from tqdm import tqdm

except ImportError:  # tqdm module is optional.
    print("[i] tqdm module in not installed, falling back to old progress bar.")
    TQDM_INSTALLED = False

else:
    TQDM_INSTALLED = True


class HTMLFilter(HTMLParser):
    """
    Filters out all HTML tags.
    """

    text: str = ''

    def handle_data(self, data: str):
        self.text += data


class API:
    def __init__(self, timeout: int = 60):
        """
        The initialization method of API() class.

        :param timeout: The timeout of the requests module in seconds.
        """

        self._cdn = "https://cdn.unusann.us"  # This is where the video files are stored.
        self._endpoint = "https://api.unusann.us"  # Updated API endpoint.

        self.timeout: int = timeout  # Timeout for requests

    @property
    def _extensions(self) -> dict[str, str]:
        return {
            "video": "mp4",
            "subtitles": "vtt",
            "thumbnail": "jpg",
            "nfo": "nfo"
        }

    @property
    def _video_qualities(self) -> tuple[int, ...]:
        return (2160, 1440, 1080, 720, 480, 360, 240)

    def _download(self, url: str, fname: str, s: int | None = None, e: int | None = None) -> int:
        """
        Download <url> with tqdm progress bar.

        :param url: The URL of the file to be downloaded.
        :param fname: The filename of the output; Where to write the data to
        :param s: Season number
        :param e: Episode number

        :returns: `0` if download is successful.
                  `1` if the download is not completed.
                  `2` if the downloaded file is larger than the expected size.
                  If there is an unknown error, it will return the requests object's status code.
        """

        resp = requests.get(url, stream=True, timeout=self.timeout)
        total = int(resp.headers.get('content-length', 0))
        if s is None or e is None:
            desc = f"Downloading to {fname}..."

        else:
            desc = f"Downloading S{s}E{e}..."

        if resp.status_code != 200:  # Check if response is "OK".
            return resp.status_code

        if TQDM_INSTALLED:  # Use tqdm module if it is installed.
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

        else:  # Fallback to the old method if tqdm is not installed.
            with open(fname, 'wb') as file:
                downloaded_size = 0
                bar_size = 40  # 40 characters
                percentage = 0  # Percent downloaded
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    downloaded_size += size
                    percentage = (downloaded_size / total) * 100
                    bar = ("=" * round(percentage / 100 * bar_size)) + (" " * (bar_size - round(percentage / 100 * bar_size)))
                    sys.stdout.write(f"\r{desc} [{bar}] ({round(percentage, 2)}%)")
                    sys.stdout.flush()

                print('\r')

        if downloaded_size < total:
            return 1  # Success is False; Not successful

        elif downloaded_size > total:
            return 2  # This is suspicious if this happens.

        else:
            return 0  # Successful; downloaded_size == total

    def _check(self, value: int, vtype: str) -> str:
        """
        Check if the value is right, depending on type.

        :param value: The value to check.
        :param vtype: `s` for season numbers or `e` for episode numbers.

        :returns: Processed version of the value.
        """

        if vtype == 's':
            if len(str(value)) < 2:
                value = f"0{value}"  # type: ignore

        elif vtype == 'e':
            while len(str(value)) < 3:
                value = "0" + str(value)  # type: ignore

        return str(value)

    def getMetadata(self, s: int | None = None, e: int | None = None, dl_all: bool = False) -> requests.Response:
        """
        Get episode <e> of season <s> metadata from <self.endpoint>.

        :param s: Season number (Not needed if dl_all is True)
        :param e: Episode number (Not needed if dl_all is True)
        :param dl_all: Download all season and episode metadata

        :returns: requests response object.
        """

        if dl_all:
            r = requests.get(f"{self._endpoint}/v2/metadata/all", timeout=self.timeout)

        else:
            r = requests.get(
                f"{self._endpoint}/v2/metadata/episode/s{self._check(s, 's')}.e{self._check(e, 'e')}",  # type: ignore
                timeout=self.timeout
            )

        return r

    def getThumbnail(self, s: int, e: int) -> bytes:
        """
        Get thumbnail of season <s> episode <e>.

        :param s: Season number.
        :param e: Episode number.

        :returns: thumbnail data in jpg format.
        """

        return requests.get(
            f"{self._cdn}/thumbnails/{self._check(s, 's')}/{self._check(e, 'e')}.{self._extensions['thumbnail']}",
            timeout=self.timeout
        ).content

    def getVideoData(self, season: int, episode: int, filepath: str, quality: int = 1080) -> int:
        """
        Get the actual video data from the CDN.

        :param season: Season number
        :param episode: Episode number
        :param filepath: Where to store the downloaded video.
        :param quality: `1080` for 1080p, (Other options: `2160`, `1440`, `720`, `480`, `360`, `240`)

        :returns: The error code.
        """

        if quality not in self._video_qualities:
            raise ValueError("Invalid quality parameter!")

        # return requests.get(f"{self.cdn}/{season}/{episode}/{quality}.{self.extensions['video']}").content
        return self._download(
            f"{self._cdn}/{self._check(season, 's')}/{self._check(episode, 'e')}/{quality}.{self._extensions['video']}",
            filepath,
            season,
            episode
        )

    def getSubtitle(self, s: int, e: int, language: str | None = None, dl_all: bool = False) -> dict[str, bytes]:
        """
        Get subtitles of season <s> episode <e>.

        :param s: Season number.
        :param e: Episode number.
        :param language: The language to download. (Country code like `en` for English)
        :param dl_all: Download all available subtitles.

        :returns: A dictionary containing the subtitles in <bytes>. Returns an empty dictionary if no subtitles are found.
        """

        if dl_all:
            episode_metadata = self.getMetadata(int(s), int(e))
            result = {}
            for tracks in json.loads(episode_metadata.content)["tracks"]:
                result[tracks["srclang"]] = requests.get(
                    f"{self._cdn}/subs/{self._check(s, 's')}/{self._check(e, 'e')}.{tracks['srclang']}.{self._extensions['subtitles']}",
                    timeout=self.timeout
                ).content

            return result

        else:
            if language is None:
                raise ValueError("You need to set `language` if dl_all is False.")

            r = requests.get(
                f"{self._cdn}/subs/{self._check(s, 's')}/{self._check(e, 'e')}.{language}.{self._extensions['subtitles']}",
                timeout=self.timeout
            )
            if r.status_code == 200:
                return {language: r.content}

            else:
                return {}

    def genNFO(self, s: int, e: int) -> str:
        """
        Generate NFO using self.getMetadata().
        NOTE: This method have hardcoded variables.

        :param s: Season number.
        :param e: Episode number.

        :returns: NFO output.
        """

        meta: dict[str, Any] = json.loads(self.getMetadata(s, e).content)
        title: str = meta.get("title", "Unus Annus")

        # Process the plot.
        plot: str = meta.get("description", "")
        plot_parser = HTMLFilter()
        plot_parser.feed(plot.replace("<br>", '\n'))
        plot = plot_parser.text

        date: str | None = str(meta.get("date", None))
        if date is not None:
            date = "\n  <aired>{0}</aired>".format(
                datetime.datetime.fromtimestamp(
                    int(date[:-3])  # Remove the last three characters from the integer.
                ).strftime("%Y-%m-%d")
            )

        else:
            date = ""

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
  <season>{s}</season>{date}
</episodedetails>"""


class Main():
    def __init__(self, season: int, episode: int, quality: int = 1080):
        self.s = season
        self.e = episode
        self.quality = quality
        self._api = API()
        self.retries = 3  # Maximum retries

    def main(self) -> int:
        s = self._api._check(self.s, 's')
        e = self._api._check(self.e, 'e')
        filename = f"Unus Annus S{self.s}E{self.e}"
        sf = f"Season {s}"  # Season folder
        ef = os.path.join(f"{sf}", f"Unus Annus S{self.s}E{self.e}")  # Episode folder

        if "error" in json.loads(self._api.getMetadata(s, e).content):  # type: ignore
            print("Episode not found!")
            return 1

        print("Creating folder...")
        os.makedirs(ef, exist_ok=True)

        print("Downloading subtitles...")
        subs = self._api.getSubtitle(
            s=self.s,
            e=self.e,
            language=None,
            dl_all=True
        )
        print("Downloading thumbnail...")
        poster = self._api.getThumbnail(
            s=self.s,
            e=self.e
        )

        print("Writing thumbnail to file...")
        with open(os.path.join(ef, f"{filename}-thumb.{self._api._extensions['thumbnail']}"), 'wb') as f:
            f.write(poster)

        for lang in subs:
            print(f"Writing `{lang}` subtitles to file...")
            with open(os.path.join(ef, f"{filename}.{lang}.{self._api._extensions['subtitles']}"), 'wb') as f:
                f.write(subs[lang])

        print("Generating NFO...")
        with open(os.path.join(ef, f"{filename}.{self._api._extensions['nfo']}"), 'wb') as f:
            f.write(self._api.genNFO(self.s, self.e).encode("utf-8"))

        if os.path.isfile(os.path.join(ef, f"{filename}.{self._api._extensions['video']}")):
            print("Skipping video because it already exists.")

        else:
            print("Downloading video... (Might take a long time)")
            video_dl_retries = 0
            while True:
                dlerrcode = self._api.getVideoData(  # Try downloading the file.
                    season=self.s,
                    episode=self.e,
                    filepath=os.path.join(ef, f"{filename}.{self._api._extensions['video']}"),
                    quality=self.quality
                )
                if (dlerrcode != 0) and (video_dl_retries == self.retries):  # If the maximum retries is reached, break.
                    print("Failed to download video and maximum retries reached.")
                    break

                if dlerrcode != 0:  # If the download failed
                    video_dl_retries += 1
                    print(f"Video download of S{s}E{e} failed. [Error {dlerrcode}] Retrying... ({video_dl_retries}/{self.retries})")

                    try:  # Remove the incomplete file.
                        os.remove(os.path.join(ef, f"{filename}.{self._api._extensions['video']}"))

                    except FileNotFoundError:
                        pass

                    continue

                else:  # If the download is successful
                    if video_dl_retries == 1:
                        retry_grammar = "retry"

                    else:
                        retry_grammar = "retries"

                    print(f"Download successful with {video_dl_retries} {retry_grammar}.")
                    break

        print("Done!")
        return 0


if __name__ == "__main__":
    def __dl(s, e, q):
        """
        A private function to be used below.
        """

        print(f"Downloading S{s}E{e}...")
        return Main(
            season=s,
            episode=e,
            quality=q
        ).main()

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
        print('p, '.join(map(str, API()._video_qualities)) + 'p')
        sys.exit(1)

    try:
        q = int(sys.argv[3])

    except IndexError:
        q = 1080  # Default quality

    if type(e) is int:
        sys.exit(__dl(s, e, q))

    else:
        ec = 0  # Error code
        if i == -1:  # type: ignore
            e_range = range(e[0], (e[1] - 1), i)  # type: ignore

        else:
            e_range = range(e[0], (e[1] + 1), i)  # type: ignore

        print(f"Downloading S{s}E{e[0]}-{e[1]}... ({len(e_range)} episodes)")  # type: ignore

        for current_episode in e_range:
            print()
            ec += __dl(s, current_episode, q)
            pass

        sys.exit(ec)
