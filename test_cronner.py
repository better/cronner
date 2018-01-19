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
        line = cronner.get_crontab_lines()[0]
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
        lines = cronner.get_crontab_lines()
        self.assertEqual(
            sorted(line.split() for line in lines),
            sorted([
                ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(__file__), 'run', 'fn'],
                ['*', '*', '*', '*', '*', sys.executable, os.path.abspath(__file__), 'run', 'gn']
            ])
        )
