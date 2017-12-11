# Gunicorn Configuration File.
# See: http://docs.gunicorn.org/en/latest/settings.html

import multiprocessing

bind = '0.0.0.0:8080'

# Send error logs to stderr
errorlog = '-'

workers = multiprocessing.cpu_count() * 2 + 1

threads = 2

# Workers silent for more than this many seconds are killed and restarted.
timeout = 90

# By preloading an application you can save some RAM resources as well as speed up server boot times.
preload_app = True
