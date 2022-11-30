# -*- coding: utf-8 -*-
import itertools
import operator
import os
import subprocess
from typing import Dict, List, Optional

import nox
import nox_poetry

_friendly_name_mapping: Dict[str, str] = dict()


def friendly_name(self) -> str:
    name = self._orig_friendly_name
    return _friendly_name_mapping.get(name, name)


nox.sessions.SessionRunner._orig_friendly_name = nox.sessions.SessionRunner.friendly_name  # type: ignore[attr-defined]
# noinspection PyPropertyAccess
nox.sessions.SessionRunner.friendly_name = property(friendly_name)  # type: ignore[assignment]


def _get_latest_patch_of_minor_versions(
    *, oldest_minor: Optional[int] = None, latest_minor: Optional[int] = None
) -> List[str]:
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
                latest_patch = list(minor_group)[-1]
                path = os.path.join(pyenv_root, 'versions', '.'.join(map(str, latest_patch)), 'bin', 'python')
                _friendly_name_mapping[f'tests_pyenv-{path}'] = f'tests_pyenv-python3.{minor}'
                paths.append(path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If anything fails, resolve to no paths
        pass
    return paths


def _run_tests(session: nox_poetry.Session, with_coverage=True, do_cov_append=False):
    session.install('pytest-asyncio', 'pytest-cov', 'pytest-mock', '.')

    extra_args = []
    if with_coverage:
        extra_args.append('--cov=green_eggs')
        extra_args.append('--cov-report=html')
        if do_cov_append:
            extra_args.append('--cov-append')

    session.run('pytest', *extra_args, 'tests')


@nox_poetry.session(python=_get_latest_patch_of_minor_versions(oldest_minor=7, latest_minor=10))
def tests_pyenv(session: nox_poetry.Session):
    """
    Runs pytest with coverage on the latest available patch of each pyenv python version between 3.7 and 3.10.
    """
    first_python_name = f'tests_pyenv-{tests_pyenv.python[0]}'  # type: ignore[attr-defined]
    is_first_run = _friendly_name_mapping.get(first_python_name) == session.name
    _run_tests(session, do_cov_append=not is_first_run)


@nox_poetry.session()
def tests_whichever(session: nox_poetry.Session):
    """
    Runs pytest with coverage on the python that ran nox.
    """
    _run_tests(session)
