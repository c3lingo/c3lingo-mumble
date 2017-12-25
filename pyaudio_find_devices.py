"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import pyaudio

p = pyaudio.PyAudio()

device_count = p.get_device_count()
print(device_count)
for i in range(device_count):
    print(p.get_device_info_by_index(i))

