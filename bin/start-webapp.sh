#!/bin/bash
gunicorn --conf gunicorn.conf.py arbitrage.wsgi:application
