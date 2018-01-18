from setuptools import setup

setup(
    name='cronner',
    version='0.1.1',
    description='Easily schedule python methods to be run under the cron daemon.',
    py_modules=['cronner'],
    url='https://github.com/liambuchanan/cronner',
    author='Liam Buchanan',
    author_email='liam.buchanan@gmail.com',
    license='MIT',
    keywords='cron crontab',
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4'
)
