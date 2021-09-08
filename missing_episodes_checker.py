"""
missing_episodes_checker.py

For checking which episodes are not yet downloaded.

**USAGE**:

1. Edit `rootdir` variable.
2. Run the script. (Add `-i` or `--invert` as an argument to show only the downloaded videos)
"""

import os
import sys

# Change this to the root directory where your season folders are stored.
# Use forward slashes (/) or the program might break because I'm too lazy
# to do security checks. Also add a trailing slash.
rootdir = "E:/HomeTheater/YouTube Series/Unus Annus (2019)/"

try:
    if sys.argv[1] in ("-i", "--invert"):
        invert = True

    else:
        invert = False

except IndexError:
    invert = False

episodes = {
    0: os.listdir(f"{rootdir}Season 00"),
    1: os.listdir(f"{rootdir}Season 01")
}

missing = []

# Check Season 00

i = 1
while i != 12:
    filepath = f"{rootdir}Season 00/Unus Annus S0E{i}"
    if invert:
        if os.path.exists(filepath):
            missing.append(filepath)

    else:
        if not os.path.exists(filepath):
            missing.append(filepath)

    i += 1

# Check Season 01

i = 1
while i != 368:
    filepath = f"{rootdir}Season 01/Unus Annus S1E{i}"
    if invert:
        if os.path.exists(filepath):
            missing.append(filepath)

    else:
        if not os.path.exists(filepath):
            missing.append(filepath)

    i += 1

if invert:
    print("Available episodes:")

else:
    print("Missing episodes:")

print()
for filepath in missing:

    print(f"    + {filepath}")

print()
