from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import _qdrant
from qdrant_client.http import models
from langchain.schema import Document  
from qdrant_client.http.models import CollectionStatus


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

collections = _qdrant.qdrant_client.get_collections().collections

if COLLECTION_NAME not in [collection.name for collection in collections]:
    logging.info(f"Collection '{COLLECTION_NAME}' không tồn tại. Đang tạo mới...")
    _qdrant.qdrant_client.create_collection(
        COLLECTION_NAME,
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
    )
    logging.info(f"Đã tạo collection '{COLLECTION_NAME}' thành công.")
else:
    logging.info(f"Collection '{COLLECTION_NAME}' đã tồn tại.")
    
    
try:
    _qdrant.delete_old_points(COLLECTION_NAME)
except Exception as e:
    pass

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
service = Service("C:/chromedriver-win32/chromedriver.exe") 

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
    'value': 'AQEDAU0MA38BZcpPAAABkx_BK9sAAAGTcxlPTE0AlvZJvPXEj1G583YgY62VVbMn32nhBsq9MN_NtZMNNB0vSvpXGjQpO2C1bc6kwZClQkL8kuVL86W6j4tZxSZV89PMyfbObIXsd0Ew-ouarAWYWDdr',  # Thay bằng giá trị cookie thực tế của bạn
    'domain': '.linkedin.com',
    'path': '/',
    'secure': True,
    'httpOnly': True
}


docs = []
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
        try:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.uniform(2, 5))
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
            logging.info("Cuộn trang để tải thêm nội dung...")
        except Exception as e:
            logging.error(f"Lỗi khi cuộn trang: {e}")
            break

    # Phân tích HTML bằng BeautifulSoup
    logging.info("Đang phân tích HTML để lấy thông tin công việc...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_postings = soup.find_all('div', {'class': 'job-card-container'})

    # Trích xuất thông tin từ mỗi công việc
    for job in job_postings:
        try:
            job_id = job.get('data-job-id', None)
            if not job_id:
                logging.warning("Không tìm thấy ID công việc, bỏ qua.")
                continue

            # Kiểm tra công việc đã tồn tại trong Qdrant
            try:
                existing_job, _ = _qdrant.qdrant_client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="metadata.id_job", match=models.MatchValue(value=job_id))]
                    ),
                    limit=1
                )
                if existing_job:
                    logging.info(f"Job với id_job {job_id} đã tồn tại trong Qdrant.")
                    continue
            except Exception as e:
                logging.warning(f"Lỗi khi kiểm tra job {job_id} trong Qdrant: {e}")

            job_link = f"https://www.linkedin.com/jobs/view/{job_id}"
            logging.info(f"Đang truy cập chi tiết công việc: {job_link}")
            driver.get(job_link)
            time.sleep(5)

            # Lấy thông tin chi tiết công việc
            try:
                job_soup = BeautifulSoup(driver.page_source, "html.parser")
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
                logging.warning(f"Lỗi khi lấy thông tin chi tiết công việc {job_id}: {e}")
                continue

            # Lấy mô tả công việc
            try:
                about_job = job_soup.find('div', id='job-details')
                text_about_job = about_job.get_text(separator='\n')
                text_about_job_cleaned = re.sub(r'\s+', ' ', text_about_job)
                text_about_job_cleaned = re.sub(r'\n+', '\n', text_about_job_cleaned).strip()
                logging.info(f"About job: {text_about_job_cleaned[:100]}...")  # Log ngắn gọn mô tả
            except AttributeError as e:
                logging.warning(f"Lỗi khi lấy mô tả công việc {job_id}: {e}")
                continue

            # Tạo metadata và tài liệu
            metadata = {
                "id_job": job_id,
                "job_title": job_title,
                "link_post": job_link,
                "location": location,
                "date": date_format,
            }
            doc = Document(metadata=metadata, page_content=text_about_job_cleaned)
            docs.append(doc)
        except Exception as e:
            logging.error(f"Lỗi xảy ra trong quá trình xử lý công việc: {e}")
            continue

# Sắp xếp và lưu tài liệu vào Qdrant
try:
    logging.info("Đã cập nhật các công việc xong.")
except Exception as e:
    logging.error(f"Lỗi khi lưu tài liệu vào Qdrant: {e}")

driver.quit()
logging.info("Đã cập nhật các công việc xong.")
