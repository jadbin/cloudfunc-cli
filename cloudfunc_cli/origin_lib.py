# coding=utf-8

from typing import List

import requests


class LibFetcher:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()

    def fetch(self, libs: List[str]) -> List[dict]:
        result = []
        for lib in libs:
            resp = self.session.get(self.url, params={'name': lib})
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                is_set = False
                data = [data]
            else:
                is_set = True
            for d in data:
                d['cloud_func_name'] = f"{lib}.{d['name']}" if is_set else lib
            result.extend(data)
        return result


def write_lib_definitions_to_file(libs: List[dict], file: str):
    to_write = _prepare_lib_definitions(libs)
    with open(file, 'w') as f:
        for s in to_write:
            f.write(s)


def _prepare_lib_definitions(libs: List[dict]) -> List[str]:
    lib_imports = set()
    func_defines = []
    func_names = set()
    for lib in libs:
        func_defines.append(f"\n\n@origin_func('{lib['cloud_func_name']}')\n")
        func_defines.append(f"def {lib['cloud_func_name'] if lib['name'] in func_names else lib['name']}(")
        func_names.add(lib['name'])
        for i, arg in enumerate(lib['arg_info']):
            if i > 0:
                func_defines.append(', ')
            arg_name = arg['name']
            func_defines.append(arg_name)
            if arg_name in lib['type_info']:
                arg_type = lib['type_info'][arg_name]
                if arg_type['module_name'] != 'builtins':
                    lib_imports.add(f"from {arg_type['module_name']} import {arg_type['class_name']}\n")
                func_defines.append(f": {arg_type['class_name']}")
                if arg['default'] is not None:
                    func_defines.append(f" = {arg['default']}")
            else:
                if arg['default'] is not None:
                    func_defines.append(f"={arg['default']}")
        func_defines.append(')')
        if 'return' in lib['type_info']:
            return_type = lib['type_info']['return']
            if return_type['module_name'] != 'builtins':
                lib_imports.add(f"from {return_type['module_name']} import {return_type['class_name']}\n")
            func_defines.append(f" -> {return_type['class_name']}")
        func_defines.append(':\n')
        func_defines.append('    """{}"""\n'.format(lib['doc'] or ''))

    result = ['# coding=utf-8\n\n']
    lib_imports = sorted(lib_imports)
    if len(lib_imports) > 0:
        result.extend(lib_imports)
        result.append('\n')
    result.append('from cloudfunc import origin_func\n')
    result.extend(func_defines)
    return result
