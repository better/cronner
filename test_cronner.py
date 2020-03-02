from cronner.cronner import Cronner

import contextlib
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import unittest
import yaml


class TestCronner(unittest.TestCase):
    @contextlib.contextmanager
    def captureOutput(self, assert_stdout=None, assert_stderr=None):
        out, err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = StringIO(), StringIO()
        try:
            yield
        finally:
            sys.stdout.seek(0), sys.stderr.seek(0)
            actual_stdout, actual_stderr = sys.stdout.read(), sys.stderr.read()
            sys.stdout, sys.stderr = out, err
            if assert_stdout is not None:
                self.assertEqual(actual_stdout, assert_stdout)
            if assert_stderr is not None:
                self.assertEqual(actual_stderr, assert_stderr)

    def test_run(self):
        state = {}
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            state['a'] = 1
        cronner.run('{}.{}'.format(fn.__module__, fn.__name__))
        self.assertEqual(state, {'a': 1})

    def test_run_with_args(self):
        state = {}
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn(a, b):
            state.update(a=a, b=b)
        cronner.run('{}.{}'.format(fn.__module__, fn.__name__), 2, 3)
        self.assertEqual(state, {'a': 2, 'b': 3})

    def test_crontab_single(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            pass
        line = cronner.get_entries()
        self.assertEqual(
            line.split(),
            ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(sys.argv[0]), 'run', '{}.{}'.format(fn.__module__, fn.__name__)]
        )

    def test_crontab_multiple(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            pass
        @cronner.register('* * * * *')
        def gn():
            pass
        lines = cronner.get_entries().split('\n')
        self.assertEqual(
            sorted(line.split() for line in lines),
            sorted([
                ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(sys.argv[0]), 'run', '{}.{}'.format(fn.__module__, fn.__name__)],
                ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(sys.argv[0]), 'run', '{}.{}'.format(gn.__module__, gn.__name__)]
            ])
        )

    def test_custom_serializer(self):
        cronner = Cronner()
        cronner.configure(serializer=lambda _: 'custom_template')
        @cronner.register('* * * * *')
        def fn():
            pass
        line = cronner.get_entries()
        self.assertEqual(line, 'custom_template')

    def test_template_vars(self):
        cronner = Cronner()
        cronner.configure(serializer=lambda es: '\n'.join(e['var'] for e in es))
        @cronner.register('* * * * *', template_vars={'var': 'template_var'})
        def fn():
            pass
        line = cronner.get_entries()
        self.assertEqual(line, 'template_var')

    def test_custom_template(self):

        template = '\n'.join(['concurrencyPolicy: Allow',
        'namespace: test',
        'restartPolicy: Never',
        'image: 000000000000.dkr.ecr.us-east-1.amazonaws.com/non-existent-image',
        'labelKey: kronjob/job.test-template',
        'memoryRequest: 4096Mi',
        'memoryLimit: 6144Mi',
        'nodeSelector:',
          '  group: jobs',
        'env:',
          '  - name: ENV',
            '    value: test'
        ])
        template_yaml = yaml.load(template, Loader=yaml.FullLoader)
        cronner = Cronner()
        cronner.configure(kronjob_template=template)
        @cronner.register('* * * * *')
        def fn():
            pass
        spec = yaml.load(cronner.get_entries(), Loader=yaml.FullLoader)
        self.assertListEqual([spec[k] for k in sorted(template_yaml.keys())], [template_yaml[k] for k in sorted(template_yaml.keys())])
        self.assertEqual(spec['jobs'][0]['schedule'], '* * * * *')
        self.assertEqual(spec['jobs'][0]['name'], '{}.{}'.format(fn.__module__, fn.__name__).lower().replace('_', '-').strip('-'))
        self.assertEqual(spec['jobs'][0]['command'], [sys.executable, os.path.abspath(sys.argv[0]), 'run', '{}.{}'.format(fn.__module__, fn.__name__)])

    def test_template_vars_custom_template(self):
        template = '\n'.join(['concurrencyPolicy: Allow',
        'namespace: test',
        'restartPolicy: Never',
        'image: 000000000000.dkr.ecr.us-east-1.amazonaws.com/non-existent-image',
        'labelKey: kronjob/job.test-template',
        'memoryRequest: 4096Mi',
        'memoryLimit: 6144Mi',
        'nodeSelector:',
          '  group: jobs',
        'env:',
          '  - name: ENV',
            '    value: test'
        ])
        template_yaml = yaml.load(template, Loader=yaml.FullLoader)
        cronner = Cronner()
        cronner.configure(kronjob_template=template)
        @cronner.register('* * * * *', template_vars={'foo':'bar'})
        def fn():
            pass
        spec = yaml.load(cronner.get_entries(), Loader=yaml.FullLoader)
        self.assertEqual(spec['jobs'][0]['foo'], 'bar')

    def test_main_run(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn(*args):
            print('+'.join(args))
        with self.captureOutput(assert_stdout='a+b+c\n'):
            cronner.main(['run', '{}.{}'.format(fn.__module__, fn.__name__), '--params', 'a', 'b', 'c'])

    def test_main_gen_cfg(self):
        cronner = Cronner()
        cronner.configure(serializer=lambda es: '\n'.join('{}'.format(e['schedule']) for e in es))
        @cronner.register('* * * * *')
        def fn():
            pass
        with self.captureOutput(assert_stdout='* * * * *\n'):
            cronner.main(['gen-cfg'])

    def test_main_help(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            pass
        with self.captureOutput():
            try:
                cronner.main(['--help'])
            except SystemExit as e:
                self.assertEqual(e.code, 0)

    def test_main_unknown_input(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            pass
        with self.captureOutput():
            try:
                cronner.main(['unknown-input'])
            except SystemExit as e:
                self.assertTrue(e.code > 0)

    def test_main_no_input(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            pass
        with self.captureOutput():
            try:
                cronner.main([])
            except SystemExit as e:
                self.assertTrue(e.code > 0)

    def test_name_collision(self):
        cronner = Cronner()

        def get_f1():
            def f():
                pass
            return f

        def get_f2():
            def f():
                pass
            return f

        f1 = get_f1()
        f2 = get_f2()

        self.assertEqual(f1.__name__, f2.__name__)  # Both their names are 'f'
        self.assertNotEqual(f1, f2)  # But they are different

        cronner.register('* * * * *')(f1)  # This should be fine
        cronner.register('* * * * *')(f1)  # Can register the same function again
        # However, it should fail if we try to register another function with the same name
        self.assertRaises(Exception, lambda: cronner.register('* * * * *')(f2))
