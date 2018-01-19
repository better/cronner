from setuptools import setup

setup(
    name='cronner',
    version='0.4.0',
    description='Easily schedule python methods to be run under the cron daemon.',
    py_modules=['cronner'],
    test_suite='test_cronner',
    url='https://github.com/liambuchanan/cronner',
    license='MIT',
    author='Liam Buchanan',
    author_email='liam.buchanan@gmail.com',
    keywords='cron crontab',
)
