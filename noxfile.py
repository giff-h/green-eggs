# -*- coding: utf-8 -*-
import itertools
import operator
import os
import subprocess
from typing import Dict, List

import nox
import nox_poetry

OLDEST_MINOR_VERSION = 6

_friendly_name_mapping: Dict[str, str] = dict()


def friendly_name(self) -> str:
    name = self._orig_friendly_name
    return _friendly_name_mapping.get(name, name)


nox.sessions.SessionRunner._orig_friendly_name = nox.sessions.SessionRunner.friendly_name  # type: ignore[attr-defined]
# noinspection PyPropertyAccess
nox.sessions.SessionRunner.friendly_name = property(friendly_name)  # type: ignore[assignment]


def _get_latest_minor_versions() -> List[str]:
    def shell_output(*args):
        return subprocess.run(list(args), stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    pyenv_root = shell_output('pyenv', 'root')
    versions_output = shell_output('pyenv', 'whence', 'python3')
    sorted_versions = sorted(tuple(map(int, v.split('.'))) for v in versions_output.split('\n'))
    paths = []
    for minor, minor_group in itertools.groupby(sorted_versions, operator.itemgetter(1)):
        if minor >= 7:
            latest_minor = tuple(map(str, list(minor_group)[-1]))
            path = os.path.join(pyenv_root, 'versions', '.'.join(latest_minor), 'bin', 'python')
            _friendly_name_mapping[f'tests_pyenv-{path}'] = f'tests-pyenv-python{".".join(latest_minor[:-1])}'
            paths.append(path)
    return paths


@nox_poetry.session(python=_get_latest_minor_versions())
def tests_pyenv(session: nox_poetry.Session):
    """
    Runs pytest on the latest patch of each available pyenv minor python version at least 3.7.
    """
    session.install('pytest-asyncio', 'pytest-mock', '.')
    session.run('pytest', 'tests/')


@nox_poetry.session()
def tests_whichever(session: nox_poetry.Session):
    """
    Runs pytest on the first python version that nox finds.
    """
    session.install('pytest-asyncio', 'pytest-mock', '.')
    session.run('pytest', 'tests/')
