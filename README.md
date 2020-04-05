# Feed talk audio streams to the c3lingo mumble server for 36c3

The setup this year is different from previous occasions. This README describes
the setup specifically for 36c3; this branch has only the files that are
required for this setup. The master branch has all python modules.

## Installation

The Python code requires Python 3.7 or newer, and `pipenv` or `venv` and pip`.

Debian:
```
sudo apt install -y git python3-dev python3-venv python3-wheel
```

Mac:
```sh
brew install opus python
```

Then create a virtual environment for the project.

With `venv` and `pipenv`:
```
$ pipenv install
```

With `pip`
```
$ python3 -m venv .venv
$ .venv/bin/pip install -r requirements.txt
```

## Setup

Audio is taken directly from the Voctomix setup (on the Voctomix host).

We connect to Voctomix to receive a stream consisting of a Matroska container
with both video and audio, and use ffmpeg to extract the audio channels.

```
$ ffprobe tcp://localhost:15000
ffprobe version 4.1.4-1~deb10u1 Copyright (c) 2007-2019 the FFmpeg developers
   ...
Input #0, matroska,webm, from 'tcp://localhost:15000':
 Metadata:
   encoder         : GStreamer matroskamux version 1.14.4
   creation_time   : 2019-12-11T17:06:50.000000Z
 Duration: N/A, start: 49.920000, bitrate: 6144 kb/s
   Stream #0:0(eng): Video: ...
   Metadata:
     title           : Video
   Stream #0:1(eng): Audio: pcm_s16le, 48000 Hz, 8 channels, s16, 6144 kb/s (default)
   Metadata:
     title           : Audio

```

There are four stereo audio channels interleaved into a single stream. We use
ffmpeg to extract and downmix the audio to three mono channels: for the original
sound from the speaker, one for the first translation channel, and one for
the second one. The fourth source channel is ignored.

We then feed this into the Python code that sends each channel to the configured
Mumble channel, using a unique user for that channel.

The pipeline looks like this:
```
ffmpeg -loglevel error -i tcp://localhost:15000 \
    -filter_complex '[0:a]pan=3c|c0=.5*c0+.5*c1|c1=.5*c2+.5*c3|c2=.5*c4+.5*c5[a0]' \
    -map '[a0]' -ac 3 -f s16le -c:a pcm_s16le -y - \
| pipenv run python -m c3lingo_mumble.send_stdin -f c3lingo-adams.yaml
```

A sample config file for the Python code can be found in
[examples/send_stdin/adams.yaml](examples/send_stdin/adams.yaml).

A sample systemd unit file can be found under
[examples/send_stdin/mumblesender.service](examples/send_stdin/mumblesender.service)