import os
import subprocess


ssh_connect_cmd = 'ssh -i ~/.ssh/ssh_pi pi@192.168.0.84'
remote_working_dir = '/home/pi/Desktop'
dirname = os.path.dirname(__file__)
remote_script_name = 'capture_image_remote_script.py'
remote_script_path = os.path.join(dirname, remote_script_name)
image_folder_path = os.path.join(dirname, '..', 'pi_images')


def copy_file_to_remote(file_path, remote_dir):
    return os.popen(f'cat {file_path} | {ssh_connect_cmd} "cat > {remote_dir}/{os.path.basename(file_path)}"')


def copy_file_from_remote(remote_file_path, local_file_path):
    return subprocess.call(f'{ssh_connect_cmd} "cat {remote_file_path}" > {local_file_path}', shell=True)


def execute_remote_command(command):
    return os.popen(f'{ssh_connect_cmd} "{command}"')


def delete_remote_image(remote_file_path):
    execute_remote_command(f'rm {remote_file_path}')


def take_image_on_remote():
    copy_file_to_remote(remote_script_path, remote_working_dir)

    output = execute_remote_command(f'python {remote_working_dir}/{remote_script_name}')
    picture_file_name = output.read()
    return picture_file_name


def copy_image_from_remote_to_local(remote_file_path):
    local_file_path = f'{image_folder_path}/{remote_file_path.split("/")[-1]}'
    copy_file_from_remote(remote_file_path, local_file_path)
    return local_file_path


def capture_and_get_image_from_remote():
    remote_path = take_image_on_remote()
    local_file_path = copy_image_from_remote_to_local(remote_path)
    delete_remote_image(remote_path)
    return local_file_path


if __name__ == '__main__':
    capture_and_get_image_from_remote()
