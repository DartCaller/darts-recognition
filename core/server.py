# https://picamera.readthedocs.io/en/release-1.12/recipes1.html#capturing-to-a-network-stream
# served as a basis for this file
import io
import socket
import struct
from helper_functions import save_image
import cv2
import numpy as np
import main


def convert_jpeg_bytes_into_numpy_rgb(jpeg_bytes):
    return cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), -1).copy()


main.setup()
# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
print('Listening for Ws Connection')

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

try:
    while True:
        # Read the lengths of the images as a 32-bit unsigned int
        image_lengths = list(map(
            lambda _: struct.unpack('<L', connection.read(struct.calcsize('<L')))[0],
            range(2)
        ))
        if not any(image_lengths):
            print('Received Close signal')
            break
        print(image_lengths)
        # Construct streams to hold the image data and read the images
        # data from the connection
        image_streams = list(map(lambda _: io.BytesIO(), range(2)))
        images = []
        for image_byte_size, axis in zip(image_lengths, ['x', 'y']):
            image_bytes = connection.read(image_byte_size)
            save_image(axis, image_bytes)
            images.append(convert_jpeg_bytes_into_numpy_rgb(image_bytes))

        main.on_incoming_images(images[0], images[1])

finally:
    connection.close()
    server_socket.close()
