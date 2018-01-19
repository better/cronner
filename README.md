# Easily schedule python methods to be run under cron

[![Build Status](https://travis-ci.org/liambuchanan/cronner.svg?branch=master)](https://travis-ci.org/liambuchanan/cronner)

## Writing a random integer to `/home/randint` every minute

Create the following file and name it `test.py`.

```python
import cronner
import random

@cronner.register('* * * * *')
def write_randint():
    with open('/home/randint', 'at') as f:
            f.write('{}\n'.format(random.randint(0, 100)))

cronner.main()
```

Run this.

```sh
$ python test.py crontab | crontab -
```

That's it.

## Installation

```sh
$ pip install cronner
```
