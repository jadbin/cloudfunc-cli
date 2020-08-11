# coding=utf-8

import os
from os.path import abspath

import requests

from cloudfunc_cli.package import create_package
from cloudfunc_cli.uploader import Uploader
from .base import Command, load_env


class Deploy(Command):
    @property
    def syntax(self):
        return '[PROFILE]'

    @property
    def name(self):
        return 'deploy'

    @property
    def short_desc(self):
        return 'Deploy the project'

    def add_arguments(self, parser):
        parser.add_argument(dest='profile', nargs='?', metavar='PROFILE',
                            help='active profile')

    def run(self, args):
        project_dir = abspath('')
        load_env(project_dir, profile=args.profile)

        pkg = create_package(project_dir)
        upload_url = 'http://{}/repo/upload'.format(os.environ['CLOUDFUNC_SERVE_ADDRESS'])
        uploader = Uploader(upload_url)
        resp = uploader.upload(pkg)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            print('Failed:', resp.text)
        else:
            print('Success')
