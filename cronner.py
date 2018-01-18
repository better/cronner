"""
Easily schedule python methods to be run under the cron daemon.

# Demo

Write a random integer to the file `/home/randint` every minute.

## Create a script

### `test.py`

```python
import cronner
import random

@cronner.register('* * * * *')
def write_randint():
    with open('/home/randint', 'at') as f:
        f.write(str(random.randint(0, 100)) + '\n')

cronner.main()
```

## Register the schedule with `crond`

```sh
$ python test.py crontab | crontab -
```
"""

from __future__ import print_function
import sys


_CONFIG_DEFAULT = {
    'lock_executable': 'flock',
    'lock_args': ['-n', '{lock_file}'],
    'python_executable': sys.executable,
    'python_args': [],
    'timeout_executable': 'timeout',
    'timeout_args': ['-t', '{timeout}'],
    'global_suffix': ''
}


class Cronner:
    def __init__(self):
        self._registry = {}
        self.configure()

    def configure(self, **kwargs):
        self._config = dict(_CONFIG_DEFAULT, **kwargs)
        return self

    def register(self, schedule, timeout=None, lock=False, suffix=None):
        def wrapper(fn):
            self._registry[fn.__name__] = (fn, schedule, timeout, lock, suffix)
            return fn
        return wrapper

    def _get_crontab_line(self, fn_name, schedule, timeout, lock, suffix):
        # TODO: simplify this or allow arbitrary user-supplied template fields
        cfg = dict(
            self._config, 
            fn_name=fn_name,
            schedule=schedule,
            timeout=timeout,
            lock=lock,
            suffix=suffix,
            lock_file='~/.{}.cronner.lock'.format(fn_name) # FIXME
        )
        items = [
            schedule,
            '{} {}'.format(
                cfg['lock_executable'], ' '.join(cfg['lock_args'])
            ) if lock else None,
            '{} {}'.format(
                cfg['timeout_executable'], ' '.join(cfg['timeout_args'])
            ) if timeout is not None else None,
            '{} {}'.format(
                cfg['python_executable'], ' '.join(cfg['python_args'])
            ),
            'run',
            fn_name,
            suffix,
            cfg['global_suffix']
        ]
        return ' '.join(
            item.format(**cfg) for item in items if item is not None
        )

    def _get_crontab(self):
        return '\n'.join(
            self._get_crontab_line(fn_name, schedule, timeout, lock, suffix)
            for fn_name, (_, schedule, timeout, lock, suffix)
            in self._registry.items()
        )

    def __contains__(self, fn_name):
        return fn_name in self._registry

    def _run(self, fn_name):
        self._registry[fn_name][0]()

    def main(self):
        if len(sys.argv) >= 2 and sys.argv[1] == 'crontab':
            print(self._get_crontab())
        elif len(sys.argv) >= 3 and sys.argv[1] == 'run' and sys.argv[2] in self:
            self._run(sys.argv[2])
        else:
            print('Unknown instruction', file=sys.stderr)
            sys.exit(1)


_CRONNER = Cronner()
configure = _CRONNER.configure
register = _CRONNER.register
main = _CRONNER.main
