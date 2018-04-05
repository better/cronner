from __future__ import print_function
import argparse
import inspect
import os
import string
import sys


_DEFAULT_TEMPLATE = '${schedule} ${python_executable} ${script_path} run ${fn_name}'
_DEFAULT_TEMPLATE_JOINER = '\n'


class Cronner:
    def __init__(self):
        self._registry = {}
        self.configure()

    def __contains__(self, fn_name):
        return fn_name in self._registry

    def configure(self, template=_DEFAULT_TEMPLATE, template_joiner=_DEFAULT_TEMPLATE_JOINER):
        self._template = template
        self._template_joiner = template_joiner

    def register(self, schedule, name=None, template_vars=None):
        if template_vars is not None:
            template_vars = dict(template_vars, schedule=schedule)
        else:
            template_vars =  {'schedule': schedule}
        def wrapper(fn):
            fn_name = name if name is not None else fn.__name__
            fn_cfg = {
                '_fn': fn,
                'template_vars': template_vars
            }
            if fn_name in self._registry and self._registry[fn_name] != fn_cfg:
                raise Exception('Function %s and %s have the same name %s' % (
                        fn, self._registry[fn_name]['_fn'], fn_name))
            self._registry[fn_name] = fn_cfg
            return fn
        return wrapper

    def get_entries(self):
        def _get_entry(fn_name, fn_cfg):
            template_vars = {
                'fn_name': fn_name,
                'python_executable': sys.executable,
                'script_path': os.path.abspath(sys.argv[0])
            }
            template_vars.update(fn_cfg['template_vars'])
            # TODO: user should be able to choose whether this does safe_sub or not
            return string.Template(self._template).safe_substitute(**template_vars)

        return self._template_joiner.join([_get_entry(fn_name, fn_cfg) for fn_name, fn_cfg in self._registry.items()])

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
register = _CRONNER.register
main = _CRONNER.main
