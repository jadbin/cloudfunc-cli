# coding=utf-8

import fnmatch
import os
from os.path import basename, join, isfile, isdir, relpath
from typing import List
import tarfile

from cloudfunc.setuptools import run_setup, after_setup


class PackageFile:
    def __init__(self, filename: str, metadata: dict):
        self.filename = filename
        self.base_filename = basename(filename)
        self.metadata = dict(metadata)


def create_package(project_dir: str) -> PackageFile:
    setup_file = join(project_dir, 'setup.py')
    if not isfile(setup_file):
        raise FileNotFoundError(setup_file)
    run_setup(setup_file)
    metadata = after_setup

    package_files = _read_package_files(project_dir)
    package_dist_dir = join(project_dir, 'dist')
    os.makedirs(package_dist_dir, exist_ok=True)
    package_dist_file = join(
        package_dist_dir,
        '{}-{}.tar'.format(metadata['name'], metadata['version'])
    )
    with tarfile.open(package_dist_file, 'w') as f:
        for file in package_files:
            f.add(file, arcname=relpath(file, project_dir))
    return PackageFile(package_dist_file, metadata)


def _read_package_files(project_dir: str) -> List[str]:
    ignores = []
    ignore_file = join(project_dir, '.cloudfunc.ignore')
    if isfile(ignore_file):
        with open(ignore_file, 'r') as f:
            for line in f:
                s = line.strip()
                if s:
                    if s.startswith('*') or s.startswith('/'):
                        pass
                    else:
                        ignores.append('*/' + s)
                    ignores.append(s)
    return _walk_files('', base=project_dir, ignores=ignores)


def _walk_files(path: str, base: str = None, ignores: List[str] = None):
    if base is None:
        cur_path = path
    else:
        cur_path = join(base, path)
    if any((fnmatch.fnmatch(path, i) for i in ignores)):
        return []
    files = []
    if isdir(cur_path):
        names = os.listdir(cur_path)
        for name in names:
            files += _walk_files(join(path, name), base=base, ignores=ignores)
    elif isfile(cur_path):
        files.append(cur_path)
    return files
