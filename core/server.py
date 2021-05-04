# https://picamera.readthedocs.io/en/release-1.12/recipes1.html#capturing-to-a-network-stream
# served as a basis for this file
import sys
import socket
import struct
from helper_functions import save_image
import cv2
import numpy as np
import main
from pathlib import Path
from threading import Thread
from collections import deque
from time import sleep


main.setup()
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(10)
received_image_queue = deque()
print('Listening for Ws Connection')

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')


def convert_jpeg_bytes_into_numpy_rgb(jpeg_bytes):
    return cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), -1).copy()


def label_image(images_in_bytes):
    label = input('Label for the current Image Pair:')
    folder = Path(f'./labeled_images/{label}')
    folder.mkdir(parents=True, exist_ok=True)
    count_of_same_label = round(len(list(folder.glob('*.jpg'))) / 2)
    for i, axs in enumerate(['x', 'y']):
        with open(f'{str(folder)}/{axs}_{count_of_same_label}.jpg', 'wb') as file:
            file.write(images_in_bytes[i])


def read_images_from_ws(image_queue):
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
            # Construct streams to hold the image data and read the images
            # data from the connection
            images_bytes = list(map(
                lambda image_length: connection.read(image_length),
                image_lengths
            ))

            image_queue.append(images_bytes)

    finally:
        connection.close()
        server_socket.close()


Thread(target=read_images_from_ws, args=(received_image_queue,)).start()

while True:
    try:
        img_bytes_list = received_image_queue.popleft()
        if len(sys.argv) > 1 and sys.argv[1] == '--label-mode':
            label_image(img_bytes_list)
            input('Enter to continue:')
            sleep(3)
            received_image_queue.clear()
        else:
            for img_bytes, axis in zip(img_bytes_list, ['x', 'y']):
                save_image(axis, img_bytes)

            imgs = list(map(lambda image_bytes: convert_jpeg_bytes_into_numpy_rgb(image_bytes), img_bytes_list))
            Thread(target=main.on_incoming_imgs, args=(imgs[0], imgs[1])).start()
    except IndexError:
        sleep(0.5)
    except OSError:
        pass
