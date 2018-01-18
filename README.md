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
