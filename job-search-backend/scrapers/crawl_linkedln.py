from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from controller.vector_database import _qdrant
from qdrant_client.http import models

import pandas as pd
import time
import re
import logging
import random
import csv
import os

file_path = 'points.txt'

load_dotenv()

# Lấy các biến môi trường từ file .env
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_SERVER = os.getenv("QDRANT_SERVER")


    
# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


logging.info(f"Đang lọc lại tài liệu trên qdrant")

_qdrant.delete_old_points(COLLECTION_NAME)



# Hàm hỗ trợ để chuyển đổi thời gian sang datetime
def convert_to_datetime(relative_time):
    try:
        logging.info(f"Converting relative time '{relative_time}' to datetime...")
        time_pattern = r"(\d+)\s+(minutes?|hours?|days?)\s+ago"
        reposted_pattern = r"Reposted\s+(\d+)\s+(minutes?|hours?|days?)\s+ago"
        now = datetime.now()
        
        match = re.search(time_pattern, relative_time) or re.search(reposted_pattern, relative_time)
        
        if match:
            number, unit = int(match.group(1)), match.group(2)
            if 'minute' in unit:
                converted_time = now - timedelta(minutes=number)
            elif 'hour' in unit:
                converted_time = now - timedelta(hours=number)
            elif 'day' in unit:
                converted_time = now - timedelta(days=number)
            logging.info(f"Converted time: {converted_time}")
            return converted_time
        logging.warning(f"No matching time pattern found for '{relative_time}'")
        return None
    except Exception as e:
        logging.error(f"Lỗi xảy ra khi chuyển đổi thời gian: {e}")
        return None

# Hàm chuyển datetime sang string
def convert_to_str(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")

# Đường dẫn đến ChromeDriver
service = Service('/usr/local/bin/chromedriver') 

# Cấu hình Chrome Options để chạy không giao diện
options = Options()
options.add_argument("--headless")  # Chạy ở chế độ không giao diện
options.add_argument("--no-sandbox")  
options.add_argument("--disable-dev-shm-usage")  
options.add_argument("--disable-gpu")

# Khởi tạo trình duyệt
logging.info("Đang khởi tạo trình duyệt...")
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)

# Thêm cookie vào trình duyệt
logging.info("Đang thêm cookie vào trình duyệt...")

driver.get('https://www.linkedin.com')
# Thiết lập cookie 'li_at' để đăng nhập
cookie = {
    'name': 'li_at',
    'value': 'AQEDAVCQlYkB-XvGAAABku_CiZMAAAGTE88Nk1YAGCm-HAMJW8QQD0qSJspSqpvQ8XPCIA8GK-GQ2qdiYHuMwqm6h78m5419vvwus9xJ__lkD9TBeN_4cEOQV_WKo1eSyeIQDvv0fai2yZo_dKNokhiO',  # Thay bằng giá trị cookie thực tế của bạn
    'domain': '.linkedin.com',
    'path': '/',
    'secure': True,
    'httpOnly': True
}

driver.add_cookie(cookie)
# Tiếp tục truy cập trang để xác thực cookie đã được thêm
logging.info("Đang tải lại trang LinkedIn để xác thực đăng nhập...")
driver.get('https://www.linkedin.com')  


    
    # Vòng lặp qua các trang công việc
for page_num in range(1, 20):
    logging.info(f"Đang truy cập trang công việc {page_num}...")
    url = f'https://www.linkedin.com/jobs/search/?currentJobId=4062516658&f_PP=102267004%2C105790653%2C105668258&f_TPR=r86400&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={25 * (page_num - 1)}'
    driver.get(url)
    time.sleep(10)

    # Cuộn xuống cuối trang để tải thêm nội dung
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(random.uniform(2, 5))
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
        logging.info("Cuộn trang để tải thêm nội dung...")

    # Phân tích HTML bằng BeautifulSoup
    logging.info("Đang phân tích HTML để lấy thông tin công việc...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_postings = soup.find_all('div', {'class': 'job-card-container'})

    # Trích xuất thông tin từ mỗi công việc
    for job in job_postings:
        try:
            job_id = job.get('data-job-id', None)
            existing_job, _ = _qdrant.qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="id_job", match=models.MatchValue(value=job_id))]
                ),
                limit=1
            )
            if existing_job:
                logging.info(f"Job với id_job {job_id} đã tồn tại trong Qdrant.")
                continue
            else:
                job_link = f"https://www.linkedin.com/jobs/view/{job_id}"
                logging.info(f"Đang truy cập chi tiết công việc: {job_link}")
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
                    logging.info(f"Title: {job_title}, Location: {location}, Date: {date_format}")
                except AttributeError as e:
                    logging.error(f"Lỗi khi lấy thông tin chi tiết công việc: {e}")
                    continue
                try:
                    about_job = job_soup.find('div', id='job-details')
                    text_about_job = about_job.get_text(separator='\n')
                    text_about_job_cleaned = re.sub(r'\s+', ' ', text_about_job)
                    text_about_job_cleaned = re.sub(r'\n+', '\n', text_about_job_cleaned).strip()
                    logging.info(f"About job: {text_about_job_cleaned[:100]}...")  # Log ngắn gọn mô tả
                except AttributeError as e:
                    logging.error(f"Lỗi khi lấy mô tả công việc: {e}")
                    continue
                job_data = {
                    "id_job": job_id,
                    "job_title": job_title,
                    "link_post": job_link,
                    "location": location,
                    "date": date_format,
                    "about_job": text_about_job_cleaned,
                }
        except AttributeError:
            logging.error("Không tìm thấy ID công việc, bỏ qua công việc này.")
            continue
            
            
            
driver.quit()

logging.info("Đã cập nhật các công việc trong vòng 7 ngày qua.")
