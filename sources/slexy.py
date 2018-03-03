import logging

from bs4 import BeautifulSoup

from settings import SLEEP_SLEXY
from sources.base import Paste, Site
import helper


class SlexyPaste(Paste):
    def __init__(self, id):
        self.id = id
        self.headers = {'Referer': 'http://slexy.org/view/' + self.id}
        self.url = 'http://slexy.org/raw/' + self.id
        super(SlexyPaste, self).__init__()


class Slexy(Site):
    sleep = SLEEP_SLEXY

    def __init__(self, last_id=None):
        if not last_id:
            last_id = None
        self.ref_id = last_id
        self.BASE_URL = 'http://slexy.org'
        self.sleep = SLEEP_SLEXY
        super(Slexy, self).__init__()

    @helper.setInterval(sleep)
    def update(self):
        '''update(self) - Fill Queue with new Slexy IDs'''
        logging.info('[*] Retrieving Slexy ID\'s')
        results = BeautifulSoup(helper.download(self.BASE_URL + '/recent'), 'lxml').find_all(
            lambda tag: tag.name == 'td' and tag.a and '/view/' in tag.a['href'])
        new_pastes = []
        if not self.ref_id:
            results = results[:60]
        for entry in results:
            paste = SlexyPaste(entry.a['href'].replace('/view/', ''))

            # Check to see if we found our last checked URL
            if paste.id == self.ref_id:
                break
            new_pastes.append(paste)
        for entry in new_pastes[::-1]:
            if self.put(entry):
                logging.info('[+] Adding URL: ' + entry.url)

    def get_paste_text(self, paste):
        return helper.download(paste.url, paste.headers)
