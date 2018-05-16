from __future__ import print_function
import argparse
import functools
import importlib
import inspect
import os
import pkgutil
import string
import sys


__all__ = ['configure', 'find_registrations', 'main', 'register']


def _default_serializer(entries):
    cron_entry_template = '${schedule} ${python_executable} ${script_path} run ${fn_name}'
    return '\n'.join(
        string.Template(cron_entry_template).safe_substitute(**entry)
        for entry in entries
    )


class Cronner:
    def __init__(self):
        self._registry = {}
        self.configure()

    def __contains__(self, fn_name):
        return fn_name in self._registry

    def configure(self, serializer=None, kronjob_template=None):
        if serializer is not None:
            self._serializer = serializer
        elif kronjob_template is not None:
            from cronner.kronjob_util import serialize_kronjob
            self._serializer = functools.partial(serialize_kronjob, kronjob_template)
        else:
            self._serializer = _default_serializer

    def register(self, schedule, template_vars=None):
        if template_vars is not None:
            template_vars = dict(template_vars, schedule=schedule)
        else:
            template_vars =  {'schedule': schedule}
        def wrapper(fn):
            fn_name = '{}.{}'.format(fn.__module__, fn.__name__)
            fn_cfg = {
                '_fn': fn,
                'template_vars': template_vars
            }
            if fn_name in self._registry and self._registry[fn_name] != fn_cfg:
                raise Exception('Function %s and %s have the same name %s' % (fn, self._registry[fn_name]['_fn'], fn_name))
            self._registry[fn_name] = fn_cfg
            return fn
        return wrapper

    def get_entries(self):
        return self._serializer([
            dict(
                {'fn_name': fn_name, 'python_executable': sys.executable, 'script_path': os.path.abspath(sys.argv[0])},
                **fn_cfg['template_vars']
            )
            for fn_name, fn_cfg in self._registry.items()
        ])

    def find_registrations(self, *module_names):
        for module_name in module_names:
            module = importlib.import_module(module_name)
            if hasattr(module, '__path__'):  # module is a package
                for _, name, _ in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
                    importlib.import_module(name, package=module)

    def run(self, fn_name, *params):
        self._registry[fn_name]['_fn'](*params)

    def main(self, argv=None):
        commands = {
            'gen-cfg': lambda _: print(self.get_entries()),
            'run': lambda args: self.run(args.fn_name, *args.params)
        }

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = True

        gen_cfg_parser = subparsers.add_parser('gen-cfg')

        run_parser = subparsers.add_parser('run')
        run_parser.add_argument('fn_name', choices=self._registry.keys())
        run_parser.add_argument('--params', nargs='+', default=[])

        args = parser.parse_args(argv)
        commands[args.command](args)


_CRONNER = Cronner()
configure = _CRONNER.configure
find_registrations = _CRONNER.find_registrations
register = _CRONNER.register
main = _CRONNER.main
