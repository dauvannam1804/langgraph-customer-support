import os
import shutil
import sqlite3

import pandas as pd
import requests

# Lấy đường dẫn thư mục hiện tại chứa file Python
script_dir = os.path.dirname(os.path.abspath(__file__))

db_url = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
local_file = os.path.join(script_dir, "travel2.sqlite")
backup_file = os.path.join(script_dir, "travel2.backup.sqlite")
overwrite = False

if overwrite or not os.path.exists(local_file):
    response = requests.get(db_url)
    response.raise_for_status()
    with open(local_file, "wb") as f:
        f.write(response.content)
    shutil.copy(local_file, backup_file)
    