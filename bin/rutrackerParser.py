# bin/rutrackerParser.py
import sqlite3
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import os
import random
from bin.settings.settings import BASE_DIR, BACKUP_DIR, logger, load_cookies, get_database_path, get_database_filename

def convert_size_to_kb(size_str):
    match = re.match(r"(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB)", size_str, re.I)
    if match:
        size, unit = float(match.group(1)), match.group(2).upper()
        factor = {"KB": 1, "MB": 1024, "GB": 1024**2, "TB": 1024**3}
        return round(size * factor[unit], 2)
    return None

def convert_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M").date()
    except ValueError:
        return None

def setup_database(category_parameter):
    db_name = get_database_filename(category_parameter)
    db_path = get_database_path(category_parameter)

    if os.path.exists(db_path):
        backup_path = os.path.join(BACKUP_DIR, f"backup_{db_name}")
        os.replace(db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")

    logger.info(f"OK - get connection to database {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY,
        topic_id INTEGER,
        title TEXT,
        author TEXT,
        seeders INTEGER,
        leechers INTEGER,
        size_kb REAL,
        replies INTEGER,
        downloads INTEGER,
        last_post_date DATE,
        last_poster TEXT,
        torrent_link TEXT,
        parsed_url TEXT
    )
    ''')
    conn.commit()
    return conn, cursor, db_path

def parse(cursor, text, parsed_url):
    soup = BeautifulSoup(text, 'html.parser')

    for row in soup.find_all("tr", class_="hl-tr"):
        topic_id = row.get("data-topic_id")
        title_tag = row.find("a", class_="torTopic bold tt-text")
        author_tag = row.find("a", class_="topicAuthor")
        seeders_tag = row.find("span", class_="seedmed")
        leechers_tag = row.find("span", class_="leechmed")
        size_tag = row.find("a", class_="small f-dl dl-stub")
        replies_tag = row.find("td", class_="vf-col-replies tCenter small nowrap").find("span")
        downloads_tag = row.find("td", class_="vf-col-replies tCenter small nowrap").find("b")
        last_post_date_tag = row.find("td", class_="vf-col-last-post tCenter small nowrap").find("p")
        last_poster_tag = row.find("td", class_="vf-col-last-post tCenter small nowrap").find_all("a")[0]
        torrent_link_tag = row.find("a", class_="small f-dl dl-stub")

        title = title_tag.text.strip() if title_tag else None
        author = author_tag.text.strip() if author_tag else None
        seeders = int(seeders_tag.text.strip()) if seeders_tag else 0
        leechers = int(leechers_tag.text.strip()) if leechers_tag else 0
        size_kb = convert_size_to_kb(size_tag.text.strip()) if size_tag else None
        replies = int(replies_tag.text.strip().replace(',','')) if replies_tag else 0
        downloads = int(downloads_tag.text.replace(",", "").strip()) if downloads_tag else 0
        last_post_date = convert_date(last_post_date_tag.text.strip()) if last_post_date_tag else None
        last_poster = last_poster_tag.text.strip() if last_poster_tag else None
        torrent_link = "https://rutracker.org/forum/" + torrent_link_tag.get("href") if torrent_link_tag else None

        cursor.execute('''
            INSERT INTO snippets (topic_id, title, author, seeders, leechers, size_kb, replies, downloads, last_post_date, last_poster, torrent_link, parsed_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (topic_id, title, author, seeders, leechers, size_kb, replies, downloads, last_post_date, last_poster, torrent_link, parsed_url))

def extract_page_range(text):
    soup = BeautifulSoup(text, 'html.parser')
    page_links = [a['href'] for a in soup.select('p span.pg-jump-menu ~ a.pg')]
    start_values = [int(re.search(r'start=(\d+)', link).group(1)) for link in page_links if 'start=' in link]

    if not start_values:
        return [0]

    step = start_values[1] - start_values[0] if len(start_values) > 1 else 50
    max_value = max(start_values)
    return list(range(0, max_value + step, step))

def run_parser(category_parameter, progress_callback=None):
    from bin.rutrackerorgCrawler import get_response_fc

    conn, cursor, db_path = setup_database(category_parameter)
    cookies = load_cookies()  # Load cookies from file

    text = get_response_fc(f=category_parameter, start="0", cookies=cookies)
    page_range = extract_page_range(text)
    total_pages = len(page_range)

    for i, start in enumerate(page_range, 1):
        logger.info(f"Parsing page {i}/{total_pages} with start={start}")
        text = get_response_fc(f=category_parameter, start=str(start), cookies=cookies)
        parse(cursor, text, f"viewforum.php?f={category_parameter}&start={start}")
        conn.commit()
        if progress_callback and callable(progress_callback):
            progress_callback(i, total_pages)
        time.sleep(random.uniform(3, 5))

    conn.close()
    return db_path