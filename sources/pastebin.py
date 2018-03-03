import logging
from time import sleep

import requests
from bs4 import BeautifulSoup

import helper
from settings import SLEEP_PASTEBIN
from sources.base import Paste, Site


class PastebinPaste(Paste):
    def __init__(self, id):
        self.id = id
        self.headers = None
        self.scraping_url = 'https://pastebin.com/api_scrape_item.php?i=' + self.id
        self.url = 'http://pastebin.com/raw.php?i=' + self.id
        super(PastebinPaste, self).__init__()


class Pastebin(Site):

    sleep = SLEEP_PASTEBIN

    def __init__(self, last_id=None):
        if not last_id:
            last_id = None
        self.ref_id = last_id
        self.BASE_URL = 'http://pastebin.com'
        self.sleep = SLEEP_PASTEBIN
        self.session = requests.Session()
        super(Pastebin, self).__init__()

    @helper.setInterval(sleep)
    def update(self):
        '''update(self) - Fill Queue with new Pastebin IDs'''
        logging.info('Retrieving Pastebin ID\'s')
        new_pastes = []

        r = self.session.get('https://pastebin.com/api_scraping.php')

        results = r.json()

        for entry in results:
            paste = PastebinPaste(entry['key'])
            paste.title = entry['title']
            paste.length = entry['size']
            paste.date = entry['date']
            paste.author = entry['user']
            # Check to see if we found our last checked URL
            if paste.id == self.ref_id:
                break
            new_pastes.append(paste)

        for entry in new_pastes[::-1]:
            if self.put(entry):
                logging.info('Adding URL: ' + entry.url)

    def get_paste_text(self, paste):
        return helper.download(paste.scraping_url)
