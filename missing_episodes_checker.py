"""
missing_episodes_checker.py

For checking which episodes are not yet downloaded.

**USAGE**:

1. Run the script. (Add `-i` or `--invert` as an argument to show only the downloaded videos)
"""

import os
import sys

rootdir = os.getcwd()  # Assume that the files are in the current working directory.

try:  # Check if `--invert` exists in `sys.argv`.
    invert = True if sys.argv[1] in ("-i", "--invert") else False

except IndexError:
    invert = False

ep_folder_name = "Unus Annus S{s}E{e}"

episodes = {
    0: 14,  # Season 0 (Specials) have 14 episodes.
    1: 368  # Season 1 have 368 episodes.
}


def _episodeCheck(value: int) -> str:
    """
    Convert int<value> to str<value> and make its length == 3.

    :param value: (episode) value.

    :returns: The formatted value.
    """

    while len(str(value)) < 3:
        value = "0" + str(value)  # type: ignore

    return str(value)


def _buildFilepath(season: int, episode: int) -> str:
    """
    Build the expected filepath for the episode.

    :param season: Season number.
    :param episode: Episode number.

    :returns: The filepath.
    """

    return os.path.join(  # Build filepath
        rootdir,
        f"Season 0{season}",  # NOTE: Season number length is hardcoded. (There's only two seasons anyway.)
        str(ep_folder_name.format(s=season, e=episode))
    )


def main() -> int:
    files = []
    if invert:  # Invert result if `--invert` is activated.
        for season in episodes:
            for episode in range(1, episodes[season] + 1):
                episode_folder = _buildFilepath(season, episode)
                if os.path.isdir(episode_folder):
                    # Add to `files` if the folder exists.
                    files.append((season, episode, episode_folder))

    else:  # Do this if `--invert` is not activated.
        for season in episodes:
            for episode in range(1, episodes[season] + 1):
                episode_folder = _buildFilepath(season, episode)
                if not os.path.isdir(episode_folder):
                    # Add to `files` if the folder does not exist.
                    files.append((season, episode, episode_folder))

    if invert:
        print("Available episodes:")

    else:
        print("Missing episodes:")

    print()
    print("Season | Episode | Filepath")
    for f in files:
        print(f"0{f[0]}     | {_episodeCheck(f[1])}     | {f[2]}")

    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
