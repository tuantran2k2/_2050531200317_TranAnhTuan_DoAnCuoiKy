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
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None

def convert_to_str(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")


csv_file_path = 'jobs.csv'
existing_data = set()
try:
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            existing_data.add(row['id_job'])
except FileNotFoundError:
    pass

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Bật trình duyệt có giao diện (headless=False)
    page = browser.new_page()

    # Đăng nhập LinkedIn bằng cookie 'li_at'
    page.goto('https://www.linkedin.com')
    page.context.add_cookies([{
        'name': 'li_at',
        'value': 'AQEDAVCQlYkAtNdoAAABkthqBQMAAAGS_HaJA04AtE-Nirk91X6NNCQLNM-TPNIm_cZ3bmIArxxczng3zx4DupGoZQzKu8LnAK4oFz0jiX-2rzWlEC6B6YrGEGy8A8s5vDvWBLvN7cTPaLp3T4X-NAtq',
        'domain': '.linkedin.com',
        'path': '/',
        'secure': True,
        'httpOnly': True
    }])

    page.goto('https://www.linkedin.com/jobs/search/')
    time.sleep(5)

    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['id_job', 'job_title', 'link_post', 'location', 'date', 'about_job']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if csv_file.tell() == 0:
            writer.writeheader()

        for page_num in range(1, 20):
            url = f'https://www.linkedin.com/jobs/search/?currentJobId=4035893544&f_PP=102267004%2C105790653%2C105668258&f_TPR=r604800&geoId=104195383&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={25 * (page_num - 1)}'
            page.goto(url)
            time.sleep(5)

            # Scroll để tải thêm nội dung
            for i in range(3):  # Cuộn trang 3 lần
                page.mouse.wheel(0, 1000)
                time.sleep(random.uniform(2, 5))

            # Lấy source page và parse bằng BeautifulSoup
            soup = BeautifulSoup(page.content(), 'html.parser')
            job_postings = soup.find_all('div', {'class': 'job-card-container'})

            for job in job_postings:
                try:
                    job_id = job.get('data-job-id', None)
                    if job_id in existing_data:
                        continue
                except AttributeError:
                    job_id = None

                job_link = f"https://www.linkedin.com/jobs/view/{job_id}" if job_id else None

                if job_link:
                    page.goto(job_link)
                    time.sleep(5)
                    job_soup = BeautifulSoup(page.content(), 'html.parser')
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
                        job_title, location, date_format = None, None, None

                    about_job = job_soup.find('div', id='job-details')
                    text_about_job = about_job.get_text(separator='\n') if about_job else ""
                    text_about_job_cleaned = re.sub(r'\s+', ' ', text_about_job).strip()

                    print("="*50)
                    print(text_about_job_cleaned)
                    print("="*50)

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

    browser.close()

# Đọc và lọc dữ liệu công việc trong vòng 7 ngày
df = pd.read_csv(csv_file_path)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
today = datetime.today()
filtered_df = df[df['date'] >= today - timedelta(days=7)]
filtered_df.to_csv('jobs.csv', index=False)

print("Đã cập nhật file 'jobs.csv' với các công việc trong vòng 7 ngày qua.")
