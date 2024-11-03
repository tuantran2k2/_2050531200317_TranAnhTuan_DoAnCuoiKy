<<<<<<< HEAD
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import pandas as pd
import time
import re
import logging
import random
import csv
# Hàm hỗ trợ để chuyển đổi thời gian sang datetime

# Tạo log để kiểm tra tiến trình
logging.basicConfig(level=logging.INFO)
def convert_to_datetime(relative_time):
    try:
      # Các đơn vị thời gian
        time_pattern = r"(\d+)\s+(minutes?|hours?|days?)\s+ago"
        reposted_pattern = r"Reposted\s+(\d+)\s+(minutes?|hours?|days?)\s+ago"
      # Lấy thời gian hiện tại
        now = datetime.now()
        # Tìm sự chênh lệch thời gian trong chuỗi
        match = re.search(time_pattern, relative_time) or re.search(reposted_pattern, relative_time)
        if match:
            number, unit = int(match.group(1)), match.group(2)
            if 'minute' in unit:
                return now - timedelta(minutes=number)
            elif 'hour' in unit:
                return now - timedelta(hours=number)
            elif 'day' in unit:
                return now - timedelta(days=number)
            else:
                return None  # Trả về None nếu không khớp với 'minute', 'hour', 'day'
        else:
            return None  # Trả về None nếu không khớp với mẫu thời gian
    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None  # Trả về None nếu có lỗi xảy ra
    
def convert_to_str(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")
# Đường dẫn đến ChromeDriver
# Cấu hình Chrome Options
options = Options()
options.add_argument("--headless")  # Chạy ở chế độ không có giao diện
options.add_argument("--no-sandbox")  # Bỏ qua sandbox (tránh lỗi quyền)
options.add_argument("--disable-dev-shm-usage")  # Giải quyết lỗi shared memory
options.add_argument("--disable-gpu")  # Vô hiệu hóa GPU nếu không cần
# Khởi tạo ChromeDriver Service
service = Service('/usr/local/bin/chromedriver') 
logging.info("Đang khởi tạo trình duyệt...")

driver = webdriver.Chrome(service=service, options=options)
# Thiết lập chờ ngầm định
driver.implicitly_wait(10)
# Truy cập trang chủ LinkedIn
logging.info("Đang truy cập LinkedIn...")

driver.get('https://www.linkedin.com')
# Thiết lập cookie 'li_at' để đăng nhập
cookie = {
    'name': 'li_at',
    'value': 'AQEDAU0MA38FL2xKAAABktibw5EAAAGS_KhHkU4Aq2VDIBsdaAprfDeBXTry7eD-9MS4ptnUQBDDluFt0PBpxx9qxGSaglNtbWFdFkbUFavqGxSPxmIC4fJQjVa7CzuTVxGiT17mMHtoPh7hK2Al0rZe',  # Thay bằng giá trị cookie thực tế của bạn
    'domain': '.linkedin.com',
    'path': '/',
    'secure': True,
    'httpOnly': True
}
csv_file_path = 'jobs.csv'
# Đọc dữ liệu CSV hiện có (nếu có) và lấy danh sách các id_job đã lưu trước đó
existing_data = set()
try:
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            existing_data.add(row['id_job'])
except FileNotFoundError:
   # Nếu file không tồn tại, tiếp tục và tạo mới file CSV sau đó
    pass
# Thêm cookie vào trình duyệt

driver.add_cookie(cookie)

logging.info("Sau khi đăng nhập tài khoản...")
# Tải lại trang để áp dụng cookie
driver.get('https://www.linkedin.com')
# Mở file CSV để ghi thêm dữ liệu mới
with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['id_job', 'job_title' ,'link_post', 'location', 'date', 'about_job']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    # Nếu file CSV trống, ghi tiêu đề vào file CSV
    if csv_file.tell() == 0:
        writer.writeheader()
    for page_num in range(1, 20):
        url = f'https://www.linkedin.com/jobs/search/?currentJobId=4062516658&f_PP=102267004%2C105790653%2C105668258&f_TPR=r86400&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={25 * (page_num - 1)}'
        driver.get(url)
        time.sleep(10)
        # Cuộn xuống cuối trang để tải thêm nội dung
        last_height = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.uniform(2, 5)) # Đợi cho trang tải
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        # Chờ trang tải và phân tích cú pháp HTML
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_postings = soup.find_all('div', {'class': 'job-card-container'})
        # Trích xuất thông tin từ mỗi công việc
        for job in job_postings:
            try:
                # Lấy giá trị id job 
                job_id = job.get('data-job-id', None)
                # Bỏ qua công việc nếu đã tồn tại trong CSV
                if job_id in existing_data:
                    continue
            except AttributeError:
                job_title = None
            try:
                # Lấy link job 
                job_link = "https://www.linkedin.com/jobs/view/" + job_id
            except (AttributeError, TypeError):
                job_link = None
            if job_link:
                driver.get(job_link)
                time.sleep(5)
                job_soup = BeautifulSoup(driver.page_source, "html.parser")
                try:
                    # Lấy tiêu đề job 
                    job_title = job_soup.find("h1", {"class": "t-24 t-bold inline"}).text.strip()
                    job_card = job_soup.find('div', class_='job-details-jobs-unified-top-card__primary-description-container')
                    text_content = job_card.get_text(separator=' ', strip=True)
                    parts = text_content.split(' · ')
                    location = parts[0]
                    time_posted = parts[1]
                    exact_time = convert_to_datetime(time_posted)
                    # Ngày đăng
                    if exact_time:
                        date_format = convert_to_str(exact_time)
                    else:
                        date_format = None
                except AttributeError:
                    location = None
                    date_format = None
                about_job = job_soup.find('div', id='job-details')
                text_about_job = about_job.get_text(separator='\n')
                # Làm sạch văn bản chỉ còn 1 dấu cách và 1 dấu xuống dòng liền nhau
                text_about_job_cleaned = re.sub(r'\s+', ' ', text_about_job)  # Thay thế nhiều khoảng trắng bằng một khoảng trắng
                text_about_job_cleaned = re.sub(r'\n+', '\n', text_about_job_cleaned)  # Thay thế nhiều \n bằng một \n
                text_about_job_cleaned = text_about_job_cleaned.strip()
                print("="*50)
                print(text_about_job_cleaned)
                print("="*50)
                # Tạo từ điển với dữ liệu mới
                new_data = {
                    "id_job": job_id,
                    "job_title" : job_title,
                    "link_post": job_link,
                    "location": location,
                    "date": date_format,
                    "about_job": text_about_job_cleaned,
                }
                # Ghi dữ liệu mới vào file CSV
                writer.writerow(new_data)

                # Thêm job_id vào tập hợp để tránh trùng lặp
                existing_data.add(job_id)
print(f"Dữ liệu đã được lưu vào file CSV '{csv_file_path}'")
driver.quit()
df = pd.read_csv(csv_file_path)
# Chuyển cột 'date' sang kiểu datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')
# Lấy ngày hiện tại
today = datetime.today()
# Lọc ra các hàng có 'date' lớn hơn hoặc bằng 7 ngày trước
filtered_df = df[df['date'] >= today - timedelta(days=7)]
# Ghi đè lại file gốc (cập nhật dữ liệu)
filtered_df.to_csv('jobs.csv', index=False)
print("Đã cập nhật file 'jobs.csv' với các công việc trong vòng 7 ngày qua.")
=======
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
    'value': 'AQEDAU0MA38Bs_vGAAABkt2PtfsAAAGTAZw5-04AhLQtOgID7JKGOe9VY4qSTVbrtVf5dFqDZAQlooYqSjSrgY2hLeb9S_dcxScGAApSlwLYrgW-LvHR39tVCv4vbQcRAfpOCVxEKfPyQ3UaL4ebBrWd',  # Thay bằng cookie thật của bạn
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
                logging.info("nội dung của : " + job_title )
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
>>>>>>> 04f8510 (push)
