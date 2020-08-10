# coding=utf-8

import re
import sys
from os.path import join, dirname
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

with open(join(dirname(__file__), 'README.rst'), 'r', encoding='utf-8') as fd:
    long_description = fd.read()


def read_version():
    p = join(dirname(__file__), 'cloudfunc_cli', '__init__.py')
    with open(p, 'r', encoding='utf-8') as f:
        return re.search(r"__version__ = '([^']+)'", f.read()).group(1)


def read_requirements(file):
    with open(join(dirname(__file__), 'requirements', file), 'r', encoding='utf-8') as f:
        return [l.strip() for l in f]


class PyTest(TestCommand):
    def run_tests(self):
        import pytest

        errno = pytest.main(['tests'])
        sys.exit(errno)


tests_require = read_requirements('test.txt')
version = read_version()
install_requires = [
    'cloudfunc=={}'.format(version),
    'inquirer>=2.7.0',
    'Jinja2>=2.11.2',
    'python-dotenv>=0.14.0',
    'requests>=2.24.0',
    'requests-toolbelt>=0.9.1',
    'tqdm>=4.48.2',
]


def main():
    if sys.version_info < (3, 6):
        raise RuntimeError("The minimal supported Python version is 3.6")

    setup(
        name="cloudfunc-cli",
        version=version,
        url="https://github.com/jadbin/cloudfunc-cli",
        description="Standard tooling for cloudfunc development",
        long_description=long_description,
        author="jadbin",
        author_email="jadbin.com@hotmail.com",
        license="MIT",
        zip_safe=False,
        packages=find_packages(exclude=("tests",)),
        include_package_data=True,
        entry_points={
            "console_scripts": ["cloudfunc = cloudfunc_cli.main:main"]
        },
        python_requires='>=3.6',
        install_requires=install_requires,
        tests_require=tests_require,
        cmdclass={"test": PyTest},
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ]
    )


if __name__ == "__main__":
    main()
