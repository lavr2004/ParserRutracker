# Rutracker Parser

A Python tool for parsing forum data from Rutracker.org, storing it in a SQLite database, and generating an HTML report. It supports both a graphical user interface (GUI) built with Tkinter and command-line execution.

## Features
- Parse forum topics from Rutracker.org by category ID or URL.
- Store parsed data in a SQLite database with automatic backups.
- Generate an HTML report with sortable tables, automatically opened in the default browser.
- GUI with fields for category ID, URL, and cookie input, featuring a progress bar with ETA.
- Asynchronous parsing to ensure the GUI remains responsive.
- Logging to both console and file (`logs.txt`).
- Cookie management via GUI (supports Python dict, JSON, or curl command input).

## Project Structure
ParserRutracker/
├── bin/
│   ├── gui.py                  # Tkinter-based GUI implementation
│   ├── rutrackerParser.py      # Parsing logic
│   ├── rutrackerHtmlGenerator.py # HTML report generation
│   ├── rutrackerorgCrawler.py  # HTTP request handler
│   └── settings/
│       └── settings.py         # Configuration and utility functions
├── main.py                     # Entry point for CLI and GUI modes
├── .gitignore
├── requirements.txt
└── README.md

## Prerequisites
- Python 3.6 or higher
- Required libraries listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/lavr2004/ParserRutracker.git
   cd ParserRutracker
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### GUI Mode
1. Run the script:
   ```bash
   python main.py
   ```
2. In the GUI:
    - Enter a category ID (e.g., `2226`) or a forum URL (e.g., `https://rutracker.org/forum/viewforum.php?f=2226&start=50`).
    - (Optional) Paste your Rutracker cookies in JSON format into the "Cookies" field.
    - Click "Start" to parse and generate HTML, or "Generate HTML" to create a report from an existing database.
3. The progress bar will show parsing progress, and the resulting HTML will open in your default browser.

### Command Line Mode
Run with a category ID:
```bash
python main.py 2226
```

## Configuration
- **Cookies**: Store your Rutracker cookies in `cookies.json` (excluded from git) or enter them in the GUI. Example format:
  ```json
  {
    "bb_guid": "your_value",
    "bb_ssl": "1",
    "bb_session": "your_session",
    "cf_clearance": "your_clearance"
  }
  ```
- **Config**: Last used values are saved in `config.json` (excluded from git).
- Example
  - ```json
     {
     "bb_guid": "T7CmkZ0udKpp",
     "bb_ssl": "1",
     "bb_session": "0-45456361-CgoiI8feFZ1gLlWtrK5J",
     "bb_t": "a:63:{i:6634755;i:1742888794;...}",
     "cf_clearance": "ZETGrnsNXIgxcweKocaU5XcjaQUXSLnVGSP6pizIq4s-1743117049-1.2.1.1-..."
     }
    ```

## Files
- `main.py`: Entry point for CLI and GUI modes.
- `gui.py`: Tkinter-based graphical interface.
- `rutrackerParser.py`: Parsing logic.
- `rutrackerorgCrawler.py`: HTTP request handler.
- `rutrackerHtmlGenerator.py`: HTML generation.
- `settings.py`: Configuration and logging setup.

## Notes
Authentication: Cookies are required for authenticated access to Rutracker.org. Keep cookies.json private.
Threading: Uses daemon threads for parsing to prevent GUI freezing and ensure proper shutdown.
Output: Generated files are named rutrackerParser_<category_id>.sqlite and rutrackerParser_<category_id>.html.