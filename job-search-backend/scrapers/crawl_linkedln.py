from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime, timedelta
import logging
import random
import csv

# Tạo log để kiểm tra tiến trình
logging.basicConfig(level=logging.INFO)

# Hàm chuyển đổi thời gian sang datetime
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
        print(f"Lỗi xảy ra: {e}")
        return None

def convert_to_str(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")

# Cấu hình Chrome Options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# Khởi tạo ChromeDriver Service
service = Service('/usr/local/bin/chromedriver')
logging.info("Đang khởi tạo trình duyệt...")
driver = webdriver.Chrome(service=service, options=options)

# Thiết lập chờ ngầm định
driver.implicitly_wait(10)

# Truy cập LinkedIn và thêm cookie
logging.info("Đang truy cập LinkedIn...")
driver.get('https://www.linkedin.com')
cookie = {
    'name': 'li_at',
    'value': 'AQEDAU0MA38Bs_vGAAABkt2PtfsAAAGTAZw5-04AhLQtOgID7JKGOe9VY4qSTVbrtVf5dFqDZAQlooYqSjSrgY2hLeb9S_dcxScGAApSlwLYrgW-LvHR39tVCv4vbQcRAfpOCVxEKfPyQ3UaL4ebBrWd',
    'domain': '.linkedin.com', 'path': '/', 'secure': True, 'httpOnly': True
}
driver.add_cookie(cookie)
logging.info("Sau khi đăng nhập tài khoản...")
driver.get('https://www.linkedin.com')

csv_file_path = 'jobs.csv'

# Đọc dữ liệu CSV nếu tồn tại
existing_data = set()
try:
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            existing_data.add(row['id_job'])
except FileNotFoundError:
    pass

# Mở file CSV để ghi dữ liệu mới
with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['id_job', 'job_title', 'link_post', 'location', 'date', 'about_job']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    if csv_file.tell() == 0:
        writer.writeheader()

    for page_num in range(1, 20):
        url = f'https://www.linkedin.com/jobs/search/?currentJobId=4062516658&f_PP=102267004%2C105790653%2C105668258&f_TPR=r86400&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={25 * (page_num - 1)}'
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

        # Lấy thông tin từng công việc
        for job in job_postings:
            try:
                job_id = job.get('data-job-id', None)
                if job_id in existing_data:
                    continue
            except AttributeError:
                job_id = None

            job_link = f"https://www.linkedin.com/jobs/view/{job_id}" if job_id else None
            if job_link:
                driver.get(job_link)
                time.sleep(5)
                job_soup = BeautifulSoup(driver.page_source, "html.parser")

                try:
                    job_title = job_soup.find("h1", {"class": "t-24 t-bold inline"}).text.strip()
                    job_card = job_soup.find('div', class_='job-details-jobs-unified-top-card__primary-description-container')
                    text_content = job_card.get_text(separator=' ', strip=True)
                    parts = text_content.split(' · ')
                    location = parts[0]
                    time_posted = parts[1]
                    exact_time = convert_to_datetime(time_posted)
                    date_format = convert_to_str(exact_time) if exact_time else None
                except AttributeError:
                    location, date_format = None, None

                about_job = job_soup.find('div', id='job-details')
                text_about_job = about_job.get_text(separator='\n').strip()
                text_about_job_cleaned = re.sub(r'\s+', ' ', text_about_job)
                text_about_job_cleaned = re.sub(r'\n+', '\n', text_about_job_cleaned).strip()

                new_data = {
                    "id_job": job_id,
                    "job_title": job_title,
                    "link_post": job_link,
                    "location": location,
                    "date": date_format,
                    "about_job": text_about_job_cleaned,
                }
                writer.writerow(new_data)
                existing_data.add(job_id)

print(f"Dữ liệu đã được lưu vào file CSV '{csv_file_path}'")
driver.quit()

df = pd.read_csv(csv_file_path)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
today = datetime.today()
filtered_df = df[df['date'] >= today - timedelta(days=7)]
filtered_df.to_csv('jobs.csv', index=False)
print("Đã cập nhật file 'jobs.csv' với các công việc trong vòng 7 ngày qua.")
