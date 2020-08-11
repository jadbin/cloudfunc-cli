# coding=utf-8

import os
from os.path import abspath, isfile, join, relpath, isdir

import requests
import inquirer
from inquirer.themes import GreenPassion

from cloudfunc_cli.origin_lib import LibFetcher, write_lib_definitions_to_file
from .base import Command, load_env


class Fetch(Command):
    @property
    def syntax(self):
        return '[PROFILE]'

    @property
    def name(self):
        return 'fetch'

    @property
    def short_desc(self):
        return 'Fetch the project dependencies'

    def add_arguments(self, parser):
        parser.add_argument(dest='profile', nargs='?', metavar='PROFILE',
                            help='active profile')

    def run(self, args):
        project_dir = abspath('')
        load_env(project_dir, profile=args.profile)

        lib_file = join(project_dir, '.cloudfunc.libs')
        if not isfile(lib_file):
            print("No '.cloudfunc.libs'")
            self.exitcode = 1
            return

        libs = set()
        with open(lib_file, 'r') as f:
            for line in f:
                s = line.strip()
                if s not in libs:
                    libs.add(s)
        libs = sorted(libs)
        fetch_url = 'http://{}/cloud-funcs'.format(os.environ['CLOUDFUNC_SERVE_ADDRESS'])
        fetcher = LibFetcher(fetch_url)
        try:
            libs = fetcher.fetch(libs)
        except requests.HTTPError as e:
            print('Failed:', e.response.text)
            self.exitcode = 1
            return

        lib_dir = self._choose_libs_file(project_dir)
        file = join(project_dir, lib_dir, 'origin_libs.py')
        write_lib_definitions_to_file(libs, file)
        print('View at: {}'.format(relpath(file, project_dir)))

    def _choose_libs_file(self, project_dir: str) -> str:
        choices = []
        for name in os.listdir(project_dir):
            d = join(project_dir, name)
            if isdir(d) and isfile(join(d, '__init__.py')):
                choices.append(name)
        choices.append('.')
        if len(choices) > 1:
            questions = [
                inquirer.List(
                    'libs_dir',
                    message="Where to put the libs?",
                    choices=choices,
                ),
            ]
            answers = inquirer.prompt(questions, theme=GreenPassion(), raise_keyboard_interrupt=True)
            libs_dir = answers['libs_dir']
        else:
            libs_dir = choices[0]
        if libs_dir == '.':
            libs_dir = ''
        return libs_dir
