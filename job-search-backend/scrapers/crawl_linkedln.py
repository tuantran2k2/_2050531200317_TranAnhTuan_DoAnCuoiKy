from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import _qdrant
from qdrant_client.http import models
from langchain.schema import Document  
from models.Jobs import Job
from dependencies.dependencies import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

import pandas as pd
import time
import re
import logging
import random
import csv
import os
# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
# Lấy các biến môi trường từ file .env
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


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


def check_id_job(id_job ,db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id_job == id_job).first()
    return job


def save_job_to_db(job, db: Session = Depends(get_db)):
    db.add(job)
    db.commit()
    db.refresh(job)
    return job.id_job


def crawl_linkedin_jobs(time_range="r86400" ,db: Session = None):
    # kiểm tra xem collection đã tồn tại hay chưa
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
    ##################################################################################

       
    # Xóa các điểm có "date" quá 7 ngày   
    try:
        logging.info("Đang vào kiểm tra điểm có 'date' quá 7 ngày...")
        _qdrant.delete_old_points(COLLECTION_NAME)
    except Exception as e:
        logging.info("không có điểm nào có 'date' quá 7 ngày")
        pass
    ###############################################

    if db is None:
        db = next(get_db())  # Tạo session nếu không được truyền vào
        
    # Đường dẫn đến ChromeDriver
    service = Service("C:/chromedriver/chromedriver.exe") 

    # Cấu hình Chrome Options để chạy không giao diện
    options = Options()
    options.add_argument("--headless")  # Chạy ở chế độ không giao diện
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--use-gl=swiftshader")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-gpu")  # Tắt GPU hoàn toàn nếu không cần
    options.add_argument("--disable-webgl")  # Tắt WebGL nếu không cần thiết

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
        'value': '',  # Thay bằng giá trị cookie thực tế của bạn
        'domain': '.linkedin.com',
        'path': '/',
        'secure': True,
        'httpOnly': True
    }
    driver.add_cookie(cookie)
    # Tiếp tục truy cập trang để xác thực cookie đã được thêm
    logging.info("Đang tải lại trang LinkedIn để xác thực đăng nhập...")
    driver.get('https://www.linkedin.com')  
    url_ex = f'https://www.linkedin.com/jobs/search/?f_PP=102267004%2C105790653%2C105668258&f_TPR={time_range}&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD'
    logging.info(f"Đang truy cập trang công việc: {url_ex}")
        # Vòng lặp qua các trang công việc
    for page_num in range(1, 100):
        logging.info(f"Đang truy cập trang công việc {page_num}...")
        url = f'https://www.linkedin.com/jobs/search/?f_PP=102267004%2C105790653%2C105668258&f_TPR={time_range}&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={25 * (page_num - 1)}'
        driver.get(url)
        time.sleep(10)
        # Cuộn xuống cuối trang để tải thêm nội dung
        # Khởi tạo giá trị ban đầu
        last_height = driver.execute_script('return document.body.scrollHeight')
        scroll_limit = 5  # Số lần cuộn tối đa khi không có nội dung mới
        extra_scrolls = 0  # Đếm số lần cuộn thêm

        while True:
            try:
                # Cuộn xuống cuối trang
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.uniform(2, 5))  # Chờ để tải thêm nội dung

                # Lấy chiều cao mới của trang
                new_height = driver.execute_script('return document.body.scrollHeight')

                if new_height == last_height:
                    # Nếu không có nội dung mới, tăng bộ đếm
                    extra_scrolls += 1
                    if extra_scrolls >= scroll_limit:
                        logging.info("Đã cuộn thêm đủ số lần và không có nội dung mới. Dừng cuộn.")
                        break
                else:
                    # Nếu có nội dung mới, đặt lại bộ đếm
                    last_height = new_height
                    extra_scrolls = 0

                logging.info("Cuộn trang để tải thêm nội dung...")
            except Exception as e:
                logging.error(f"Lỗi khi cuộn trang: {e}")
                break

                # Phân tích HTML bằng BeautifulSoup
        logging.info("Đang phân tích HTML để lấy thông tin công việc...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_postings = soup.find_all('div', {'data-job-id': True})
        print(len(job_postings))
        
        # Dừng vòng lặp nếu không tìm thấy công việc nào
        if not job_postings:
            logging.info(f"Không tìm thấy công việc nào ở trang {page_num}. Dừng crawl.")
            break

        # Trích xuất thông tin từ mỗi công việc
        for job in job_postings:
            try:
                job_id = job.get('data-job-id', None)
                if not job_id:
                    logging.warning("Không tìm thấy ID công việc, bỏ qua.")
                    continue
                job_db = check_id_job(job_id, db)
                logging.info(f"Kiểm tra công việc {job_id} trong database: {job_db}")
                if job_db != None:
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
                    print("===============================================start=====================================================")
                    print(about_job)
                    print("=================================================end===================================================")
                    text_about_job = about_job.get_text(separator='\n')
                    text_about_job_cleaned = re.sub(r'\s+', ' ', text_about_job)
                    text_about_job_cleaned = re.sub(r'\n+', '\n', text_about_job_cleaned).strip()
                    logging.info(f"About job: {text_about_job_cleaned[:100]}...")  # Log ngắn gọn mô tả
                except AttributeError as e:
                    logging.info(f"Lỗi khi lấy mô tả công việc {job_id}: {e}")
                    continue
                
                job_new = Job(id_job=job_id , job_title=job_title, link_post=job_link, location=location, date_post=date_format)
                job_save_id = save_job_to_db(job_new, db)
                logging.info(f"Đã lưu công việc vào database với id {job_save_id}")
                # Tạo metadata và tài liệu
                metadata = {
                    "id_job": job_id,
                    "job_title": job_title,
                    "link_post": job_link,
                    "location": location,
                    "date": date_format,
                }
                docs = []
                doc = Document(metadata=metadata, page_content=text_about_job_cleaned)
                docs.append(doc)
                _qdrant.save_vector_db(docs,COLLECTION_NAME)
            except Exception as e:
                logging.error(f"Lỗi xảy ra trong quá trình xử lý công việc: {e}")
                continue
    driver.quit()
    logging.info("Đã crawl dữ liệu xong")



