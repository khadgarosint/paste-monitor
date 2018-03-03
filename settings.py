# settings.py

import os

# Thresholds
EMAIL_THRESHOLD = 20
HASH_THRESHOLD = 30
DB_KEYWORDS_THRESHOLD = .55

# Time to Sleep for each site
SLEEP_SLEXY = 60
SLEEP_PASTEBIN = 15
SLEEP_PASTIE = 30

TERMS = os.environ['TERMS'].split(',')

# Other configuration
log_file = "output.log"
