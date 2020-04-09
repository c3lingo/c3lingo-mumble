![Docker Image CI](https://github.com/c3lingo/c3lingo-mumble/workflows/Docker%20Image%20CI/badge.svg)

# Mumble Audio Utilities

This project contains Python modules that are used in conjuction with a Mumble server to insert and extract audio into/from Mumble channels.

## Installation

The Python code requires Python 3.7 or newer, and `pipenv` or `venv` and pip`.

### Docker

A docker image is available at https://hub.docker.com/r/c3lingo/c3lingo-mumble. Use the docker image like you would use the Python command:

```
docker run --rm -it -v $PWD/c3lingo-mumbleweb:/c3lingo-mumbleweb c3lingo/c3lingo-mumble:latest -m c3lingo_mumble.play_wav -c /c3lingo-mumbleweb/test-channel.yaml
```

### Local Installation

Install the prerequisite packages, then set up a local environment.

#### Debian
```
sudo apt install -y git python3-dev python3-venv python3-wheel libopus-dev portaudio19-dev pulseaudio
```

#### Mac
```sh
brew install opus python portaudio
```

#### Local Environment with Pipenv

With `pipenv`:
```
$ pipenv install
```

#### Local Environment with Pip

With `venv` and `pip`
```
$ python3 -m venv .venv
$ .venv/bin/pip install -r requirements.txt
```

## Using c3lingo-mumble

### Playing a WAV file to a Mumble channel with `play_wav`

This module connects to a channel and plays the wav file. The file can be played in a loop.

```
python -m c3lingo_mumble.play_wav -c examples/play_wav/test-channel.yaml
```

The config file contains all necessary information. See [examples/play_wav/test-channel.yaml](./examples/play_wav/test-channel.yaml) for an example.


### Receive audio from a channel with `recv_stdout` and send it to stdout

This module connects to a channel and produces any audio received on standard out, as raw little endian 16 bit PCM 48000 samples/sec.

```
python -m c3lingo_mumble.recv_stdout mumble.c3lingo.org test
```

The optional third argument specifies a file to record to. Recording stops when the Python program is stopped (^C or kill).


### Receive audio from a channel with `recv_pyaudio` and send it to an output

This module connects to a channel and send the sound to a [PortAudio](http://www.portaudio.com) device.

```
python -m c3lingo_mumble.recv_stdout mumble.c3lingo.org test headphones
```

The third argument specifies the device to play the audio on. To get a list of devices, run
```
python -m c3lingo_mumble.audio
```
Then use the index or the name of the device.

### Additional Modules

There are more useful modules. See the source code and the (examples/)[examples/] directory for more information.

## Building

### Updating `requirements.txt`

```
pipenv run pip freeze > requirements.txt
```

## Setup at 36c3

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