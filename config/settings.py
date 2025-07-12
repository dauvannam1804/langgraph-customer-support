import os

# Đường dẫn và URL của cơ sở dữ liệu
DB_URL = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
LOCAL_DB_FILE = "travel2.sqlite"
BACKUP_DB_FILE = "travel2.backup.sqlite"

# Đặt True để buộc tải lại và ghi đè cơ sở dữ liệu khi khởi động ứng dụng
OVERWRITE_DB_ON_STARTUP = False