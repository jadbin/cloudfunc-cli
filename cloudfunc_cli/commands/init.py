# coding=utf-8

import os
from os.path import abspath, join, exists, dirname, isdir, basename
from shutil import ignore_patterns

from jinja2 import Environment
import inquirer
from inquirer.themes import GreenPassion
from inquirer.errors import ValidationError

from cloudfunc_cli.errors import AbortedError, TemplateError
from cloudfunc_cli.config import _template_folder
from cloudfunc_cli.utils import string_lowercase_underscore
from .base import Command


class InitCommand(Command):
    @property
    def syntax(self):
        return '[options]'

    @property
    def name(self):
        return 'init'

    @property
    def short_desc(self):
        return 'Initialize a project'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--root-dir', dest='root_dir', metavar='DIR',
                            help='application root directory')

    def run(self, args):
        project_dir = abspath(args.root_dir or '')
        try:
            settings = self.get_settings_by_steps(project_dir)
            self.copy_files(project_dir, settings)
        except (KeyboardInterrupt, AbortedError):
            print(flush=True)
            self.exitcode = 1

    def get_settings_by_steps(self, project_dir: str) -> dict:
        settings = {'project_dir': project_dir}
        default_project_name = string_lowercase_underscore(basename(project_dir))

        q = [
            inquirer.Text('project_name',
                          message='What is the name of your application? ({})'.format(default_project_name),
                          validate=project_name_validation)
        ]
        answers = inquirer.prompt(q, theme=GreenPassion())
        settings['project_name'] = answers['project_name'] or default_project_name
        return settings

    def copy_files(self, project_dir: str, settings: dict):
        settings = dict(settings)
        settings['project_dir'] = project_dir

        self.filename_mapping = self.make_filename_mapping(settings)

        self.copytree(join(_template_folder, 'project'), project_dir, settings)

    def make_filename_mapping(self, settings):
        m = {
            '_project_name': settings['project_name'],
        }
        return m

    def copytree(self, src: str, dst: str, settings: dict):
        names = os.listdir(src)
        ignored_names = ignore_patterns('*.pyc')(src, names)
        for name in names:
            if name in ignored_names:
                continue
            src_path = join(src, name)
            dst_name, is_template = self.resolve_filename(name)
            dst_path = join(dst, dst_name)
            dst_rel_path = self.relative_path(dst_path, settings['project_dir'])

            if isdir(src_path):
                self.copytree(src_path, dst_path, settings)
            else:
                content = self.read_file(src_path)
                if is_template:
                    content = self.render_string(content, **settings)
                print('>', dst_rel_path)
                self.write_file(dst_path, content)

    def resolve_filename(self, name):
        if name.endswith('.jinja2'):
            is_template = True
            name = name.rsplit('.', maxsplit=1)[0]
        else:
            is_template = False
        if name in self.filename_mapping:
            name = self.filename_mapping[name]
        return name, is_template

    @staticmethod
    def relative_path(path, fpath):
        path = abspath(path)
        fpath = abspath(fpath)
        if path.startswith(fpath):
            path = path[len(fpath):]
            if path.startswith(os.path.sep):
                path = path[1:]
        return path

    @staticmethod
    def read_file(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_file(path, raw):
        d = dirname(path)
        if not exists(d):
            os.makedirs(d)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(raw)

    @staticmethod
    def render_string(raw, **kwargs):
        env = jinja2_env()
        return env.from_string(raw).render(**kwargs)


def jinja2_env():
    def _raise_helper(message):
        if message:
            raise TemplateError(message)
        raise TemplateError

    def _assert_helper(logical, message=None):
        if not logical:
            _raise_helper(message)
        return ''

    env = Environment(keep_trailing_newline=True)
    env.globals['raise'] = _raise_helper
    env.globals['assert'] = _assert_helper
    return env


def project_name_validation(answers, current):
    project_name = string_lowercase_underscore(current)
    if project_name:
        if project_name != current or str.isdigit(project_name[0]):
            raise ValidationError(current, reason="Only lowercase letters, digits and '_' available")
    return True
