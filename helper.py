'''
helper.py - provides misc. helper functions
Author: Jordan

'''

import logging
import threading
from time import sleep

import requests

import settings

r = requests.Session()


def download(url, headers=None):
    if not headers:
        headers = None
    if headers:
        r.headers.update(headers)
    try:
        response = r.get(url).text
    except requests.ConnectionError:
        logging.warn('[!] Critical Error - Cannot connect to site')
        sleep(5)
        logging.warn('[!] Retrying...')
        response = download(url)
    return response


def log(text):
    '''
    log(text): Logs message to both STDOUT and to .output_log file

    '''
    print(text)
    with open(settings.log_file, 'a') as logfile:
        logfile.write(text + '\n')


def get_tags(paste):
    '''
    build_tweet(url, paste) - Determines if the paste is interesting and, if so, builds and returns the tweet accordingly

    '''
    tags = []
    if paste.match():
        if 'google_api' in paste.types:
            tags.append('Found possible Google API key(s)')
        elif 'cisco' in paste.types or 'juniper' in paste.types:
            tags.append('Possible router configuration')
        elif 'ssh_private' in paste.types:
            tags.append('Possible SSH private key')
        elif 'honeypot' in paste.types:
            tags.append('Dionaea Honeypot Log')
        elif 'pgp_private' in paste.types:
            tags.append('Found possible PGP Private Key')
    return tags


def setInterval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):  # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped

        return wrapper

    return decorator
