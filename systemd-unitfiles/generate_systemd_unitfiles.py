#!/usr/bin/env python3
import os
filename_template = "c3lingo-stream-{stream_name}.service"
file_template = """
[Unit]
Description=c3lingo-mumble streams one channel from an AES67 source to a specific channel on a mumble server.

[Service]
ExecStart={exec_command}
User={user}
Group={group}

[Install]
WantedBy=multi-user.target
"""

input_file = 'all_stream_processes.txt'
output_folder = 'unitfiles'
unix_user = 'hellerbarde'
unix_group = 'hellerbarde'

os.makedirs(output_folder, exist_ok=True)

with open(input_file, 'r') as input_fd:
    for line in input_fd.readlines():
        room_number, process_string = line.split(":") 
        out_filename = os.path.join(output_folder, filename_template.format(stream_name=room_number))

        with open(out_filename, 'w') as output_fd:
            output_fd.write(file_template.format(exec_command=process_string,
                                                 user=unix_user,
                                                 group=unix_group))

        
