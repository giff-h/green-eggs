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


def _get_latest_patch_of_minor_versions(*, oldest_minor: int = None, latest_minor: int = None) -> List[str]:
    if oldest_minor is not None and latest_minor is not None and oldest_minor > latest_minor:
        raise ValueError(f'oldest_minor {oldest_minor} may not be greater than latest_minor {latest_minor}')

    def shell_output(*args):
        return subprocess.run(list(args), stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').strip()

    paths = []
    try:
        pyenv_root = shell_output('pyenv', 'root')
        versions_output = shell_output('pyenv', 'whence', 'python3')
        sorted_versions = sorted(tuple(map(int, v.split('.'))) for v in versions_output.split('\n'))
        for minor, minor_group in itertools.groupby(sorted_versions, operator.itemgetter(1)):
            include_version = (oldest_minor is None or minor >= oldest_minor) and (
                latest_minor is None or minor <= latest_minor
            )
            if include_version:
                latest_patch = tuple(map(str, list(minor_group)[-1]))
                path = os.path.join(pyenv_root, 'versions', '.'.join(latest_patch), 'bin', 'python')
                _friendly_name_mapping[f'tests_pyenv-{path}'] = f'tests_pyenv-python{".".join(latest_patch[:-1])}'
                paths.append(path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If anything fails, resolve to no paths
        pass
    return paths


def _run_tests(session: nox_poetry.Session, with_coverage=True):
    session.install('pytest-asyncio', 'pytest-cov', 'pytest-mock', '.')
    test_args = ['--cov-report=html', '--cov-append', '--cov=green_eggs'] if with_coverage else []
    session.run('pytest', *test_args, 'tests/')


@nox_poetry.session(python=_get_latest_patch_of_minor_versions(oldest_minor=7, latest_minor=10))
def tests_pyenv(session: nox_poetry.Session):
    """
    Runs pytest with coverage on the latest patch of each available pyenv minor python version at least 3.7.
    """
    _run_tests(session)


@nox_poetry.session()
def tests_whichever(session: nox_poetry.Session):
    """
    Runs pytest with coverage on the first python version that nox finds.
    """
    _run_tests(session)


@nox_poetry.session()
def tests_ci(session: nox_poetry.Session):
    """
    Runs pytest without coverage for CI.
    """
    _run_tests(session, with_coverage=False)
