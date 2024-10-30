from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime, timedelta
import logging
import random
import csv

# Khởi tạo logging để kiểm tra tiến trình
logging.basicConfig(level=logging.INFO)

# Hàm chuyển đổi thời gian từ văn bản sang datetime
def convert_to_datetime(relative_time):
    try:
        time_pattern = r"(\d+)\s+(minutes?|hours?|days?)\s+ago"
        reposted_pattern = r"Reposted\s+(\d+)\s+(minutes?|hours?|days?)\s+ago"
        now = datetime.now()

        match = re.search(time_pattern, relative_time) or re.search(reposted_pattern, relative_time)
        if match:
            number, unit = int(match.group(1)), match.group(2)
            if 'minute' in unit:
                return now - timedelta(minutes=number)
            elif 'hour' in unit:
                return now - timedelta(hours=number)
            elif 'day' in unit:
                return now - timedelta(days=number)
        return None
    except Exception as e:
        logging.error(f"Lỗi xảy ra: {e}")
        return None

def convert_to_str(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} không thể chuyển đổi")

# Cấu hình ChromeDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

service = Service('/usr/local/bin/chromedriver')

logging.info("Khởi tạo trình duyệt...")
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)

# Đăng nhập LinkedIn bằng cookie
logging.info("Truy cập LinkedIn...")
driver.get('https://www.linkedin.com')

cookie = {
    'name': 'li_at',
    'value': 'AQEDAU0MA38FL2xKAAABktibw5EAAAGS_KhHkU4Aq2VDIBsdaAprfDeBXTry7eD-9MS4ptnUQBDDluFt0PBpxx9qxGSaglNtbWFdFkbUFavqGxSPxmIC4fJQjVa7CzuTVxGiT17mMHtoPh7hK2Al0rZe',  # Thay bằng cookie thật của bạn
    'domain': '.linkedin.com',
    'path': '/',
    'secure': True,
    'httpOnly': True
}
driver.add_cookie(cookie)
driver.get('https://www.linkedin.com')

# Đọc dữ liệu từ file CSV
csv_file_path = 'jobs.csv'
existing_data = set()

try:
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        existing_data = {row['id_job'] for row in reader}
except FileNotFoundError:
    logging.warning("File CSV không tồn tại, sẽ tạo mới.")

# Mở file CSV để ghi dữ liệu mới
with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['id_job', 'job_title', 'link_post', 'location', 'date', 'about_job']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    if csv_file.tell() == 0:
        writer.writeheader()

    # Lấy dữ liệu từ nhiều trang
    for page_num in range(1, 20):
        url = f'https://www.linkedin.com/jobs/search/?currentJobId=4061299828&f_TPR=r86400&sortBy=DD?start={25 * (page_num - 1)}'
        driver.get(url)
        time.sleep(10)

        # Cuộn trang để tải thêm nội dung
        last_height = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.uniform(2, 5))
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_postings = soup.find_all('div', {'class': 'job-card-container'})

        # Duyệt qua từng bài đăng công việc
        for job in job_postings:
            job_id = job.get('data-job-id')
            if job_id in existing_data:
                continue

            job_link = f"https://www.linkedin.com/jobs/view/{job_id}"
            driver.get(job_link)
            time.sleep(5)

            job_soup = BeautifulSoup(driver.page_source, "html.parser")
            try:
                job_title = job_soup.find("h1", {"class": "t-24 t-bold inline"}).text.strip()
                location, time_posted = [
                    part.strip() for part in job_soup.find(
                        'div', class_='job-details-jobs-unified-top-card__primary-description-container'
                    ).get_text(separator=' · ').split(' · ')
                ]
                exact_time = convert_to_datetime(time_posted)
                date_format = convert_to_str(exact_time) if exact_time else None
                about_job = job_soup.find('div', id='job-details').get_text(separator='\n').strip()

                # Ghi dữ liệu mới vào CSV
                new_data = {
                    "id_job": job_id,
                    "job_title": job_title,
                    "link_post": job_link,
                    "location": location,
                    "date": date_format,
                    "about_job": about_job
                }
                writer.writerow(new_data)
                existing_data.add(job_id)
            except Exception as e:
                logging.error(f"Lỗi khi xử lý công việc: {e}")

logging.info(f"Dữ liệu đã được lưu vào '{csv_file_path}'")
driver.quit()

# Đọc và lọc dữ liệu trong 7 ngày qua
df = pd.read_csv(csv_file_path)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
filtered_df = df[df['date'] >= datetime.today() - timedelta(days=7)]
filtered_df.to_csv(csv_file_path, index=False)

print("Đã cập nhật file 'jobs.csv' với các công việc trong vòng 7 ngày qua.")
