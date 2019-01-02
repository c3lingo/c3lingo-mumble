#!/bin/bash

# usage: /usr/local/bin/c3lingo-stream.sh multicast_ip channel{0,1} mumble_channelname mumble_username

cd "$HOME/c3lingo-mumble"

MULTICAST_ADDRESS="$1"
VENV="$HOME/venv"
CERTS="$HOME/certs"
CHANNEL="$2"
export HOST=localhost 
export PORT=64738 
export MUMBLE_CHANNEL="$3" 
export MUMBLE_USER="$4" 
export MUMBLE_CERT="$CERTS/$4.cert.pem" 
export MUMBLE_KEY="$CERTS/$4.key.pem" 

#gst-launch-1.0 -q udpsrc address= port=5004 multicast-iface=ens7 ! application/x-rtp,clock-rate=48000,format=S16LE,channels=2 ! rtpL24depay ! audioconvert ! deinterleave name=d d.src0 ! fdsink |\

#gst-launch-1.0 -q audiotestsrc ! audio/x-raw,rate=48000,channels=2 ! audioconvert ! audioresample ! audio/x-raw, format=S16LE, rate=48000 ! deinterleave name=d d.src_0 ! fdsink |\

AES_SOURCE="udpsrc address=${MULTICAST_ADDRESS} port=5004 multicast-iface=ens7 ! application/x-rtp,clock-rate=48000,channels=2 ! rtpL24depay"
AUDIO_FORMAT="audioconvert ! audioresample ! audio/x-raw, format=S16LE, rate=48000"
CHANNEL_SELECT="deinterleave name=d d.src_${CHANNEL}"

gst-launch-1.0 -q $AES_SOURCE ! $AUDIO_FORMAT ! $CHANNEL_SELECT ! fdsink |\
"$VENV/bin/python" -m c3lingo_mumble.single_wrapper
