import os
from pathlib import Path
from helper_functions.bash_functions import copy_file_to_remote, copy_file_from_remote, via_ssh, execute_command


dirname = os.path.dirname(__file__)
take_image_script_path = os.path.join(dirname, "helper_functions/take_image.py")
take_image_script_file_name = os.path.basename(take_image_script_path)
remote_working_dir = '/home/pi/Desktop'
remote_take_image_path = '/home/pi/Desktop/' + take_image_script_file_name


class Camera:
    def __init__(self, axis, remote_connection=False):
        if remote_connection:
            self.remote_connection = remote_connection
            self.remote = True
        else:
            self.remote_connection = None
            self.remote = False

        self.pos = None
        self.axis = axis
        self.image_dir = os.path.join(dirname, f'./pi_images/{self.axis}')

        self._make_sure_camera_image_dir_exists()

    def _make_sure_camera_image_dir_exists(self):
        Path(self.image_dir).mkdir(parents=True, exist_ok=True)

    def take_photo(self):
        return self._take_photo_on_remote() if self.remote else self._take_photo_on_local()

    def _take_photo_on_remote(self):
        copy_file_to_remote(take_image_script_path, remote_working_dir, self.remote_connection)
        remote_path = execute_command(via_ssh(f'python {remote_take_image_path}', self.remote_connection))
        local_file_path = copy_file_from_remote(remote_path, self.image_dir, self.remote_connection)
        # execute_command(via_ssh(f'rm {remote_path}', self.remote_connection))
        # return local_file_path
        return 'a'

    def _take_photo_on_local(self):
        from helper_functions.take_image import take_image
        local_file_path = take_image(self.image_dir)
        return local_file_path
