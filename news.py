
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

url = 'https://news.ltn.com.tw/list/breakingnews/business'

res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

news = soup.select('ul.list > li')

with open('news.csv', mode='w', encoding='big5', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Link', 'Date'])

    for item in news:

        title_and_time = item.select_one('a.tit').text.strip()
        time_str = title_and_time.split()[0]
        title = ' '.join(title_and_time.split()[1:])

        link = item.select_one('a.tit')['href']

        hour, minute = time_str.split(':')
        time = datetime.strptime(time_str, '%H:%M')
        today = date.today()
        datetime_obj = datetime.combine(today, time.time())
        formatted_date = datetime_obj.strftime('%Y/%m/%d %H:%M')

        image_url = None
        check = item.select_one('img')
        if check is not None:
            image_url = check['data-src']

        writer.writerow([title, link, formatted_date, image_url])
