
class ConfigurationError(Exception):
    pass

class MumbleMapping(object):

    def __init__(self, audio_channel, mumble_username, mumble_channel, mumble_cert, mumble_key):
        self.mumble_cert = self.check_cert(mumble_cert)
        self.mumble_key = self.check_cert(mumble_key)
        self.mumble_channel = self.check_mumble_channel(mumble_channel)
        self.mumble_username = self.check_mumble_username(mumble_username)
        self.audio_channel = self.check_audio_channel(audio_channel)

    @staticmethod
    def check_cert(mumble_cert):
        if isinstance(mumble_cert, str):
            if os.path.isfile(mumble_cert):
                return mumble_cert
            else:
                raise ConfigurationError("Could not find Mumble Certificate at {}.".format(mumble_cert))
        else:
            raise ConfigurationError("Mumble Certificate is not an instance of str.")

    @staticmethod
    def check_mumble_channel(mumble_channel):
        if isinstance(mumble_channel, str):
            return mumble_channel
        else:
            raise ConfigurationError("Mumble channel is not an instance of str.")

    @staticmethod
    def check_mumble_username(mumble_username):
        if isinstance(mumble_username, str):
            return mumble_username
        else:
            raise ConfigurationError("Mumble User Name is not an instance of str.")

    @staticmethod
    def check_audio_channel(audio_channel):
        try:
            audio_channel_int = int(audio_channel)
            if audio_channel_int > 0:
                return audio_channel_int
            else:
                raise ConfigurationError("Audio Channel is 1-indexed. Zero or negative values are not valid.")
        except ValueError as e:
            raise ConfigurationError("Audio Channel could not be converted to an int.")
