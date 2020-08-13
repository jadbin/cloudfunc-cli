# coding=utf-8

from os.path import join, isfile

from dotenv import load_dotenv


class Command:
    def __init__(self):
        self.exitcode = 0

    @property
    def name(self):
        return ""

    @property
    def syntax(self):
        return ""

    @property
    def short_desc(self):
        return ""

    @property
    def long_desc(self):
        return self.short_desc

    def add_arguments(self, parser):
        pass

    def process_arguments(self, args):
        pass

    def run(self, args):
        raise NotImplementedError


def load_env(project_dir: str, env: str = None):
    default_env_file = join(project_dir, '.cloudfunc.env')
    if isfile(default_env_file):
        load_dotenv(default_env_file)
    if env:
        env_file = join(project_dir, '.cloudfunc.env.{}'.format(env))
        load_dotenv(env_file)
