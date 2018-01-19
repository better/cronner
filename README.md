# Easily schedule python functions to be run under cron

[![Build Status](https://travis-ci.org/liambuchanan/cronner.svg?branch=master)](https://travis-ci.org/liambuchanan/cronner)

## Make an HTTPS GET request to `google.com` every minute

Create the following file and name it `test.py`.

```python
import cronner
import random
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen

@cronner.register('* * * * *')
def write_randint():
    urlopen('https://google.com')

cronner.main()
```

Run this.

```sh
$ python test.py gen-cfg | crontab -
```

That's it.

## Installation

```sh
$ pip install cronner
```
