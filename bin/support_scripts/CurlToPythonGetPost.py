import re
from urllib.parse import unquote, urlparse

# Пример использования с curl-запросом
curl_command = """
curl 'https://rutracker.org/forum/viewforum.php?f=2226&start=50' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6' \
  -b 'bb_guid=T7CmkZ0udKpp; bb_ssl=1; bb_session=0-45456361-CgoiI8feFZ1gLlWtrK5J; bb_t=a%3A63%3A%7Bi%3A6634755%3Bi%3A1742888794%3Bi%3A6651038%3Bi%3A1742967050%3Bi%3A5868196%3Bi%3A1742676228%3Bi%3A6657868%3Bi%3A1742407412%3Bi%3A6538393%3Bi%3A1742737872%3Bi%3A5669986%3Bi%3A1742893631%3Bi%3A6489372%3Bi%3A1741075968%3Bi%3A6626428%3Bi%3A1740397009%3Bi%3A6616248%3Bi%3A1740209920%3Bi%3A6572492%3Bi%3A1740186523%3Bi%3A6510525%3Bi%3A1740244598%3Bi%3A6547553%3Bi%3A1739461413%3Bi%3A6457248%3Bi%3A1738518562%3Bi%3A6640893%3Bi%3A1738687044%3Bi%3A6612408%3Bi%3A1736504235%3Bi%3A6566160%3Bi%3A1738247549%3Bi%3A6599600%3Bi%3A1737065925%3Bi%3A6509706%3Bi%3A1737030779%3Bi%3A6609550%3Bi%3A1736871374%3Bi%3A6617543%3Bi%3A1737023491%3Bi%3A6510118%3Bi%3A1736860666%3Bi%3A6398318%3Bi%3A1732958607%3Bi%3A6597580%3Bi%3A1732621265%3Bi%3A5820660%3Bi%3A1733800486%3Bi%3A6350892%3Bi%3A1732961354%3Bi%3A6016222%3Bi%3A1732798043%3Bi%3A6202717%3Bi%3A1733843974%3Bi%3A6518157%3Bi%3A1734251085%3Bi%3A6521334%3Bi%3A1734336615%3Bi%3A6536470%3Bi%3A1734358417%3Bi%3A6609014%3Bi%3A1734409472%3Bi%3A5998537%3Bi%3A1732608306%3Bi%3A6389827%3Bi%3A1731874200%3Bi%3A6599207%3Bi%3A1731655678%3Bi%3A6536949%3Bi%3A1731619394%3Bi%3A6451908%3Bi%3A1731759267%3Bi%3A6557059%3Bi%3A1730588469%3Bi%3A5477297%3Bi%3A1729588648%3Bi%3A5621542%3Bi%3A1731520549%3Bi%3A6595534%3Bi%3A1731072428%3Bi%3A6592866%3Bi%3A1730873757%3Bi%3A6085807%3Bi%3A1731527527%3Bi%3A6598626%3Bi%3A1731517732%3Bi%3A6155699%3Bi%3A1731434888%3Bi%3A6592058%3Bi%3A1731528700%3Bi%3A6590206%3Bi%3A1730054931%3Bi%3A6272305%3Bi%3A1729870843%3Bi%3A6394574%3Bi%3A1730544752%3Bi%3A6441183%3Bi%3A1731251442%3Bi%3A5951421%3Bi%3A1730563483%3Bi%3A6577847%3Bi%3A1728599014%3Bi%3A5158462%3Bi%3A1729450021%3Bi%3A6588852%3Bi%3A1729691177%3Bi%3A6588888%3Bi%3A1729777591%3Bi%3A6577670%3Bi%3A1729698237%3Bi%3A6579805%3Bi%3A1729695984%3Bi%3A6575161%3Bi%3A1729767706%3Bi%3A6505473%3Bi%3A1729695991%3Bi%3A6589351%3Bi%3A1729747643%3Bi%3A5930062%3Bi%3A1729705593%3Bi%3A6557963%3Bi%3A1728983534%3Bi%3A6555310%3Bi%3A1728577227%3Bi%3A6572658%3Bi%3A1728088494%3B%7D; cf_clearance=ZETGrnsNXIgxcweKocaU5XcjaQUXSLnVGSP6pizIq4s-1743117049-1.2.1.1-UUEjIsZPE0IwTLbkj40jVouOHB3oiL2Z7niPQXDesF91nnYaTBty47a7bgVl48.c9HCGD0qjFhMv6DQ5eIlDsh2ZjcXW3TqiI3OvhQ7E9RlhF6qPFetg1KgRe5y3zYDWS3MfuNJpXhoyB1hqfueSQuW3fwAZAdLRZqPYBX8AJtybrXVHLEOFbik_0zMStYBgwqBRNznnN3pksmy5oQFYOmwjUV5gNKQtF3CJ.B88Q1rEJ90TBrNirFbasZkd0sbx9L4alQCVQJ7hKU3kztWREUBILcOcEjKVzfR12YxK74fUsoBuQOYY1zhII.5q0oxpDuwUdrfNmlxh3e28fEgdgEx_w2OpO3eRHYRb.hKWf1g' \
  -H 'priority: u=0, i' \
  -H 'referer: https://rutracker.org/forum/viewforum.php?f=2226' \
  -H 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
"""

def parse_curl_to_python(curl_command):
    # Извлечение URL
    url_match = re.search(r"curl '([^']+)'", curl_command)
    if not url_match:
        raise ValueError("Не удалось найти URL в команде curl")
    url = url_match.group(1)

    # Извлечение имени домена для имени файла
    domain = urlparse(url).netloc.replace('.', '')
    filename = f"{domain}Crawler.py"

    # Разделение URL на базовый адрес и параметры
    if '?' in url:
        base_url, query_string = url.split('?', 1)
        params = dict(param.split('=') for param in query_string.split('&'))
    else:
        base_url = url
        params = {}

    # Инициализация заголовков, кук и данных
    headers = {}
    cookies = {}
    data = None
    method = 'GET'  # Значение по умолчанию

    # Парсинг метода (-X)
    method_match = re.search(r"-X (\w+)", curl_command)
    if method_match:
        method = method_match.group(1).upper()

    # Парсинг заголовков (-H)
    header_matches = re.findall(r"-H '([^']+)'", curl_command)
    for header in header_matches:
        key, value = header.split(': ', 1)
        headers[key.lower()] = value.strip()

    # Парсинг кук (-b)
    cookie_match = re.search(r"-b '([^']+)'", curl_command)
    if cookie_match:
        cookie_string = cookie_match.group(1)
        cookie_pairs = cookie_string.split('; ')
        for pair in cookie_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                cookies[key] = unquote(value)

    # Парсинг данных (-d)
    data_match = re.search(r"-d '([^']+)'", curl_command)
    if data_match:
        data_string = data_match.group(1)
        if '&' in data_string and '=' in data_string:
            data = dict(param.split('=') for param in data_string.split('&'))
        else:
            data = data_string
        if not method_match:
            method = 'POST'

    # Генерация Python-кода
    python_code = "import requests\n\n"

    # Формирование сигнатуры функции с параметрами
    if params:
        signature = ", ".join(f"{key} = '{value}'" for key, value in params.items())
        python_code += f"def get_response_fc({signature}):\n"
    else:
        python_code += "def get_response_fc():\n"

    # Куки
    if cookies:
        python_code += "    cookies = {\n"
        for key, value in cookies.items():
            python_code += f"        '{key}': '{value}',\n"
        python_code += "    }\n\n"
    else:
        python_code += "    cookies = {}\n\n"

    # Заголовки
    if headers:
        python_code += "    headers = {\n"
        for key, value in headers.items():
            python_code += f"        '{key}': '{value}',\n"
        python_code += "    }\n\n"
    else:
        python_code += "    headers = {}\n\n"

    # Параметры (используем переменные из сигнатуры)
    if params:
        python_code += "    params = {\n"
        for key in params.keys():
            python_code += f"        '{key}': f'{{{key}}}',\n"
        python_code += "    }\n\n"
    else:
        python_code += "    params = {}\n\n"

    # Данные (для POST)
    if data:
        if isinstance(data, dict):
            python_code += "    data = {\n"
            for key, value in data.items():
                python_code += f"        '{key}': '{value}',\n"
            python_code += "    }\n\n"
        else:
            python_code += f"    data = '{data}'\n\n"
    else:
        python_code += "    data = None\n\n"

    # Запрос
    if method == 'GET':
        python_code += f"    response = requests.get('{base_url}', params=params, cookies=cookies, headers=headers)\n"
    elif method == 'POST':
        python_code += f"    response = requests.post('{base_url}', params=params, data=data, cookies=cookies, headers=headers)\n"
    else:
        raise ValueError(f"Метод {method} не поддерживается в этом примере")

    # Дополнительные строки
    python_code += "    response.raise_for_status()\n\n"
    python_code += "    print(f\"OK: response status code: {response.status_code}\")\n"
    python_code += "    print(f\"OK: response length: {len(response.text)}\")\n\n"
    python_code += "    return response.text\n\n"
    python_code += "if __name__ == \"__main__\":\n"
    python_code += "    get_response_fc()"

    # Вывод в консоль
    print(python_code)

    # Запись в файл
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(python_code)

    return python_code, filename



# Генерируем код и записываем в файл
generated_code, filename = parse_curl_to_python(curl_command)
print(f"\nСохранено в файл: {filename}")