import socketio
from picamera import PiCamera
import datetime
from time import sleep
import io
import os
import subprocess


debug = False
camera = PiCamera()
camera.resolution = (1640, 1232)  # (3280, 2464)
camera.framerate = 15
camera.rotation = 180
camera.start_preview(alpha=192)
ssh = 'raspberrypi.local'
remote_dir = '/home/pi/Desktop'


sio = socketio.Client(logger=debug, engineio_logger=debug)


def get_remote_camera_daemon_id():
    pid = execute_command(via_ssh('pgrep raspistill', ssh)).read().rstrip()
    if (pid != ""):
        print(f'Found already running camera daemon with pid {pid}')
        return pid
    else:
        process = execute_command(via_ssh('cd /home/pi/Desktop/ && ./camera.sh', ssh))
        sleep(3)
        pid = execute_command(via_ssh('pgrep raspistill', ssh)).read().rstrip()
        print(f'Started Camera Daemon with pid {pid}')
        return pid


def via_ssh(command, ssh_ip):
    return f'ssh {ssh_ip} "{command}"'


def execute_command(cmd):
    return os.popen(cmd)


@sio.event
def connect():
    print(f'connected at {datetime.datetime.now()}')
    main()


@sio.event
def connect_error():
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


sio.connect('ws://192.168.0.127:8000')


def main():
    pid = get_remote_camera_daemon_id()
    image_stream = io.BytesIO()
    try:
        while True:
            # Take image locally
            camera.capture(image_stream, 'jpeg')
            local_image_data = image_stream.getvalue()
            # Take image remotely
            execute_command(via_ssh(f'kill -USR1 {pid}', ssh))
            sleep(1)
            subprocess.call(f'ssh {ssh} "cat {remote_dir}/dart.jpg" > dart.jpg', shell=True)
            f = open('dart.jpg', 'rb')
            remote_image_data = f.read()
            f.close()
            # Emit Event
            data = local_image_data + remote_image_data
            cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            split_pos = len(local_image_data)
            sio.emit('image', {'split_pos': split_pos, 'time': cur_time, 'stream': data})
            sleep(5)
    finally:
        image_stream.close()
        camera.stop_preview()
