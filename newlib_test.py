import sounddevice as sd
import pymumble_py3 as pymumble
import wave

import time


def get_channel_data(channel, data):
    return data[:, channel].tobytes()



sampling_frequency = pymumble.constants.PYMUMBLE_SAMPLERATE

snd_data = sd.rec(frames=100000,
                  samplerate=sampling_frequency,
                  # channels=2,
                  dtype='int16',
                  mapping=[1, 2],
                  blocking=True,
                  device="microphone wdm-ks")

print(snd_data[:, 0])
# print(snd_data[:,1].tolist())

# sd.play(snd_data, samplerate=sampling_frequency, blocking=True)

frames = snd_data[:, 0].tobytes()
print(frames)

host = 'mumble.c3lingo.org'
user = 'abot3'


abot = pymumble.Mumble(host, user)

abot.set_application_string("c3lingo (%s)" % 0.1)
abot.set_codec_profile('audio')
abot.start()
abot.is_ready()
abot.set_bandwidth(90000)
abot.sound_output.add_sound(frames)


wf = wave.open("sounddevice_test.wav", 'wb')
wf.setnchannels(1)
wf.setsampwidth(2)
wf.setframerate(sampling_frequency)
wf.writeframes(frames)
wf.close()

time.sleep(5)