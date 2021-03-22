import itertools
import operator
import os
import subprocess
from typing import List, Dict

import nox
import nox_poetry

OLDEST_MINOR_VERSION = 6

_friendly_name_mapping: Dict[str, str] = dict()


def friendly_name(self) -> str:
    name = self._orig_friendly_name
    return _friendly_name_mapping.get(name, name)


nox.sessions.SessionRunner._orig_friendly_name = nox.sessions.SessionRunner.friendly_name
# noinspection PyPropertyAccess
nox.sessions.SessionRunner.friendly_name = property(friendly_name)


def _get_latest_minor_versions() -> List[str]:
    def shell_output(*args):
        return subprocess.run(list(args), stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    pyenv_root = shell_output('pyenv', 'root')
    versions_output = shell_output('pyenv', 'whence', 'python3')
    sorted_versions = sorted(tuple(map(int, v.split('.'))) for v in versions_output.split('\n'))
    paths = []
    for _, minor_group in itertools.groupby(sorted_versions, operator.itemgetter(1)):
        version = '.'.join(map(str, list(minor_group)[-1]))
        path = os.path.join(pyenv_root, 'versions', version, 'bin', 'python')
        _friendly_name_mapping[f'tests-{path}'] = f'tests-python{version}'
        paths.append(path)
    return paths


@nox_poetry.session(python=_get_latest_minor_versions())
def tests(session: nox_poetry.Session):
    session.install('pytest', '.')
    session.run('pytest', 'tests/')
