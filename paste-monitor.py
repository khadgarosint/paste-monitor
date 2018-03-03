# dumpmon.py
# Author: Jordan Wright
# Version: 0.0 (in dev)

# ---------------------------------------------------
# To Do:
#
#	- Refine Regex
#	- Create/Keep track of statistics

import logging
import os
import threading
from time import sleep

import rethinkdb as r

from sources.pastebin import Pastebin
from sources.pastie import Pastie
from sources.slexy import Slexy


def monitor():
    '''
    monitor() - Main function... creates and starts threads

    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="more verbose", action="store_true")
    args = parser.parse_args()
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s', level=level)
    logging.info('Monitoring...')

    # Create lock for both output log and tweet action
    log_lock = threading.Lock()

    conn = r.connect(os.environ.get('RETHINK_HOST', 'localhost'), int(os.environ.get('RETHINK_PORT', 28015))).repl()

    pastebin_thread = threading.Thread(
        target=Pastebin().monitor, args=[r, conn])
    slexy_thread = threading.Thread(
        target=Slexy().monitor, args=[r, conn])
    pastie_thread = threading.Thread(
        target=Pastie().monitor, args=[r, conn])

    for thread in (pastebin_thread, slexy_thread, pastie_thread):
        thread.daemon = True
        thread.start()

    # Let threads run
    try:
        while True:
            sleep(5)
    except KeyboardInterrupt:
        logging.warn('Stopped.')


if __name__ == "__main__":
    monitor()
