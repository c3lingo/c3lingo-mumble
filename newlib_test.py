import sounddevice as sd
import pymumble_py3 as pymumble
import wave


def get_channel_data(channel, data):
    return data[:, channel].tobytes()



sampling_frequency = pymumble.constants.PYMUMBLE_SAMPLERATE

snd_data = sd.rec(frames=100000,
                  samplerate=sampling_frequency,
                  # channels=2,
                  dtype='int16',
                  mapping=[1, 2],
                  blocking=True,
                  device="stereo mix wdm-ks")

print(snd_data[:, 0])
# print(snd_data[:,1].tolist())

sd.play(snd_data, samplerate=sampling_frequency, blocking=True)

frames = snd_data[:, 0].tobytes()
print(frames)




wf = wave.open("sounddevice_test.wav", 'wb')
wf.setnchannels(1)
wf.setsampwidth(2)
wf.setframerate(sampling_frequency)
wf.writeframes(frames)
wf.close()
