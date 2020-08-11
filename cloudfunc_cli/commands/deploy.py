# coding=utf-8

import os
from os.path import abspath, isfile, join

from dotenv import load_dotenv
from requests import HTTPError

from cloudfunc_cli.package import create_package
from cloudfunc_cli.uploader import Uploader
from .base import Command


class Deploy(Command):
    @property
    def syntax(self):
        return '[PROFILE]'

    @property
    def name(self):
        return 'deploy'

    @property
    def short_desc(self):
        return 'Deploy application'

    def add_arguments(self, parser):
        parser.add_argument(dest='profile', nargs='?', metavar='PROFILE',
                            help='active profile to develop this application')

    def run(self, args):
        project_dir = abspath('')
        profile = args.profile
        default_env_file = join(project_dir, '.cloudfunc.env')
        if isfile(default_env_file):
            load_dotenv(default_env_file)
        if profile:
            profile_env_file = join(project_dir, '.cloudfunc.env.{}'.format(profile))
            load_dotenv(profile_env_file)
        pkg = create_package(project_dir)
        upload_url = 'http://{}/repo/upload'.format(os.environ['CLOUDFUNC_SERVE_ADDRESS'])
        uploader = Uploader(upload_url)
        resp = uploader.upload(pkg)
        try:
            resp.raise_for_status()
        except HTTPError:
            print('Failed:', resp.text)
        else:
            print('Success')
