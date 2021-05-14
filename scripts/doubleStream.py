import io
import socket
import struct
from time import sleep
import picamera
from typing_extensions import Literal
import subprocess

PI_ADDR = 'raspberrypi.local'


def start_remote_socket():
    p = subprocess.Popen(
        f'ssh {PI_ADDR} "cd Desktop && python doubleStreamRemote.py"',
        shell=True, stdout=subprocess.PIPE,
    )
    sleep(2)
    return p


def create_socket_connection(address, mode: Literal['wrb', 'wb']):
    new_socket = socket.socket()
    new_socket.connect((address, 8000))
    return new_socket, new_socket.makefile(mode)


def read_local_image(image_stream):
    image_length = image_stream.tell()
    image_stream.seek(0)
    return image_stream.read(), image_length


def read_remote_image(image_stream):
    remote_image_length = struct.unpack('<L', image_stream.read(struct.calcsize('<L')))[0]
    return pi_connection.read(remote_image_length), remote_image_length


def image_lengths_to_stream(output_stream, image_lengths):
    for image_length in image_lengths:
        output_stream.write(struct.pack('<L', image_length))


def write_data_to_stream(output_stream, data):
    for obj in data:
        output_stream.write(obj)
        print('4')


def try_fnc(fnc):
    try:
        fnc()
    except NameError:
        pass


try:
    remote_socket_process = start_remote_socket()
    pi_socket, pi_connection = create_socket_connection('raspberrypi.local', 'wrb')
    backend_socket, backend_connection = create_socket_connection('192.168.0.127', 'wb')

    with picamera.PiCamera() as camera:
        camera.resolution = (1640, 1232)
        camera.start_preview()
        sleep(2)
        local_img_stream = io.BytesIO()

        for foo in camera.capture_continuous(local_img_stream, 'jpeg'):
            # Sending next image signal to slave pi
            pi_connection.write(struct.pack('<L', 0))
            pi_connection.flush()

            local_img, local_img_len = read_local_image(local_img_stream)
            remote_img, remote_img_len = read_remote_image(pi_connection)

            image_lengths_to_stream(backend_connection, [local_img_len, remote_img_len])
            backend_connection.flush()

            write_data_to_stream(backend_connection, [local_img, remote_img])
            local_img_stream.seek(0)
            local_img_stream.truncate()
finally:
    try_fnc(lambda: pi_connection.close())
    try_fnc(lambda: backend_connection.close())
    try_fnc(lambda: pi_socket.close())
    try_fnc(lambda: backend_socket.close())
    try_fnc(lambda: remote_socket_process.kill())
    try_fnc(lambda: remote_socket_process.communicate())
