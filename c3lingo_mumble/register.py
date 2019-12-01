#!/usr/bin/env python3

"""
Connect to server and register username and certificate.
"""
import sys
import time

from c3lingo_mumble.config import Config
import pymumble_py3


def register(server_args, user, certfile, keyfile):
    mumble = pymumble_py3.Mumble(**server_args)
    mumble.start()
    mumble.is_ready()

    if not mumble.is_alive():
        raise Exception(f'Connection to "{server_args["host"]}" failed')

    server_args['certfile'] = certfile
    server_args['keyfile'] = keyfile
    server_args['user'] = user
    admin = pymumble_py3.Mumble(**server_args)
    admin.start()
    admin.is_ready()
    if not admin.is_alive():
        raise Exception(f'Connection to "{server_args["host"]}" as "{user}" failed')

    admin.users[mumble.users.myself_session].register()
    time.sleep(1)

    print(f'User {mumble.user} registered')

if __name__ == "__main__":
    config = Config(description='Send a WAV file to a Mumble server',
                    defaults={
                        'mumble-server': {
                            # see pymumble_py3.mumbly.Mumble.__init__
                            'host': None,
                            'port': 64738,
                            'user': None,
                            'password': '',
                            'certfile': None,
                            'keyfile': None,
                            'reconnect': False,
                            'tokens': [],
                            'debug': False,
                        },
                        'admin': None,
                        'admin_certfile': None,
                        'admin_keyfile': None,
                    })
    c = config.get_config()
    for k in ('admin', 'admin_certfile', 'admin_keyfile'):
        if k not in c or not c[k]:
            print('Missing required parameter --{}'.format(k))
            sys.exit(64)
    for k in ('host', 'user'):
        if k not in c['mumble-server'] or not c['mumble-server'][k]:
            print('Missing required parameter --{}'.format(k))
            sys.exit(64)
    print(f'Registering user \"{c["mumble-server"]["user"]}\" with cert \"{c["mumble-server"]["certfile"]}\"')
    try:
        register(c['mumble-server'], c['admin'], c['admin_certfile'], c['admin_keyfile'])
    except Exception as e:
        print(f'Unable to register user: {e.__class__.__name__}: {e}', file=sys.stderr)
