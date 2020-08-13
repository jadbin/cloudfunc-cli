# coding=utf-8

import sys
import os
from os.path import abspath

import pytest

from .base import Command, load_env


class Test(Command):
    @property
    def syntax(self):
        return '[ENV]'

    @property
    def name(self):
        return 'test'

    @property
    def short_desc(self):
        return 'Run pytest for this project'

    def add_arguments(self, parser):
        parser.add_argument(dest='env', nargs='?', metavar='ENV',
                            help='specific cloudfunc env')

    def run(self, args):
        project_dir = abspath('')
        if args.env:
            os.environ['CLOUDFUNC_ENV'] = args.env
        load_env(project_dir, env=os.environ.get('CLOUDFUNC_ENV'))

        errno = pytest.main(['tests'])
        sys.exit(errno)
