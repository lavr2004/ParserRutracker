# bin/rutrackerorgCrawler.py
import requests
from bin.settings.settings import load_cookies, logger

def get_response_fc(f='2226', start='50', cookies=None):
    if cookies is None:
        cookies = load_cookies()

    if not cookies:
        logger.warning("No cookies provided. Requests may fail without authentication.")

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
        'priority': 'u=0, i',
        'referer': f'https://rutracker.org/forum/viewforum.php?f={f}',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }

    params = {
        'f': f'{f}',
        'start': f'{start}',
    }

    response = requests.get('https://rutracker.org/forum/viewforum.php', params=params, cookies=cookies, headers=headers)
    response.raise_for_status()

    logger.info(f"OK: response status code: {response.status_code}, length: {len(response.text)}")
    return response.text

if __name__ == "__main__":
    get_response_fc()