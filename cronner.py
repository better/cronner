from __future__ import print_function
import inspect
import os
import string
import sys


_CMD_TEMPLATE = '${python_executable} ${script_path} run ${method_name}'


class Cronner:
    def __init__(self):
        self._registry = {}
        self.configure()

    def __contains__(self, fn_name):
        return fn_name in self._registry

    def configure(self, cmd_template=None, **template_vars):
        self._cmd_template = cmd_template if cmd_template is not None else _CMD_TEMPLATE
        self._template_vars = dict({'python_executable': sys.executable}, **template_vars)

    def register(self, schedule, **template_vars):
        fn_cfg = {
            'schedule': schedule,
            'template_vars': template_vars
        }
        def wrapper(fn):
            fn_cfg['_fn'] = fn
            self._registry[fn.__name__] = fn_cfg
            return fn
        return wrapper

    def get_crontab_lines(self):
        # TODO: find a better proxy for script_path
        # currently takes the filename from the first stack frame that
        # doesn't have it's code defined in this file
        for frame_record in inspect.stack():
            if inspect.getmodulename(frame_record[1]) != self.__module__:
                script_path = os.path.abspath(frame_record[1])
                break

        def _get_cmd(fn_cfg):
            template_vars = dict(self._template_vars, **fn_cfg['template_vars'])
            template_vars.setdefault('script_path', script_path)
            template_vars.setdefault('method_name', fn_cfg['_fn'].__name__)
            return string.Template(self._cmd_template).safe_substitute(**template_vars)

        return [
            '{} {}'.format(fn_cfg['schedule'], _get_cmd(fn_cfg))
            for fn_cfg in self._registry.values()
        ]

    def run(self, fn_name, *args):
        self._registry[fn_name]['_fn'](*args)

    def main(self):
        if len(sys.argv) >= 2 and sys.argv[1] == 'crontab':
            print('\n'.join(self.get_crontab_lines()))
        elif len(sys.argv) >= 3 and sys.argv[1] == 'run' and sys.argv[2] in self:
            self.run(sys.argv[2], *sys.argv[3:])
        else:
            print('Unknown instruction', file=sys.stderr)
            sys.exit(1)


_CRONNER = Cronner()
configure = _CRONNER.configure
register = _CRONNER.register
main = _CRONNER.main
