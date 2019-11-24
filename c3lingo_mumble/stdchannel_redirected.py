"""
Temporarily redirect stdout, stderr or stdin to some other file.

http://marc-abramowitz.com/archives/2013/07/19/python-context-manager-for-redirected-stdout-and-stderr/

    e.g.:

    with stdchannel_redirected(sys.stderr, os.devnull):
        ...
"""
import contextlib
import os


@contextlib.contextmanager
def stdchannel_redirected(stdchannel, dest_filename):
    oldstdchannel = None
    dest_file = None
    try:
        oldstdchannel = os.dup(stdchannel.fileno())
        dest_file = open(dest_filename, 'w')
        os.dup2(dest_file.fileno(), stdchannel.fileno())

        yield
    finally:
        if oldstdchannel is not None:
            os.dup2(oldstdchannel, stdchannel.fileno())
        if dest_file is not None:
            dest_file.close()
