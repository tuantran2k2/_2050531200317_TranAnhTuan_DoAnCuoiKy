from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import time
import re
import logging
import random
import csv
import json

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Đọc cookie từ file JSON
logging.info("Đang đọc cookie từ file 'cookies.json'...")
with open("cookies.json", "r") as file:
    cookies = json.load(file)

# Thêm cookie vào trình duyệt
logging.info("Đang đọc cookie từ file 'cookies.json'...")
with open("cookies.json", "r") as file:
    cookies = json.load(file)

# Thêm cookie vào trình duyệt
logging.info("Đang thêm cookie vào trình duyệt...")
driver.get('https://www.linkedin.com')  # Mở trang LinkedIn để cài cookie

for cookie in cookies:
    # Kiểm tra miền của cookie
    if cookie.get('domain') == '.linkedin.com':
        if 'sameSite' in cookie:
            del cookie['sameSite']  # Xóa thuộc tính sameSite nếu không hợp lệ
        logging.info(f"Adding cookie: {cookie}")
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            logging.error(f"Không thể thêm cookie {cookie['name']}: {e}")
    else:
        logging.warning(f"Bỏ qua cookie {cookie['name']} do không khớp miền: {cookie['domain']}")

# Tiếp tục truy cập trang để xác thực cookie đã được thêm
logging.info("Đang tải lại trang LinkedIn để xác thực đăng nhập...")
driver.get('https://www.linkedin.com')  

# Đọc dữ liệu CSV hiện có và lấy danh sách các id_job đã lưu trước đó
csv_file_path = 'jobs.csv'
existing_data = set()
logging.info(f"Đang kiểm tra và đọc dữ liệu từ file '{csv_file_path}' nếu có...")
try:
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            existing_data.add(row['id_job'])
    logging.info(f"Đã đọc {len(existing_data)} công việc từ file CSV hiện có.")
except FileNotFoundError:
    logging.warning(f"File '{csv_file_path}' không tồn tại, sẽ tạo file mới.")

# Mở file CSV để ghi thêm dữ liệu mới
with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['id_job', 'job_title' ,'link_post', 'location', 'date', 'about_job']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if csv_file.tell() == 0:
        writer.writeheader()
    
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
                if job_id in existing_data:
                    logging.info(f"Bỏ qua công việc {job_id} (đã tồn tại).")
                    continue
            except AttributeError:
                logging.error("Không tìm thấy ID công việc, bỏ qua công việc này.")
                continue
            
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

            # Tạo từ điển với dữ liệu mới
            new_data = {
                "id_job": job_id,
                "job_title": job_title,
                "link_post": job_link,
                "location": location,
                "date": date_format,
                "about_job": text_about_job_cleaned,
            }
            
            # Ghi dữ liệu mới vào file CSV
            try:
                writer.writerow(new_data)
                existing_data.add(job_id)
                logging.info(f"Đã lưu công việc {job_id} vào file CSV.")
            except Exception as e:
                logging.error(f"Lỗi khi ghi dữ liệu vào CSV: {e}")
                continue

logging.info(f"Dữ liệu đã được lưu vào file CSV '{csv_file_path}'")
driver.quit()

# Đọc và lọc dữ liệu trong vòng 7 ngày
logging.info("Đang đọc và lọc dữ liệu công việc trong vòng 7 ngày qua...")
df = pd.read_csv(csv_file_path)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
today = datetime.today()
filtered_df = df[df['date'] >= today - timedelta(days=7)]
filtered_df.to_csv('jobs.csv', index=False)

logging.info("Đã cập nhật file 'jobs.csv' với các công việc trong vòng 7 ngày qua.")
