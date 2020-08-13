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
        return '[ENV]'

    @property
    def name(self):
        return 'deploy'

    @property
    def short_desc(self):
        return 'Deploy the project'

    def add_arguments(self, parser):
        parser.add_argument(dest='env', nargs='?', metavar='ENV',
                            help='specific cloudfunc env')

    def run(self, args):
        project_dir = abspath('')
        if args.env:
            os.environ['CLOUDFUNC_ENV'] = args.env
        load_env(project_dir, env=os.environ.get('CLOUDFUNC_ENV'))

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
