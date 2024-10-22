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
import random
import csv

# Hàm hỗ trợ để chuyển đổi thời gian sang datetime

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
chromedriver_path = 'C:/chromedriver/chromedriver.exe'
service = Service(chromedriver_path)
options = Options()
options.add_argument("--start-maximized")
a=[]
# Khởi tạo trình điều khiển Chrome với dịch vụ và tùy chọn
driver = webdriver.Chrome(service=service, options=options)

# Thiết lập chờ ngầm định
driver.implicitly_wait(10)

# Truy cập trang chủ LinkedIn
driver.get('https://www.linkedin.com')

# Thiết lập cookie 'li_at' để đăng nhập
cookie = {
    'name': 'li_at',
    'value': 'AQEDAVCQlYkFj8b4AAABkdxoW7YAAAGSAHTftk4AWYs3WCBXC0BUXRryY9OPiuWWQ2HIS9sUa3AMhwrzh4AquwtJMpy8nSoOWgWsk_GKHMb6gevYVx_G7kY117rpV818OGp95eSTcQqKLUleoXQN7tVW',  # Thay bằng giá trị cookie thực tế của bạn
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
        url = f'https://www.linkedin.com/jobs/search/?currentJobId=4035893544&f_PP=102267004%2C105790653%2C105668258&f_TPR=r604800&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={25 * (page_num - 1)}'
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
