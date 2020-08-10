# coding=utf-8

import re
from importlib import import_module
from pkgutil import iter_modules


def walk_modules(path: str):
    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


_camelcase_invalid_chars = re.compile(r'[^a-zA-Z\d]')

_camelcase_split_chars = re.compile(r'(.)([A-Z][a-z]+)')
_camelcase_split_chars2 = re.compile(r'([a-z0-9])([A-Z])')


def string_camelcase(s):
    a = _camelcase_invalid_chars.split(s)
    return ''.join([(i[0].upper() + i[1:]) for i in a if i])


def string_lowercase_underscore(s):
    s = string_camelcase(s)
    s = _camelcase_split_chars.sub(r'\1_\2', s)
    return _camelcase_split_chars2.sub(r'\1_\2', s).lower()
