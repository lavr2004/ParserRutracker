import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
import os
import threading
import json
import time
import sys
from bin.rutrackerParser import run_parser
from bin.rutrackerHtmlGenerator import generate_html
from bin.settings.settings import BASE_DIR, logger, load_config, save_config, load_cookies, save_cookies

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Rutracker Parser")
        self.root.geometry("500x500")

        # Флаг для отслеживания закрытия приложения
        self.is_closing = False
        # Ссылка на поток парсинга
        self.parsing_thread = None

        # Загрузка последних значений
        self.config = load_config()
        self.default_id = "2226"
        self.default_url = "https://rutracker.org/forum/viewforum.php?f=2226&start=50"
        self.results_dir = os.path.join(BASE_DIR, "results")

        # Frame для ID
        self.id_frame = tk.Frame(root)
        self.id_frame.pack(pady=5)
        self.id_label = tk.Label(self.id_frame, text="Category ID:")
        self.id_label.pack(side=tk.LEFT, padx=5)
        self.id_entry = tk.Entry(self.id_frame, width=20)
        self.id_entry.insert(0, self.config.get("last_id", self.default_id))
        self.id_entry.config(foreground='black')
        self.id_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.id_entry, self.default_id))
        self.id_entry.pack(side=tk.LEFT, padx=5)
        self.id_clear = tk.Button(self.id_frame, text="Clear", command=lambda: self.clear_field(self.id_entry))
        self.id_clear.pack(side=tk.LEFT, padx=5)

        # Frame для URL
        self.url_frame = tk.Frame(root)
        self.url_frame.pack(pady=5)
        self.url_label = tk.Label(self.url_frame, text="Forum URL:")
        self.url_label.pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(self.url_frame, width=50)
        self.url_entry.insert(0, self.config.get("last_url", self.default_url))
        self.url_entry.config(foreground='black')
        self.url_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.url_entry, self.default_url))
        self.url_entry.pack(side=tk.LEFT, padx=5)
        self.url_clear = tk.Button(self.url_frame, text="Clear", command=lambda: self.clear_field(self.url_entry))
        self.url_clear.pack(side=tk.LEFT, padx=5)

        # Кнопки
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_parsing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.generate_button = tk.Button(self.button_frame, text="Generate HTML", command=self.generate_html_only)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        self.set_cookies_button = tk.Button(self.button_frame, text="Set Cookies", command=self.open_cookies_window)
        self.set_cookies_button.pack(side=tk.LEFT, padx=5)
        self.set_cookies_curl_button = tk.Button(self.button_frame, text="Set Cookies via curl", command=self.open_curl_window)
        self.set_cookies_curl_button.pack(side=tk.LEFT, padx=5)
        self.delete_db_button = tk.Button(self.button_frame, text="Delete Database", command=self.delete_selected_database)
        self.delete_db_button.pack(side=tk.LEFT, padx=5)

        # Прогресс-бар
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Метка для информации о прогрессе
        self.progress_info = tk.Label(root, text="Progress: 0/0 requests, ETA: N/A")
        self.progress_info.pack(pady=5)

        # Поле для сообщений
        self.message_label = tk.Label(root, text="", foreground="red")
        self.message_label.pack(pady=5)

        # Список баз данных
        self.db_frame = tk.Frame(root)
        self.db_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        tk.Label(self.db_frame, text="Available Databases:").pack()
        self.db_listbox = tk.Listbox(self.db_frame, height=10)
        self.db_listbox.pack(fill=tk.BOTH, expand=True)
        self.update_db_list()

        # Переменные для расчета времени
        self.start_time = None
        self.total_pages = 0

        # Сохранение конфига при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground='grey')

    def clear_field(self, entry):
        entry.delete(0, tk.END)
        entry.config(foreground='black')

    def extract_category_from_url(self, url):
        match = re.search(r'f=(\d+)', url)
        return match.group(1) if match else None

    def get_category_id(self):
        category_id = self.id_entry.get().strip() if self.id_entry.cget('foreground') != 'grey' else ""
        url = self.url_entry.get().strip() if self.url_entry.cget('foreground') != 'grey' else ""
        if not category_id and url:
            category_id = self.extract_category_from_url(url)
        return category_id

    def update_db_list(self):
        if self.is_closing:
            return
        self.db_listbox.delete(0, tk.END)
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        for file in os.listdir(self.results_dir):
            if file.endswith('.sqlite'):
                self.db_listbox.insert(tk.END, file)

    def delete_selected_database(self):
        if self.is_closing:
            return
        selected = self.db_listbox.curselection()
        if not selected:
            self.message_label.config(text="Please select a database to delete")
            logger.warning("No database selected for deletion")
            return

        db_name = self.db_listbox.get(selected[0])
        db_path = os.path.join(self.results_dir, db_name)

        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Deleted database: {db_path}")
            self.message_label.config(text=f"Deleted {db_name}")
            self.update_db_list()
        else:
            self.message_label.config(text="Database file not found")
            logger.error(f"Database file not found: {db_path}")

    def open_cookies_window(self):
        if self.is_closing:
            return
        self.cookies_window = tk.Toplevel(self.root)
        self.cookies_window.title("Set Cookies")
        self.cookies_window.geometry("600x400")

        tk.Label(self.cookies_window, text="Paste your cookies below (Python dict or JSON format):").pack(pady=5)
        cookies_text = scrolledtext.ScrolledText(self.cookies_window, width=70, height=20)
        cookies_text.pack(pady=5)

        example_cookies = """{
    'bb_guid': 'T7CmkZ0udKpp',
    'bb_ssl': '1',
    'bb_session': '0-45456361-CgoiI8feFZ1gLlWtrK5J',
    'bb_t': 'a:63:{i:6634755;i:1742888794;...}',
    'cf_clearance': 'ZETGrnsNXIgxcweKocaU5XcjaQUXSLnVGSP6pizIq4s-1743117049-1.2.1.1-...'
}"""
        cookies_text.insert(tk.END, example_cookies)
        cookies_text.config(foreground='grey')

        def save_cookies_from_input():
            if self.is_closing:
                return
            text = cookies_text.get("1.0", tk.END).strip()
            try:
                cookies = eval(text, {"__builtins__": {}}, {}) if text else {}
                if not isinstance(cookies, dict):
                    raise ValueError("Not a dictionary")
            except Exception:
                try:
                    cookies = json.loads(text)
                except json.JSONDecodeError:
                    self.message_label.config(text="Invalid cookies format")
                    logger.error("Invalid cookies format provided")
                    return

            save_cookies(cookies)
            self.message_label.config(text="Cookies saved successfully")
            logger.info("Cookies saved successfully")
            self.cookies_window.destroy()

        tk.Button(self.cookies_window, text="Save", command=save_cookies_from_input).pack(pady=5)

    def open_curl_window(self):
        if self.is_closing:
            return
        self.curl_window = tk.Toplevel(self.root)
        self.curl_window.title("Set Cookies via curl")
        self.curl_window.geometry("600x400")

        tk.Label(self.curl_window, text="Paste your curl command below:").pack(pady=5)
        curl_text = scrolledtext.ScrolledText(self.curl_window, width=70, height=20)
        curl_text.pack(pady=5)

        example_curl = """curl 'https://rutracker.org/forum/viewforum.php?f=2226' \
  -H 'Cookie: bb_guid=T7CmkZ0udKpp; bb_ssl=1; bb_session=0-45456361-CgoiI8feFZ1gLlWtrK5J; bb_t=a:63:{i:6634755;i:1742888794;...}; cf_clearance=ZETGrnsNXIgxcweKocaU5XcjaQUXSLnVGSP6pizIq4s-1743117049-1.2.1.1-...'"""
        curl_text.insert(tk.END, example_curl)
        curl_text.config(foreground='grey')

        def save_cookies_from_curl():
            if self.is_closing:
                return
            text = curl_text.get("1.0", tk.END).strip()
            cookies = self.parse_cookies_from_curl(text)
            if cookies:
                save_cookies(cookies)
                self.message_label.config(text="Cookies parsed and saved successfully")
                logger.info("Cookies parsed from curl and saved")
                self.curl_window.destroy()
            else:
                self.message_label.config(text="Could not parse cookies from curl")
                logger.error("Failed to parse cookies from curl command")

        tk.Button(self.curl_window, text="Save", command=save_cookies_from_curl).pack(pady=5)

    def parse_cookies_from_curl(self, curl_text):
        cookies = {}
        cookie_match = re.search(r"-H 'Cookie: (.*?)'", curl_text)
        if cookie_match:
            cookie_str = cookie_match.group(1)
            pairs = cookie_str.split('; ')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    cookies[key.strip()] = value.strip()
        return cookies

    def start_parsing(self):
        if self.is_closing:
            return
        category_id = self.get_category_id()
        if not category_id:
            self.message_label.config(text="Please provide a category ID or valid URL")
            logger.error("No category ID provided or could not extract from URL")
            return

        cookies = load_cookies()
        if not cookies:
            self.message_label.config(text="No cookies set. Please set cookies first.")
            logger.warning("No cookies available for parsing")
            return

        self.message_label.config(text="")
        self.start_button.config(state='disabled')
        logger.info(f"Starting parsing for category: {category_id}")

        self.start_time = time.time()
        self.parsing_thread = threading.Thread(target=self.run_parsing_thread, args=(category_id, cookies), daemon=True)
        self.parsing_thread.start()

    def run_parsing_thread(self, category_id, cookies):
        db_path = run_parser(category_id, self.update_progress)
        if db_path and not self.is_closing:
            logger.info("Parsing completed, ready to generate HTML")
            self.config["last_id"] = category_id
            self.config["last_url"] = self.url_entry.get()
            self.root.after(0, self.enable_start_button)
            self.root.after(0, self.reset_progress_info)
            self.root.after(0, self.update_db_list)

    def generate_html_only(self):
        if self.is_closing:
            return
        selected = self.db_listbox.curselection()
        if not selected:
            self.message_label.config(text="Please select a database or run parsing first")
            logger.warning("No database selected for HTML generation")
            return

        db_name = self.db_listbox.get(selected[0])
        db_path = os.path.join(self.results_dir, db_name)

        if not os.path.exists(db_path):
            self.message_label.config(text="Selected database not found")
            logger.error(f"Database {db_path} not found")
            return

        self.message_label.config(text="")
        logger.info(f"Generating HTML for database: {db_path}")
        generate_html(db_path)
        logger.info("HTML generation completed")

    def update_progress(self, current, total):
        if self.is_closing:
            return
        self.total_pages = total
        percentage = (current / total) * 100
        self.root.after(0, self.set_progress, percentage, current, total)

    def set_progress(self, percentage, current, total):
        self.progress['value'] = percentage

        if self.start_time and current > 0:
            elapsed_time = time.time() - self.start_time
            time_per_request = elapsed_time / current
            remaining_requests = total - current
            remaining_time = time_per_request * remaining_requests
            eta = f"{int(remaining_time // 60)}m {int(remaining_time % 60)}s"
        else:
            eta = "N/A"

        self.progress_info.config(text=f"Progress: {current}/{total} requests, ETA: {eta}")

    def reset_progress_info(self):
        self.progress['value'] = 0
        self.progress_info.config(text="Progress: 0/0 requests, ETA: N/A")
        self.start_time = None

    def enable_start_button(self):
        self.start_button.config(state='normal')

    def on_closing(self):
        if self.is_closing:
            return
        self.is_closing = True
        logger.info("Closing application")

        # Сохранение конфигурации
        self.config["last_id"] = self.id_entry.get() if self.id_entry.cget('foreground') != 'grey' else self.default_id
        self.config["last_url"] = self.url_entry.get() if self.url_entry.cget('foreground') != 'grey' else self.default_url
        save_config(self.config)

        # Закрытие всех дочерних окон
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.destroy()

        # Уничтожение главного окна и завершение программы
        self.root.destroy()
        if self.parsing_thread and self.parsing_thread.is_alive():
            logger.warning("Parsing thread still active, forcing shutdown")
        sys.exit(0)

root = tk.Tk()
app = App(root)
root.mainloop()