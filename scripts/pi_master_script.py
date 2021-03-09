# https://picamera.readthedocs.io/en/release-1.12/recipes1.html#capturing-to-a-network-stream
# served as a basis for this file
import io
import os
import socket
import struct
from time import sleep
import subprocess
import picamera


client_socket = socket.socket()
client_socket.connect(('192.168.0.127', 8000))
ssh = 'raspberrypi.local'
remote_dir = '/home/pi/Desktop'
# Make a file-like object out of the connection
connection = client_socket.makefile('wb')


def get_remote_camera_daemon_process():
    process_id = execute_command(via_ssh('pgrep raspistill', ssh)).read().rstrip()
    if process_id != "":
        print(f'Found already running camera daemon with pid {process_id}')
        return process_id, None
    else:
        daemon_process = execute_command(via_ssh('cd /home/pi/Desktop/ && ./camera.sh', ssh))
        sleep(3)
        process_id = execute_command(via_ssh('pgrep raspistill', ssh)).read().rstrip()
        print(f'Started Camera Daemon with pid {pid}')
        return process_id, daemon_process


def via_ssh(command, ssh_ip):
    return f'ssh {ssh_ip} "{command}"'


def execute_command(cmd):
    return os.popen(cmd)


def capture_on_remote():
    execute_command(via_ssh(f'kill -USR1 {pid}', ssh))
    sleep(1)
    subprocess.call(f'ssh {ssh} "cat {remote_dir}/dart.jpg" > dart.jpg', shell=True)
    f = open('dart.jpg', 'rb')
    remote_image_data = f.read()
    f.close()
    return remote_image_data


try:
    pid, process = get_remote_camera_daemon_process()
    with picamera.PiCamera() as camera:
        camera.resolution = (1640, 1232)
        camera.rotation = 180
        camera.start_preview()
        sleep(2)

        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            image_from_remote = capture_on_remote()
            # Write the length of both captures to the stream and flush to sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.write(struct.pack('<L', len(image_from_remote)))
            connection.flush()
            # Rewind the local stream and send both images
            stream.seek(0)
            connection.write(stream.read())
            connection.write(image_from_remote)
            # Reset the local stream for the next local capture
            stream.seek(0)
            stream.truncate()
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
    if process:
        process.close()
