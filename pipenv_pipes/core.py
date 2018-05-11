
import os
from collections import namedtuple
import pathlib
import hashlib
import base64

from .pipenv import call_python_version
from .utils import (
    get_project_name,
    get_project_dir_filepath,
)

Environment = namedtuple('Environment', [
    'envpath',
    'envname',
    'project_name',
    'binpath',
    ])


def find_environments(pipenv_home):
    """
    Returns Environment NamedTuple created from list of folders found in the
    Pipenv Environment location
    """
    environments = []
    for folder_name in sorted(os.listdir(pipenv_home)):
        envpath = os.path.join(pipenv_home, folder_name)
        project_name = get_project_name(folder_name)
        if not project_name:
            continue

        binpath = find_binary(envpath)
        environment = Environment(project_name=project_name,
                                  envpath=envpath,
                                  envname=folder_name,
                                  binpath=binpath,
                                  )
        environments.append(environment)
    return environments


def find_binary(envpath):
    """ Finds the python binary in a given environment path """
    env_ls = os.listdir(envpath)
    if 'bin' in env_ls:
        binpath = os.path.join(envpath, 'bin', 'python')
    elif 'Scripts' in env_ls:
        binpath = os.path.join(envpath, 'Scripts', 'python.exe')
    else:
        raise EnvironmentError(
            'could not find python binary path: {}'.format(envpath))
    if os.path.exists(binpath):
        return binpath
    else:
        raise EnvironmentError(
            'could not find python binary: {}'.format(envpath))


def get_binary_version(envpath):
    """ Returns a string indicating the Python version (Python 3.5.6) """
    binpath = find_binary(envpath)
    version, code = call_python_version(binpath)
    if not code:
        return version
    else:
        raise EnvironmentError('could not get binary version')


def resolve_envname_hash(project_dir=None):
    """
    Attempts to resolve envname.
    Although this might not be reliable, currently the only alternative
    is to from project_dir run `pipenv --venv`. This is slow for use
    and testing. Initially this is intended to be used for testing only,
    however if it remains stable it could replace the call_pipenv_venv calls
    """
    pipfile = pathlib.PurePath(project_dir) / 'Pipfile'
    hash = hashlib.sha256(str(pipfile).encode()).digest()[:6]
    encoded_hash = base64.urlsafe_b64encode(hash).decode()
    return encoded_hash[:8]


###############################
# Project Dir File (.project) #
###############################

def read_project_dir_file(envpath):
    project_file = get_project_dir_filepath(envpath)
    try:
        with open(project_file) as fp:
            return fp.read().strip()
    except IOError:
        return


def write_project_dir_project_file(envpath, project_dir):
    project_file = get_project_dir_filepath(envpath)
    with open(project_file, 'w') as fp:
        return fp.write(project_dir)


def delete_project_dir_file(envpath):
    project_file = get_project_dir_filepath(envpath)
    try:
        os.remove(project_file)
    except IOError:
        pass
    else:
        return project_file
