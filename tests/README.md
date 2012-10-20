# Requirements

 * transmission-cli
 * mp3gain
 * ffmpeg
 * steghide
 * normalize-audio
 * python-eyed3
 * python-mutagen

 * libavcodec-extra-53 (at least on Ubuntu 12.10)

# First run

the first time you run the hook tests you have to initialize the test environment

    python tests/runtests.py --gpo=xxx --extension=xxx --init

Please provide your path the the `gpodder checkout path`and your `extension script source path`.

The script create a sub directory with the test database and the test files


# Run your tests

from now on you can start the tests with (without the --init parameter)

    python tests/runtests.py --gpo=xxx --extension=xxx


