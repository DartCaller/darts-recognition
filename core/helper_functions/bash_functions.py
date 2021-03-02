import os
import subprocess


def copy_file_to_remote(file_path, remote_dir, ssh_ip):
    return execute_command(
        f'cat {file_path} | ssh {ssh_ip} "cat > {remote_dir}/{os.path.basename(file_path)}"'
    )


def copy_file_from_remote(remote_file_path, local_file_path, ssh_ip):
    filename = os.path.basename(remote_file_path)
    subprocess.call(
        f'ssh {ssh_ip} "cat {remote_file_path}" > {local_file_path}/{filename}',
        shell=True
    )
    return f'{local_file_path}/{filename}'


def via_ssh(command, ssh_ip):
    return f'ssh {ssh_ip} "{command}"'


def execute_command(cmd):
    return os.popen(cmd).read().rstrip()
