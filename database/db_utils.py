import os
import shutil
import sqlite3
import pandas as pd
import requests
from datetime import datetime
import pytz # Cần import nếu bạn dùng múi giờ cho pd.to_datetime

from config.settings import DB_URL, LOCAL_DB_FILE, BACKUP_DB_FILE, OVERWRITE_DB_ON_STARTUP

def initialize_database():
    """
    Tải xuống cơ sở dữ liệu nếu nó không tồn tại hoặc nếu OVERWRITE_DB_ON_STARTUP là True,
    và tạo một bản sao lưu.
    """
    if OVERWRITE_DB_ON_STARTUP or not os.path.exists(LOCAL_DB_FILE):
        print(f"Đang tải xuống cơ sở dữ liệu từ {DB_URL} về {LOCAL_DB_FILE}...")
        response = requests.get(DB_URL)
        response.raise_for_status()  # Đảm bảo yêu cầu thành công
        with open(LOCAL_DB_FILE, "wb") as f:
            f.write(response.content)
        print("Cơ sở dữ liệu đã được tải xuống thành công.")
        # Sao lưu - chúng ta sẽ sử dụng điều này để "reset" DB trong mỗi phần
        shutil.copy(LOCAL_DB_FILE, BACKUP_DB_FILE)
        print(f"Cơ sở dữ liệu đã được sao lưu vào {BACKUP_DB_FILE}.")
    else:
        print(f"Cơ sở dữ liệu {LOCAL_DB_FILE} đã tồn tại. Bỏ qua việc tải xuống.")

def update_dates_to_present(file_path):
    """
    Cập nhật ngày tháng trong cơ sở dữ liệu về thời gian hiện tại dựa trên tệp sao lưu.
    """
    print(f"Đang cập nhật ngày tháng trong {file_path}...")
    shutil.copy(BACKUP_DB_FILE, file_path) # Luôn sao chép từ bản sao lưu để đảm bảo trạng thái mới
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()

    # Xác định thời gian hiện tại có múi giờ nếu example_time có múi giờ
    if example_time.tz is not None:
        current_time = pd.to_datetime("now", utc=True).tz_convert(example_time.tz)
    else:
        current_time = pd.to_datetime("now") # Nếu example_time là naive, current_time cũng nên naive

    time_diff = current_time - example_time

    tdf["bookings"]["book_date"] = (
        pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True)
        + time_diff
    )

    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    for column in datetime_columns:
        tdf["flights"][column] = (
            pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    del df
    del tdf
    conn.commit()
    conn.close()
    print("Ngày tháng đã được cập nhật thành công.")
    return file_path