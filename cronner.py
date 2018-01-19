from __future__ import print_function
import inspect
import os
import string
import sys


_DEFAULT_TEMPLATE = '${schedule} ${python_executable} ${script_path} run ${method_name}'
_DEFAULT_TEMPLATE_JOINER = '\n'

# Demonstration only
_K8S_TEMPLATE = '''apiVersion: batch/v2alpha1
kind: CronJob
metadata:
  name: cronner-${method_name}
spec:
  schedule: "${schedule}"
  jobTemplate:
    spec:
      template:
        spec:
          nodeSelector:
            nodepurpose: cronner
          restartPolicy: Never
          containers:
          - name: job-runner
            image: alpine:3.6
            command: ["${python_executable}", "${script_path}", "run", "${method_name}"]'''


class Cronner:
    def __init__(self):
        self._registry = {}
        self.configure()

    def __contains__(self, fn_name):
        return fn_name in self._registry

    def configure(self, template=_DEFAULT_TEMPLATE, template_joiner=_DEFAULT_TEMPLATE_JOINER):
        self._template = template
        self._template_joiner = template_joiner

    def register(self, schedule, template_vars=None):
        if template_vars is not None:
            template_vars = dict(template_vars, schedule=schedule)
        else:
            template_vars =  {'schedule': schedule}
        def wrapper(fn):
            fn_cfg = {
                '_fn': fn,
                'template_vars': template_vars
            }
            self._registry[fn.__name__] = fn_cfg
            return fn
        return wrapper

    def get_entries(self):
        # TODO: find a better proxy for script_path
        # currently takes the filename from the first stack frame that
        # doesn't have it's code defined in this file
        for frame_record in inspect.stack():
            if inspect.getmodulename(frame_record[1]) != self.__module__:
                script_path = os.path.abspath(frame_record[1])
                break

        def _get_entry(fn_cfg):
            template_vars = {
                'method_name': fn_cfg['_fn'].__name__,
                'python_executable': sys.executable,
                'script_path': script_path
            }
            template_vars.update(fn_cfg['template_vars'])
            return string.Template(self._template).safe_substitute(**template_vars)

        return [_get_entry(fn_cfg) for fn_cfg in self._registry.values()]

    def run(self, fn_name, *args):
        self._registry[fn_name]['_fn'](*args)

    def main(self):
        if len(sys.argv) >= 2 and sys.argv[1] == 'gen-cfg':
            print(self._template_joiner.join(self.get_entries()))
        elif len(sys.argv) >= 3 and sys.argv[1] == 'run' and sys.argv[2] in self:
            self.run(sys.argv[2], *sys.argv[3:])
        else:
            print('Unknown instruction', file=sys.stderr)
            sys.exit(1)


_CRONNER = Cronner()
configure = _CRONNER.configure
register = _CRONNER.register
main = _CRONNER.main
