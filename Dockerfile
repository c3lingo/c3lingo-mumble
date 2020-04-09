FROM python:buster

RUN apt-get -y update && \
    apt-get install -y libopus-dev portaudio19-dev pulseaudio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

RUN useradd -ms /bin/bash app
USER app
WORKDIR /home/app
COPY --chown=app c3lingo_mumble ./c3lingo_mumble
COPY --chown=app examples ./examples


ENTRYPOINT ["/usr/local/bin/python"]
