import logging
import os
import re
import time

import helper
import settings
from regexes import regexes
from datetime import datetime
from dateutil.parser import parse as dtparse
import collections

class Paste(object):

    def __init__(self):
        '''
        class Paste: Generic "Paste" object to contain attributes of a standard paste

        '''
        self.emails = 0
        self.hashes = 0
        self.num_emails = 0
        self.num_hashes = 0
        self.text = None
        self.types = []
        self.sites = None
        self.db_keywords = 0.0
        self.terms = []
        self.domains = []

        self.title = ''
        self.length = ''
        self.date = ''
        self.author = ''

    def match(self):
        '''
        Matches the paste against a series of regular expressions to determine if the paste is 'interesting'

        Sets the following attributes:
                self.emails
                self.hashes
                self.num_emails
                self.num_hashes
                self.db_keywords
                self.types

        '''
        # Get the amount of emails
        self.terms = []

        for t in settings.TERMS:
            if t.lower() in self.text.lower():
                self.terms.append(t)
                self.types.append('term-match')
                print(self.__dict__)

        self.emails = list(set(regexes['email'].findall(self.text)))
        for email in self.emails:
            domain = email.split('@')[1]
            if domain not in self.domains:
                self.domains.append(domain)
        self.hashes = regexes['hash32'].findall(self.text)
        self.num_emails = len(self.emails)
        self.num_hashes = len(self.hashes)
        if self.num_emails > 0:
            self.sites = list(set([re.search('@(.*)$', email).group(1).lower() for email in self.emails]))
        for regex in regexes['db_keywords']:
            if regex.search(self.text):
                logging.debug('\t[+] ' + regex.search(self.text).group(1))
                self.db_keywords += round(1 / float(
                    len(regexes['db_keywords'])), 2)
        for regex in regexes['blacklist']:
            if regex.search(self.text):
                logging.debug('\t[-] ' + regex.search(self.text).group(1))
                self.db_keywords -= round(1.25 * (
                        1 / float(len(regexes['db_keywords']))), 2)
        if (self.num_emails >= settings.EMAIL_THRESHOLD) or (self.num_hashes >= settings.HASH_THRESHOLD) or (
                self.db_keywords >= settings.DB_KEYWORDS_THRESHOLD):
            self.types.append('db_dump')
        if regexes['cisco_hash'].search(self.text) or regexes['cisco_pass'].search(self.text):
            self.types.append('cisco')
        if regexes['honeypot'].search(self.text):
            self.types.append('honeypot')
        if regexes['google_api'].search(self.text):
            self.types.append('google_api')
        if regexes['pgp_private'].search(self.text):
            self.types.append('pgp_private')
        if regexes['ssh_private'].search(self.text):
            self.types.append('ssh_private')
        # if regexes['juniper'].search(self.text): self.types = 'Juniper'
        for regex in regexes['banlist']:
            if regex.search(self.text):
                self.types = []
                break
        return self.types


class Site(object):
    '''
    Site - parent class used for a generic
    'Queue' structure with a fewTerms helper methods
    and features. Implements the following methods:

            empty() - Is the Queue empty
            get(): Get the next item in the queue
            put(item): Puts an item in the queue
            tail(): Shows the last item in the queue
            peek(): Shows the next item in the queue
            length(): Returns the length of the queue
            clear(): Clears the queue
            list(): Lists the contents of the Queue
            download(url): Returns the content from the URL

    '''

    # I would have used the built-in queue, but there is no support for a peek() method
    # that I could find... So, I decided to implement my own queue with a few
    # changes

    sleep = 10

    def __init__(self, queue=None):
        if queue is None:
            self.queue = []

        self.ref_id = ''
        self.sleep = 10

        self.parsed_list = collections.deque(maxlen=200)

    def empty(self):
        return len(self.queue) == 0

    def get(self):
        if not self.empty():
            result = self.queue[0]
            del self.queue[0]
        else:
            result = None
        return result

    def put(self, item):
        if item not in self.parsed_list:
            self.queue.append(item)
            self.parsed_list.append(item)
            return True

    def peek(self):
        return self.queue[0] if not self.empty() else None

    def tail(self):
        return self.queue[-1] if not self.empty() else None

    def length(self):
        return len(self.queue)

    def clear(self):
        self.queue = []

    @helper.setInterval(sleep)
    def update(self):
        raise NotImplemented

    def get_paste_text(self, paste):
        raise NotImplemented

    def list(self):
        print('\n'.join(url for url in self.queue))

    def monitor(self, r, conn):
        self.update()

        while True:
            paste = self.get()
            if paste:
                print('.')
                self.ref_id = paste.id
                logging.info('[*] Checking ' + paste.url)
                paste.text = self.get_paste_text(paste)

                tags = helper.get_tags(paste)

                if paste.types:

                    print('Inserting paste ' + paste.id)

                    d = {'external_id': paste.id, 'agent': 'paste-monitor', 'source': self.__class__.__name__,
                         'text': paste.text if not paste.terms else '@channel {}'.format(paste.text), 'type': 'paste', 'sub_type': paste.types,
                         'date': paste.date, 'url': paste.url, 'summary': '', 'terms': paste.terms,
                         'metadata': {
                            'num_emails': paste.num_emails,
                            'domains': paste.domains,
                            'num_hashes': paste.num_hashes,
                            'db_keywords': paste.db_keywords},
                         'tags': tags, 'title': paste.title, 'length': paste.length, 'author': paste.author}

                    if not r.db('khadgar').table('url').filter({'external_id': paste.id}).count().run(conn):

                        r.db('khadgar').table('url').insert(d, conflict='update').run(conn)

            time.sleep(0.01)
