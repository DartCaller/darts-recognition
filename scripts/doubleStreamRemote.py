# https://picamera.readthedocs.io/en/release-1.12/recipes1.html#capturing-to-a-network-stream
# served as a basis for this file
import io
import socket
import struct
from time import sleep
import picamera


server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(10)
connection = server_socket.accept()[0].makefile('wrb')

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (1640, 1232)
        camera.start_preview()
        sleep(2)

        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # Block until ready signal is received
            _ = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]

            image_length = stream.tell()
            stream.seek(0)
            image = stream.read()

            connection.write(struct.pack('<L', image_length))
            connection.flush()
            connection.write(image)

            stream.seek(0)
            stream.truncate()
finally:
    connection.close()
    server_socket.close()
