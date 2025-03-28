# settings.py
import os
import logging
import json

# Project root directory
CURRENT_FILE = os.path.abspath(__file__)  # Path to settings.py
SETTINGS_DIR = os.path.dirname(CURRENT_FILE)  # bin/settings
BIN_DIR = os.path.dirname(SETTINGS_DIR)  # bin
BASE_DIR = os.path.dirname(BIN_DIR)  # root directory

# Results directory
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Backup directory
BACKUP_DIR = os.path.join(RESULTS_DIR, "backup")

# Ensure directories exist
for i in [BACKUP_DIR, RESULTS_DIR]:
    if not os.path.exists(i):
        os.makedirs(i)

# Files for storing config and cookies
CONFIG_FILE = os.path.join(SETTINGS_DIR, "config.json")
COOKIES_FILE = os.path.join(SETTINGS_DIR, "cookies.json")

# Logger setup
LOG_FILE = os.path.join(SETTINGS_DIR, "logs.txt")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Functions for handling configuration
def load_config():
    default_config = {"last_id": "2226", "last_url": "https://rutracker.org/forum/viewforum.php?f=2226&start=50"}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_config

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f)

# Functions for handling cookies
def load_cookies():
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cookies(cookies):
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)

def get_database_filename(category_id):
    return f"rutrackerParser_{category_id}.sqlite"

def get_results_html_filename(category_id):
    return f"rutrackerParser_{category_id}.html"

def get_database_path(category_id):
    return os.path.join(RESULTS_DIR, get_database_filename(category_id))

def get_results_html_filepath(category_id):
    return os.path.join(RESULTS_DIR, get_results_html_filename(category_id))