from setuptools import setup

setup(
    name='cronner',
    version='0.7.6',
    description='Easily schedule python functions to be run under the cron daemon.',
    packages=['cronner'],
    test_suite='test_cronner',
    url='https://github.com/better/cronner',
    license='MIT',
    author='Liam Buchanan',
    author_email='liam@better.com',
    keywords='cron crontab',
    tests_require=['pyyaml'],
    extras_require={
        'kronner': ['pyyaml']
    }
)
