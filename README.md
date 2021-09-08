# TUAA_Downloader

A python script I made for downloading videos from [the Unus Annus Archive](https://unusannusarchive.tk/).

## TUAA_downloader.py

The (maybe) stable version of TUAA downloader. (Tested on *Windows 10* and *Kali Linux*, working fine)

Their [Downloader application](https://github.com/TheUnusAnnusArchive/TUAA-Downloader/) doesn't work most of the times (at least for me) and I'm too lazy to try to fix it so I decided to do it in Python.

Usage: `$ python TUAA_downloader.py <season> <episode> <quality>`

- `<season>`: Season number.
- `<episode>`: Episode number.
- `<quality>`: \[Optional argument\] Set the quality to download (`2160`, `1440`, `1080`, `720`, `480`, `360`, or `240`)

This python script can be imported to another script so you can use the API.

Example API Usage:

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

## TUAA.py (Not Recommended)

This is the first script I created to move files downloaded by
TUAA's downloader application.

**USAGE**:

1. [Download](https://github.com/TheUnusAnnusArchive/TUAA-Downloader/releases/latest) The Unus Annus Downloader.
2. Download the files you need.
3. Edit variables of `TUAA.py` and run it.

**NOTE**: I do not recommend doing this because it's too hacky. Use `TUAA_downloader.py` instead.

## missing_episodes_checker.py

For checking which episodes are not yet downloaded.

**USAGE**:

1. Edit `rootdir` variable.
2. Run the script. (Add `-i` or `--invert` as an argument to show only the downloaded videos)
