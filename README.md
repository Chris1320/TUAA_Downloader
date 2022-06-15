# The Unus Annus Archive Downloader (TUAA Downloader)

A python script I made for downloading videos from [the Unus Annus Archive](https://unusann.us/). This script is tested on *Windows 10/11*, Termux (Android), and *Kali Linux*.

Their [Downloader application](https://github.com/TheUnusAnnusArchive/TUAA-Downloader/) doesn't work most of the times (at least for me) and I'm too lazy to try to fix it so I decided to do my own version of the downloader in Python 3.

Usage: `$ python tuaa.py <season> <episode|episode range> <quality>`

- `<season>`: Season number.
- `<episode|episode range>`: Episode number or a range of episode numbers.
- `<quality>`: \[Optional argument\] Set the quality to download (`2160`, `1440`, `1080`, `720`, `480`, `360`, or `240`) \[Default: `1080`\]

This python script can be imported to another script so you can use the API.

## Example API Usage

```python

import json
from tuaa import API

tuaa_api = API()

season = 1
episode = 4
quality = 1080  # Download in 1080p

metadata = tuaa_api.getMetadata(season, episode)  # Get the metadata of season 1's 4th episode.

metadata = json.loads(metadata.content)  # Convert JSON to Python dictionary.

# Do something with the metadata
print(f"Downloading {metadata['title']}...")
tuaa_api.getVideoData(season, episode, "video.mp4", quality)  # Save file to `video.mp4`
```

The API can download the videos, metadata, thumbnails/posters, and subtitles.

If you just want to automate the download of multiple episodes,
import the Main class instead.

```python

from tuaa import Main

episodes_to_download = {
    0: (2, 4, 6, 8),  # Download episodes 2, 4, 6, and 8 of season 0. (Specials)
    1: (10, 12, 14, 17)  # Download episodes 10, 12, 14, and 17 of season 1.
}

quality = 1080  # Download videos in 1080p quality.

for season in episodes_to_download:
    for episode in episodes_to_download[season]:
        Main(season, episode).main()
```

## missing_episodes_checker.py

For checking which episodes are not yet downloaded.

**USAGE**:

1. Run the script. (Add `-i` or `--invert` as an argument to show only the downloaded videos)
