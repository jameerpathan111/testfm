# helpers required for TestFM
from fabric import Connection
from testfm.constants import SAT_HOSTNAME
import os


def product(server):
    """This helper provides Satellite/Capsule version. Use decorator ansible_host_pattern
    from testfm.decorators to get server i.e satellite/capsule or
    use fixture server from conftest.py"""
    if server == 'satellite':
        satellite_version = os.popen(
            'ansible -i testfm/inventory satellite --user root -m shell '
            '-a "rpm -q satellite --queryformat=%{VERSION}" -o').read()
        satellite_project = satellite_version.splitlines()[0].split(' ')[-1]
        if satellite_project.startswith('6.7'):
            return ['sat67', '6.7']
        elif satellite_project.startswith('6.6'):
            return ['sat66', '6.6']
        elif satellite_project.startswith('6.5'):
            return ['sat65', '6.5']
        elif satellite_project.startswith('6.4'):
            return ['sat64', '6.4']
        elif satellite_project.startswith('6.3'):
            return ['sat63', '6.3']
        elif satellite_project.startswith('6.2'):
            return ['sat62', '6.2']
        else:
            return ['sat61', '6.1']
    if server == 'capsule':
        capsule_version = os.popen(
            'ansible -i testfm/inventory capsule --user root -m shell '
            '-a "rpm -q satellite-capsule --queryformat=%{VERSION}" -o').read()
        capsule_project = capsule_version.splitlines()[0].split(' ')[-1]
        # For Capsule
        if capsule_project.startswith('6.7'):
            return ['cap67', '6.7']
        elif capsule_project.startswith('6.6'):
            return ['cap66', '6.6']
        elif capsule_project.startswith('6.5'):
            return ['cap65', '6.5']
        elif capsule_project.startswith('6.4'):
            return ['cap64', '6.4']
        elif capsule_project.startswith('6.3'):
            return ['cap63', '6.3']
        elif capsule_project.startswith('6.2'):
            return ['cap62', '6.2']
        else:
            return ['cap61', '6.1']


def run(command):
    """ Use this helper to execute shell command on Satellite"""
    return Connection(SAT_HOSTNAME, 'root').run(command)
