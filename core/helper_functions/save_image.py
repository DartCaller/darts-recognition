from multiprocessing import Process
from datetime import datetime


def save_image(axis, stream):
    p = Process(target=save_image_daemon, args=(axis, stream))
    p.daemon = True
    p.start()


def save_image_daemon(axis, stream):
    with open(f'./pi_images/{axis}/{datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}.jpeg', 'wb') as file:
        file.write(stream)
