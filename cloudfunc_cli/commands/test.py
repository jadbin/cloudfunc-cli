# coding=utf-8

import sys
import os
from os.path import abspath

import pytest

from .base import Command, load_env


class Test(Command):
    @property
    def syntax(self):
        return '[PROFILE]'

    @property
    def name(self):
        return 'test'

    @property
    def short_desc(self):
        return 'Run pytest for this project'

    def add_arguments(self, parser):
        parser.add_argument(dest='profile', nargs='?', metavar='PROFILE',
                            help='active profile')

    def run(self, args):
        project_dir = abspath('')
        load_env(project_dir, profile=args.profile)
        os.environ['CLOUDFUNC_DEBUG'] = '1'

        errno = pytest.main(['tests'])
        sys.exit(errno)
