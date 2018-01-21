from cronner import Cronner

import os
import sys
import unittest


class TestCronner(unittest.TestCase):
    def test_run(self):
        state = {}
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            state['a'] = 1
        cronner.run('fn')
        self.assertEqual(state, {'a': 1})

    def test_run_with_args(self):
        state = {}
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn(a, b):
            state.update(a=a, b=b)
        cronner.run('fn', 2, 3)
        self.assertEqual(state, {'a': 2, 'b': 3})

    def test_crontab_single(self):
        cronner = Cronner()
        @cronner.register('* * * * *')
        def fn():
            pass
        line = cronner.get_entries()
        self.assertEqual(
            line.split(),
            ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(__file__), 'run', 'fn']
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
                ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(__file__), 'run', 'fn'],
                ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(__file__), 'run', 'gn']
            ])
        )

    def test_custom_template(self):
        cronner = Cronner()
        cronner.configure(template='custom_template')
        @cronner.register('* * * * *')
        def fn():
            pass
        line = cronner.get_entries()
        self.assertEqual(line, 'custom_template')

    def test_custom_template_and_joiner(self):
        cronner = Cronner()
        cronner.configure(template='custom_template', template_joiner='+')
        @cronner.register('* * * * *')
        def fn():
            pass
        @cronner.register('* * * * *')
        def gn():
            pass
        line = cronner.get_entries()
        self.assertEqual(line, 'custom_template+custom_template')

    def test_template_vars(self):
        cronner = Cronner()
        cronner.configure(template='$var')
        @cronner.register('* * * * *', template_vars={'var': 'template_var'})
        def fn():
            pass
        line = cronner.get_entries()
        self.assertEqual(line, 'template_var')
