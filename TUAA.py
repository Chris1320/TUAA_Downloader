"""
TUAA.py

This is the first script I created to move files downloaded by
TUAA's downloader application.

**USAGE**:

1. [Download](https://github.com/TheUnusAnnusArchive/TUAA-Downloader/releases/latest) The Unus Annus Downloader.
2. Download the files you need.
3. Edit variables of `TUAA.py` and run it.

"""

import os
import sys
import json

title = "Unus Annus"
tempdir = r"E:\Temp"
htdir = r"E:\HomeTheater\YouTube Series\Unus Annus (2019)"

for files in os.listdir("Videos/Season 1"):  # ! Season is hardcoded
    if "S00" in files:
        # Season 00
        season = 0
        filename = files[::-1].partition('.')[2].partition(os.sep)[0][::-1]
        episode = int(files.partition("S00E")[2].partition('.')[0])  # ! Season is hardcoded
        extension = files[::-1].partition('.')[0][::-1]
        metadata = {
            "season": season,
            "episode": episode,
            "title": None,
            "description": None,
            "date": None,
            "duration": None
        }
        with open("Metadata/Specials/{0}.json".format(filename), 'rb') as f:
            file_meta = json.loads(f.read())

        metadata["title"] = file_meta["title"]
        metadata["description"] = file_meta["description"]
        metadata["date"] = file_meta["date"]
        metadata["duration"] = file_meta["duration"]
        duration_in_hours = round((metadata["duration"] / 60) / 60)

        print()
        print(f"{filename} ({extension})")
        print(f"Season {season} Episode {episode}")
        print()
        print('=' * 25)

        new_path = os.path.join(htdir, "Season 00", "{0} S{1}E{2}".format(title, season, episode))  # ! Season is hardcoded
        if extension in ("mp4", "mkv"):
            filename = os.path.join("Videos/Specials", files)
            new_filename = os.path.join(new_path, "{0} S{1}E{2}.{3}".format(title, season, episode, extension))

        subtitle_path = os.path.join("Subtitles", "Specials", "{0}.vtt".format(filename))  # ! Season is hardcoded
        new_subtitle_path = os.path.join(new_path, "{0} S{1}E{2}.eng.{3}".format(title, season, episode, "vtt"))

        thumbnail_path = os.path.join("Thumbnails", "Specials", "{0}.jpg".format(filename))  # ! Season is hardcoded
        new_thumbnail_path = os.path.join(new_path, "metadata", "{0} S{1}E{2}.{3}".format(title, season, episode, "jpg"))

        # Create folders
        os.makedirs(os.path.join(new_path, "metadata"), exist_ok=True)  # Create folders

        # Move video, subtitle, and thumbnail files, and create NFO file.
        os.rename(filename, new_filename)
        os.rename(subtitle_path, new_subtitle_path)
        os.rename(thumbnail_path, new_thumbnail_path)
        with open(os.path.join(new_path, "{0} S{1}E{2}.{3}".format(title, season, episode, "nfo")), 'w') as f:
            f.write(f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<episodedetails>
  <plot>{metadata["description"]}</plot>
  <outline />
  <lockdata>true</lockdata>
  <title>{metadata["title"]}</title>
  <imdbid>tt11289784</imdbid>
  <runtime>{duration_in_hours}</runtime>
  <art>
    <poster>{new_thumbnail_path}</poster>
  </art>
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
  <episode>{episode}</episode>
  <season>{season}</season>
</episodedetails>""")

    elif "S01" in files:
        # Season 01
        season = 1
        filename = files[::-1].partition('.')[2].partition(os.sep)[0][::-1]
        episode = int(files.partition("S01E")[2].partition('.')[0])  # ! Season is hardcoded
        extension = files[::-1].partition('.')[0][::-1]
        metadata = {
            "season": season,
            "episode": episode,
            "title": None,
            "description": None,
            "date": None,
            "duration": None
        }
        with open("Metadata/Season 1/{0}.json".format(filename), 'rb') as f:
            file_meta = json.loads(f.read())

        metadata["title"] = file_meta["title"]
        metadata["description"] = file_meta["description"]
        metadata["date"] = file_meta["date"]
        metadata["duration"] = file_meta["duration"]
        duration_in_hours = round((metadata["duration"] / 60) / 60)

        print()
        print(f"{filename} ({extension})")
        print(f"Season {season} Episode {episode}")
        print()
        print('=' * 25)

        new_path = os.path.join(htdir, "Season 01", "{0} S{1}E{2}".format(title, season, episode))  # ! Season is hardcoded
        if extension in ("mp4", "mkv"):
            old_filename = os.path.join("Videos/Season 1", files)
            new_filename = os.path.join(new_path, "{0} S{1}E{2}.{3}".format(title, season, episode, extension))

        subtitle_path = os.path.join("Subtitles", "Season 1", "{0}.vtt".format(filename))  # ! Season is hardcoded
        new_subtitle_path = os.path.join(new_path, "{0} S{1}E{2}.eng.{3}".format(title, season, episode, "vtt"))

        thumbnail_path = os.path.join("Thumbnails", "Season 1", "{0}.jpg".format(filename))  # ! Season is hardcoded
        new_thumbnail_path = os.path.join(new_path, "metadata", "{0} S{1}E{2}.{3}".format(title, season, episode, "jpg"))

        # Create folders
        os.makedirs(os.path.join(new_path, "metadata"), exist_ok=True)  # Create folders

        # Move video, subtitle, and thumbnail files, and create NFO file.
        os.rename(old_filename, new_filename)
        try:
            os.rename(subtitle_path, new_subtitle_path)

        except FileNotFoundError:
            pass

        os.rename(thumbnail_path, new_thumbnail_path)
        with open(os.path.join(new_path, "{0} S{1}E{2}.{3}".format(title, season, episode, "nfo")), 'wb') as f:
            f.write(f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<episodedetails>
  <plot>{metadata["description"]}</plot>
  <outline />
  <lockdata>true</lockdata>
  <title>{metadata["title"]}</title>
  <imdbid>tt11289784</imdbid>
  <runtime>{duration_in_hours}</runtime>
  <art>
    <poster>{new_thumbnail_path}</poster>
  </art>
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
  <episode>{episode}</episode>
  <season>{season}</season>
</episodedetails>""".encode("utf-8"))
