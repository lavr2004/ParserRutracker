# bin/rutrackerHtmlGenerator.py
import sqlite3
import os
from bin.settings.settings import BASE_DIR, logger, get_database_path, get_results_html_filepath_by_database_path

def generate_html(db_path):
    #db_path = get_database_path(category_parameter)
    logger.info(f"OK - get connection to database {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(seeders) FROM snippets;")
    rows = cursor.fetchall()
    all_seeders_cumulation = rows[0][0]

    cursor.execute("SELECT SUM(downloads) FROM snippets;")
    rows = cursor.fetchall()
    all_downloads_cumulation = rows[0][0]

    cursor.execute("SELECT SUM(replies) FROM snippets;")
    rows = cursor.fetchall()
    all_commnents_cumulation = rows[0][0]

    one_comment_weight_to_downloads = int(all_downloads_cumulation / all_commnents_cumulation) + 1
    one_seeder_weight_to_downloads = int(all_downloads_cumulation / all_seeders_cumulation) + 1

    cursor.execute("SELECT * FROM snippets")
    rows = cursor.fetchall()

    #1st version of rate
    #rows = sorted(rows, key=lambda x: x[8] / (x[4] + x[7]) if (x[4] + x[7]) > 0 else 0, reverse=True)

    #2nd advanced version of rate
    downloads_count_index_int = 8
    replies_count_index_int = 7
    # rate_sort = downloads_count_index_int * replies_count_index_int
    #rows = sorted(rows, key=lambda x: x[7] * x[8] if (x[7] + x[8]) > 0 else 0, reverse=True)

    #3rd advanced version of rate
    seeders_count_index_int = 4
    leechers_count_index_int = 5
    replies_count_index_int = 7
    downloads_count_index_int = 8
    #((seeders * one_seeder_weight_to_downloads) + (leechers + downloads) + (replies * one_comment_weight_to_downloads)) * (leechers + 1)
    # (((x[4] * one_seeder_weight_to_downloads) + (x[5] + x[8]) + (x[7] * one_comment_weight_to_downloads)) * (x[5] + 1))
    def count_rate_for_record_fc(x):
        rate = ((x[4] * one_seeder_weight_to_downloads) + (x[5] + x[8]) + (x[7] * one_comment_weight_to_downloads)) * (x[5] + 1)
        return rate if rate > 0 else 0
    rows = sorted(rows, key=lambda x: count_rate_for_record_fc(x), reverse=True)

    html_filepath = get_results_html_filepath_by_database_path(db_path)

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Snippets Database</title>
    <style>
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; cursor: pointer; }
        th:hover { background-color: #ddd; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f5f5f5; }
        a { text-decoration: none; color: #0066cc; }
        a:hover { text-decoration: underline; }
        a:visited { color: #800020; }
    </style>
</head>
<body>
    <h1>Snippets Database</h1>
    <table id="snippetsTable">
        <thead>
            <tr>
                <th data-sort="0">ID</th>
                <th data-sort="1">Title</th>
                <th data-sort="2">Author</th>
                <th data-sort="3">Seeders ↓</th>
                <th data-sort="4">Leechers ↓</th>
                <th data-sort="5">Size (KB) ↓</th>
                <th data-sort="6">Replies ↓</th>
                <th data-sort="7">Downloads ↓</th>
                <th data-sort="8">Last Post Date ↓</th>
                <th data-sort="9">Last Poster</th>
                <th>Torrent Link</th>
            </tr>
        </thead>
        <tbody id="tableBody">"""

    for row in rows:
        (id, topic_id, title, author, seeders, leechers, size_kb,
         replies, downloads, last_post_date, last_poster, torrent_link, parsed_url) = row

        html_content += f"""
            <tr>
                <td>{id}</td>
                <td><a href="https://rutracker.org/forum/viewtopic.php?t={topic_id}">{title}</a></td>
                <td>{author}</td>
                <td>{seeders}</td>
                <td>{leechers}</td>
                <td>{size_kb}</td>
                <td>{replies}</td>
                <td>{downloads}</td>
                <td>{last_post_date}</td>
                <td>{last_poster}</td>
                <td><a href="{torrent_link}">Download</a></td>
            </tr>"""

    html_content += """
        </tbody>
    </table>
    <script>
        document.querySelectorAll('#snippetsTable th').forEach(header => {
            header.addEventListener('click', () => {
                const table = document.getElementById('snippetsTable');
                const tbody = document.getElementById('tableBody');
                const index = parseInt(header.getAttribute('data-sort'));
                const isDescending = !header.classList.contains('desc');
                
                if (isDescending) {
                    header.classList.add('desc');
                    header.classList.remove('asc');
                } else {
                    header.classList.add('asc');
                    header.classList.remove('desc');
                }
                
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    let aValue = a.cells[index].textContent;
                    let bValue = b.cells[index].textContent;
                    
                    if (index >= 3 && index <= 7) {
                        aValue = parseFloat(aValue) || 0;
                        bValue = parseFloat(bValue) || 0;
                        return isDescending ? bValue - aValue : aValue - bValue;
                    }
                    else if (index === 8) {
                        aValue = new Date(aValue);
                        bValue = new Date(bValue);
                        return isDescending ? bValue - aValue : aValue - bValue;
                    }
                    else {
                        return isDescending ? 
                            bValue.localeCompare(aValue) : 
                            aValue.localeCompare(bValue);
                    }
                });
                
                while (tbody.firstChild) {
                    tbody.removeChild(tbody.firstChild);
                }
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    </script>
</body>
</html>"""

    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML generated at: {html_filepath}")
    conn.close()
    os.startfile(html_filepath)