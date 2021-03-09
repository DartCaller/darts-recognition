import socketio
import eventlet
import socket
from helper_functions import save_image
from datetime import datetime
import main
import cv2
import numpy as np
from PIL import Image
import io


local_ip = socket.gethostbyname(socket.gethostname())
debug = False
sio = socketio.Server(logger=debug, engineio_logger=debug)
app = socketio.WSGIApp(sio)


def convert_jpeg_bytes_into_numpy_rgb(jpeg_bytes):
    return cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), -1).copy()
    # return np.array(Image.open(io.BytesIO(jpeg_bytes)))


def print_time_of_flight(send_timestamp):
    cur_time = datetime.now()
    create_time = datetime.strptime(send_timestamp, '%Y-%m-%d %H:%M:%S.%f')
    print(f'Received image {cur_time - create_time} sec. after creation')


@sio.on('connect')
def connect(sid, environ):
    print(f'connect at {datetime.now()} {sid}')


@sio.on('image')
def image(sid, data):
    print_time_of_flight(data['time'])
    x_image = data['stream'][:data['split_pos']]
    y_image = data['stream'][data['split_pos']:]
    save_image('x', x_image)
    save_image('y', y_image)
    main.on_incoming_images(
        convert_jpeg_bytes_into_numpy_rgb(x_image),
        convert_jpeg_bytes_into_numpy_rgb(y_image)
    )


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


main.setup()
eventlet.wsgi.server(eventlet.listen((local_ip, 8000)), app)
